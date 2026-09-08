import os
import world
import utils
from world import cprint
import torch
import numpy as np
import pickle as pkl
from tensorboardX import SummaryWriter
import time
import Procedure
from os.path import join
# ==============================
utils.set_seed(world.seed)
print(">>SEED:", world.seed)
# ==============================
import register
from register import dataset




if not os.path.exists('logs'):
    os.mkdir('logs')
    
if not os.path.exists('embs'):
    os.mkdir('embs')

config = f'{world.args.dataset}_seed{world.args.seed}_{world.args.model}_dim{world.args.recdim}_lr{world.args.lr}_dec{world.args.decay}_alpha{world.args.alpha}_beta{world.args.beta}_gamma{world.args.gamma}'

if world.args.model == 'lgn':
    config += f'_nl{world.args.layer}'

# P0: make config name reflect CL settings so cached embs don't collide
if world.args.use_cl:
    config += f'_cl{world.args.cl_reg}_G{world.args.G}_ct{world.args.cl_temp}_ca{world.args.cl_alpha}'

# idea2: reflect MM-alignment settings in config name
if world.args.use_mm:
    config += f'_mm_mr{world.args.mm_reg}_mt{world.args.mm_temp}'
    # idea3: reflect cost-aware weight so idea2 vs idea2+cost don't collide
    if world.args.cost_reg and world.args.cost_reg > 0:
        config += f'_cr{world.args.cost_reg}'
        if world.args.cost_target and world.args.cost_target > 0:
            config += f'_ct{world.args.cost_target}'
    # E1: force_c 冻结融合 — 不同 force_c 视为不同实验, 避免互相覆盖 + 与 run_idea2.config_name 对齐
    if world.args.force_c and world.args.force_c > 0:
        config += f'_fc{world.args.force_c:.6g}'
    # E2 修复: 此前只有 run_idea2.config_name() 加了 _mcr 后缀, 这里漏了 ->
    # E2(--mm_conf_reg 0) 的 test 行被 append 进 v3 默认 idea2_mm 的 txt(新旧混杂),
    # 而 run_idea2 去找 *_mcr0.txt 必然落空. 两侧命名必须严格对齐.
    if world.args.mm_conf_reg != 0.01:
        config += f'_mcr{world.args.mm_conf_reg:.6g}'
    # E6: 全局预算约束 — target / lambda / dual-eta 全进名字, 不同档互不覆盖.
    # eta 必须进名字: 否则 soft(eta=0) 与增广拉格朗日(eta>0) 在同一 (t,lambda) 下会撞同一 txt.
    if (world.args.mm_budget and world.args.mm_budget > 0
            and (world.args.mm_budget_lambda > 0 or world.args.mm_budget_dual > 0)):
        config += f'_mb{world.args.mm_budget:.6g}l{world.args.mm_budget_lambda:.6g}'
        if world.args.mm_budget_dual and world.args.mm_budget_dual > 0:
            config += f'd{world.args.mm_budget_dual:.6g}'
    # eval 前刷新投影缓存 = 另一种评测口径, 必须进名字, 否则与旧口径结果混写同一 txt.
    if getattr(world.args, 'mm_eval_fresh', 0):
        config += '_ef1'
    _pr = int(getattr(world.args, 'mm_proj_refresh', 0) or 0)
    if _pr:
        config += f'_pr{_pr}'

log_path = f'logs/{config}.txt'
emb_path = f'embs/{config}.pkl'

# P0: removed the three silent `exit(0)` short-circuits (layer==4, decay grid, emb cache hit).
#     emb cache now only skips when --force is NOT set, so repeated runs are explicit.
if os.path.exists(emb_path) and not world.args.force:
    print('Exists. (use --force to overwrite)')
    exit(0)

Recmodel = register.MODELS[world.model_name](world.config, dataset)
Recmodel = Recmodel.to(world.device)
bpr = utils.BPRLoss(Recmodel, world.config)

weight_file = utils.getFileName()
print(f"load and save to {weight_file}")
if world.LOAD:
    try:
        Recmodel.load_state_dict(torch.load(weight_file, map_location=torch.device('cpu')))
        world.cprint(f"loaded model weights from {weight_file}")
    except FileNotFoundError:
        print(f"{weight_file} not exists, start from beginning")
Neg_k = 1

# init tensorboard
if world.tensorboard:
    w : SummaryWriter = SummaryWriter(join(world.BOARD_PATH, time.strftime("%m-%d-%Hh%Mm%Ss-") + "-" + world.comment))
else:
    w = None
    world.cprint("not enable tensorflowboard")

