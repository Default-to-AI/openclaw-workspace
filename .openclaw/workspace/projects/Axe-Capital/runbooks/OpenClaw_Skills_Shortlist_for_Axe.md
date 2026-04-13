# OpenClaw skills shortlist (Axe Capital ops + investing)

## Must-have for research and synthesis
### youtube-search
- **Use**: find relevant YouTube sources (interviews, PM talks, risk, IC process).
- **Requirement**: `yt-dlp` must be installed and on PATH. (Currently missing on this machine.)

### notebooklm
- **Use**: create a notebook per theme (IC process, risk, playbooks), ingest web/YouTube sources, then generate memos/templates.
- **Install**: `pip install notebooklm-py` then `notebooklm skill install`
- **Auth**: `notebooklm login`
- **Parallel-safety**: use explicit notebook IDs (`-n/--notebook`), avoid `notebooklm use` across agents.

### yt-research-pipeline
- **Use**: end-to-end YouTube discovery → NotebookLM notebook → analysis/synthesis.
- **Dependency**: relies on both youtube-search (yt-dlp) and notebooklm (auth).

## Must-have for execution and ops hygiene
### taskflow + taskflow-inbox-triage
- **Use**: daily/weekly pipeline, triage incoming tasks into queues, enforce cadence.

### session-logs
- **Use**: audit trail of actions, decisions, outputs (useful for “decision log”).

### gh-issues / github
- **Use**: if you run code or data tooling (research pipelines, dashboards), manage backlog in GitHub.

## Useful for content + evidence capture
### summarize
- **Use**: compress long docs into consistent briefings.

### nano-pdf
- **Use**: quickly ingest and summarize PDFs (DDQs, broker docs, research reports).

### openai-whisper / openai-whisper-api
- **Use**: transcribe calls/meetings to feed into NotebookLM and decision logs.

### obsidian / notion
- **Use**: persist “vault artifacts” and link TOM/RACI/cadence/playbooks.

## Notes / blockers
- YouTube-based sourcing is **blocked** until `yt-dlp` is installed.
- NotebookLM workflows are **blocked** until `notebooklm login` is completed in this environment.
