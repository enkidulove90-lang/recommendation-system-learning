"""
Publish SSR paper with PDF attachment, HD images, and 5 topic tags.
Full pipeline: PDF upload → image uploads → topic search → note creation.
"""
import json, os, sys
sys.path.insert(0, r'c:\Users\xu.yan1\AppData\Roaming\Python\Python311\site-packages')
from xhs_cli.commands._common import get_cookies
from xhs_cli.client import XhsClient
from xhs_cli.constants import CREATOR_HOST

PDF = r'c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\SSR_paper.pdf'
IMG_DIR = r'c:\Users\xu.yan1\papers\recommendation-system-learning\data\parsed\2604.08011\images_hd'
IMAGES = ['model.jpg', 'ICS_2x2_mechanism.jpg', 'layer_sparsity_compare.png', 'pub_scaling_page1.png']

TITLE = "SIGIR26｜SSR显式稀疏推荐框架"
# Post body optimized for 4-image layout:
#   Fig1: model.jpg      → SSR Filter-then-Fuse 架构总览
#   Fig2: ICS_2x2        → ICS迭代竞争稀疏四阶段 (a→b→c→d)
#   Fig3: layer_sparsity  → 稀疏度逐层加深 Layer1(75%)→Layer2(90%)
#   Fig4: pub_scaling     → Scaling实验: SSR vs Dense MLP
BODY ="""🎓 推荐系统做大模型Scaling，加更多参数反而性能饱和甚至下降？阿里国际SIGIR2026论文SSR发现：92%的连接权重被压到接近零，80%能量集中在4%维度——dense架构根本不匹配推荐场景的稀疏特性。

SSR提出显式稀疏框架：Filter-then-Fuse，把被动权重压缩变成主动信号筛选。

✨ 核心亮点
• SSR-S(静态随机过滤)：固定二值选择矩阵，零额外推理成本。56%参数44%FLOPs超越RankMixer
• SSR-D(迭代竞争稀疏ICS)：可微分动态稀疏，点击AUC+0.46pt，支付AUC+0.72pt
• 在线A/B：CTR+2.1%，订单+3.2%，GMV+3.5%，延迟仅+1ms
• Avazu上SSR-S仅用51%参数就超越所有基线

🧠 方法：Filter-then-Fuse
1. 多视图稀疏过滤——输入分解为并行视图，每视图维度级稀疏筛选
2. 密集融合——过滤后视图独立通过块对角变换，拼接输出
3. ICS迭代竞争稀疏——受生物种群竞争启发的可微分机制，多轮迭代产生真正零值

📊 Scaling实验关键发现
dense MLP参数增大后性能早饱和，SSR随参数规模(~900M)持续提升——稀疏架构更高效利用大参数量。

💡 可探索方向
方向一：SSR+MoE——SSR特征维度稀疏，MoE样本维度稀疏，正交可组合
方向二：通用预处理——SSR的Filter-then-Fuse可作为任意推荐骨干前置模块
方向三：端侧部署——SSR-S静态稀疏可直接编译为内存访问模式，适合移动端

📄 arXiv：https://arxiv.org/abs/2604.08011
💻 GitHub：https://github.com/Atticus666/SSRNet
🏫 阿里国际(AliExpress) · SIGIR2026 Full Paper"""

TOPICS_KEYWORDS = ["推荐系统", "SIGIR", "论文分享", "AI", "阿里"]


