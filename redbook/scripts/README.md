# Legacy scripts

`redbook/scripts/` is retained only for historical recovery, one-off migrations,
and backwards-compatible launchers. It is not the application architecture.

All new production behavior belongs to:

```text
redbook/domain/          stable workflow and media contracts
redbook/application/     resumable state-machine use cases
redbook/services/        figure retrieval, quality gates, composition rules
redbook/infrastructure/  ModelScope/Qwen, MinerU, OpenCLI adapters
redbook/cli.py           supported command-line entry point
```

The supported figure preparation command is:

```powershell
python -m redbook.cli prepare-figures \
  --paper-id 2606.24597 \
  --arxiv-id 2606.24597 \
  --markdown data/parsed/2606.24597_qwen_agentworld/2606.24597.md \
  --images data/parsed/2606.24597_qwen_agentworld/images \
  --pdf data/papers/2606.24597_Qwen-AgentWorld.pdf \
  --layout data/parsed/2606.24597_qwen_agentworld/2606.24597_layout.json \
  --vision
```

Figure acquisition has a fixed quality order:

1. `--arxiv-id` downloads the arXiv e-print source and keeps author supplied
   assets from `pics/`, `figures/`, `fig/`, `images/` and `img/`. Embedded PDF
   vectors in that source are rendered at 4x. TikZ is detected and recorded;
   if the source does not include a rendered vector artifact, it falls through
   to the PDF path instead of silently producing a blurry screenshot.
2. MinerU layout regions are rerendered from the original PDF at 288 DPI, with
   PDF page number, figure ID and caption saved in `figure_manifest.json`.
3. Legacy MinerU image files are only used when neither source nor PDF inputs
   are available.

`--vision` is an explicit, optional human-quality gate. It uses the configured
ModelScope Qwen model to score readability and role relevance after the local
pixel/aspect/legibility gate; it never upscales a low-resolution source.

## Persona-driven copy drafts

Paper-sharing personas are configuration, not another publish script. List and
compose a draft through the supported CLI; neither command publishes anything:

```powershell
python -m redbook.cli list-personas
python -m redbook.cli compose-post \
  --summary data/summaries/2606.24597_summary.md \
  --arxiv-id 2606.24597 \
  --persona industry_analyst \
  --github https://github.com/QwenLM/Qwen-Agent \
  --output data/workflow_state/2606.24597/industry_analyst_draft.json
```

Persona definitions live in `redbook/personas/`; evidence and design choices
are recorded in `redbook/docs/research/2026-07-paper-sharing-personas.md`.