try:
    best_valid = -1
    patience = 0
    
    for epoch in range(world.TRAIN_epochs):
        start = time.time()
        Recmodel.mm_new_epoch()
        
        output_information = Procedure.BPR_train_original(dataset, Recmodel, bpr, epoch, neg_k=Neg_k,w=w)
        print(f'EPOCH[{epoch+1}/{world.TRAIN_epochs}] {output_information}')
        
        if (epoch + 1) % 5 == 0:
            if getattr(Recmodel, 'use_mm', 0):
                # conf_std / min / max: E6 的关键判据之一 —— 全局预算应把均值顶住(mean>=0.6)
                # 的同时**保留物品间分化**(std 明显 >0). 若 std->0 说明退化成了 force_c.
                print(f"[idea2] conf_mean={Recmodel.mm_info.get('conf_mean',0):.3f} "
                      f"conf_std={Recmodel.mm_info.get('conf_std',0):.3f} "
                      f"conf_range=[{Recmodel.mm_info.get('conf_min',0):.3f},"
                      f"{Recmodel.mm_info.get('conf_max',0):.3f}] "
                      f"gate={Recmodel.mm_info.get('gate_mean',{})}"
                      + (f" batch_c={getattr(Recmodel,'_mm_batch_c_mean',0):.3f}"
                         f" budget_loss={getattr(Recmodel,'_mm_budget_loss',0):.4f}"
                         if getattr(Recmodel, 'mm_budget_lambda', 0) > 0 else ""))
                # conf_mean 上面那个来自 epoch 级缓存投影(滞后整整一个 epoch 的 Adam step),
                # 而 E6 预算约束作用在新鲜投影上 -> 两者可能天差地别(实测 0.184 vs 0.825).
                # 这里额外报一份**新鲜全量投影**下的 c, 作为判据的真值口径。
                # 只读诊断, 不改 eval 融合路径, 故不影响与 E1/E2 历史数值的可比性。
                try:
                    _fr = Recmodel.mm_aligner.diag_fresh_conf(
                        Recmodel.mm_feats, Recmodel.embedding_item.weight)
                    if _fr:
                        print(f"[idea2] FRESH conf_mean={_fr['fresh_mean']:.3f} "
                              f"conf_std={_fr['fresh_std']:.3f} "
                              f"conf_range=[{_fr['fresh_min']:.3f},{_fr['fresh_max']:.3f}]"
                              f"  (cached={Recmodel.mm_info.get('conf_mean',0):.3f}"
                              f" -> 缓存滞后量 {_fr['fresh_mean']-Recmodel.mm_info.get('conf_mean',0):+.3f})")
                except Exception as _e:
                    print(f"[idea2] FRESH conf 诊断失败(不影响训练): {_e}")
                # ⚠️ mm_eval_fresh 已证伪, 默认必须为 0。
                # 曾以为"eval 前刷新投影"能对齐口径, 实测反而让 R@20 从 0.0697 崩到 0.0578
                # (valid 同步崩、loss 反升): 模型是在 c≈0.06 的图传播下训练出来的,
                # eval 却切到 c≈0.83 的前向 -> 训练/评测错配。
                # 真正的解法是让训练时图传播的 c 就受预算约束, 而不是事后换投影。
                # 保留开关仅供对照实验, 正式跑请勿开启。
                if world.config.get('mm_eval_fresh', 0):
                    Recmodel.mm_aligner.refresh_proj(Recmodel.mm_feats)
            cprint("[VALIDATION]")
            valid_results = Procedure.Valid(dataset, Recmodel, epoch, w, world.config['multicore'])
            valid_log = [valid_results['ndcg'][0], valid_results['ndcg'][1], valid_results['recall'][0], valid_results['recall'][1], valid_results['precision'][0], valid_results['precision'][1]]
            
            cprint("[TEST]")
            test_results = Procedure.Test(dataset, Recmodel, epoch, w, world.config['multicore'])
            test_log = [test_results['ndcg'][0], test_results['ndcg'][1], test_results['recall'][0], test_results['recall'][1], test_results['precision'][0], test_results['precision'][1]]
            
            with open(log_path, 'a') as f:
                f.write(f'valid ' + ' '.join([str(x) for x in valid_log]) + '\n')
                f.write(f'test ' + ' '.join([str(x) for x in test_log]) + '\n')
            
            if valid_results['ndcg'][0] > best_valid:
                best_valid = valid_results['ndcg'][0]
                patience = 0
                
                Recmodel.eval()
                all_users, all_items, _all_users, _all_items = Recmodel.computer()
                all_users, all_items = all_users.detach().cpu(), all_items.detach().cpu()
                _all_users, _all_items = _all_users.detach().cpu(), _all_items.detach().cpu()

                with open(emb_path, 'wb') as f:
                    if world.args.save_layer_emb:
                        pkl.dump([all_users, all_items, _all_users, _all_items], f)
                    else:
                        pkl.dump([all_users, all_items], f)
            else:
                patience += 1

        if patience == 10:
            print('Early Stopping')
            
            with open(log_path, 'a') as f:
                f.write('Early Stopping\n')
                
            exit(0)
finally:
    if world.tensorboard:
        w.close()