def main():
    # Use cookies directly from file (bypass browser extraction)
    import json as _json
    from pathlib import Path as _Path
    cf = _Path.home() / '.xiaohongshu-cli' / 'cookies.json'
    if cf.exists():
        cookies = _json.loads(cf.read_text())
        print(f"Using saved cookies: a1={cookies.get('a1','')[:20]}...")
    else:
        _, cookies = get_cookies('auto')
    client = XhsClient(cookies)

    with client:
        # Step 1: Get doc_id and upload PDF
        print("[1/5] Uploading PDF...")
        doc = client._creator_post('/api/galaxy/v2/creator/doc/gen_id', {})
        doc_id = str(doc['id'])

        permit = client._creator_get('/api/media/v1/upload/creator/permit', {
            'biz_name': 'sns', 'scene': 'web_doc',
            'file_count': 1, 'version': 1, 'source': 'web',
        })
        p = permit['uploadTempPermits'][0]
        with open(PDF, 'rb') as f:
            pdf_data = f.read()
        pdf_url = f"https://{p['uploadAddr']}/{p['fileIds'][0]}"
        r = client._request_with_retry('PUT', pdf_url, headers={
            'X-Cos-Security-Token': p['token'], 'Content-Type': 'application/pdf',
        }, content=pdf_data)
        print(f"  PDF: {r.status_code} ({len(pdf_data):,} bytes)")

        # Step 2: Upload images
        print("[2/5] Uploading images...")
        image_fids = []
        for img_name in IMAGES:
            img_path = os.path.join(IMG_DIR, img_name)
            ip = client._creator_get('/api/media/v1/upload/creator/permit', {
                'biz_name': 'spectrum', 'scene': 'image',
                'file_count': 1, 'version': 1, 'source': 'web',
            })
            ipp = ip['uploadTempPermits'][0]
            with open(img_path, 'rb') as f:
                img_data = f.read()
            img_url = f"https://{ipp['uploadAddr']}/{ipp['fileIds'][0]}"
            r = client._request_with_retry('PUT', img_url, headers={
                'X-Cos-Security-Token': ipp['token'], 'Content-Type': 'image/jpeg',
            }, content=img_data)
            image_fids.append(ipp['fileIds'][0])
            print(f"  {img_name}: {r.status_code} ({len(img_data):,} bytes)")

        # Step 3: Search topics for real IDs
        print("[3/5] Searching topics...")
        topic_payloads = []
        for t in TOPICS_KEYWORDS:
            data = client.search_topics(t)
            items = data.get('topic_info_dtos', [])
            if items:
                best = items[0]
                topic_payloads.append({
                    'id': best.get('id', ''), 'name': best.get('name', t), 'type': 'topic',
                })
                print(f"  {t}: id={best.get('id', '?')}")
            else:
                topic_payloads.append({'id': '', 'name': t, 'type': 'topic'})
                print(f"  {t}: NOT FOUND, using fallback")

        # Step 4: Create note
        print("[4/5] Creating note...")
        images_payload = [{'file_id': fid, 'metadata': {'source': -1}} for fid in image_fids]
        business_binds = json.dumps({
            'version': 1, 'noteId': 0, 'noteOrderBind': {},
            'notePostTiming': {'postTime': None}, 'noteCollectionBind': {'id': ''},
        })

        payload = {
            'common': {
                'type': 'normal', 'title': TITLE, 'note_id': '',
                'desc': BODY,
                'source': '{"type":"web","ids":"","extraInfo":"{\\"subType\\":\\"official\\"}"}',
                'business_binds': business_binds,
                'ats': [], 'hash_tag': topic_payloads, 'post_loc': {},
                'privacy_info': {'op_type': 1, 'type': 0},
            },
            'image_info': {'images': images_payload},
            'video_info': None,
            'related_file': {'doc_id': doc_id, 'name': 'SSR_paper.pdf'},
        }

        result = client._main_api_post('/web_api/sns/v2/note', payload, {
            'origin': CREATOR_HOST, 'referer': f'{CREATOR_HOST}/',
        })

        note_id = result.get('data', {}).get('id', result.get('id', ''))
        if note_id:
            print(f"\n[5/5] PUBLISHED!")
            print(f"  Note ID: {note_id}")
            print(f"  URL: https://www.xiaohongshu.com/explore/{note_id}")
            print(f"  PDF: attached (doc_id={doc_id})")
            print(f"  Images: {len(image_fids)}")
            print(f"  Topics: {len(topic_payloads)}")
        else:
            print(f"\n[5/5] FAILED: {json.dumps(result, ensure_ascii=False)[:500]}")


if __name__ == '__main__':
    main()
