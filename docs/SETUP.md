# SETUP

## Startup
```bash
cd ~/Development/docker/n8n
docker compose up -d
docker compose ps
docker exec -it n8n n8n --version
docker exec -it n8n ffmpeg -version
```

Start project:
```bash
cd ~/Development/codex/n8n-codex-lab
code .
export N8N_MCP_TOKEN='YOUR_TOKEN'
codex mcp list
```
