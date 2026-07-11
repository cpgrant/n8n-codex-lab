# Backup and Recovery

## Important warning

Do not casually run:

```bash
docker compose down -v
```

The `-v` option can delete the persistent n8n data volume.

## Workflow backups

Export important workflows from n8n and save the JSON files in:

```text
workflows/
```

## Files to preserve

Keep backups of:

- `docker-compose.yml`
- `Dockerfile`
- `AGENTS.md`
- exported workflow JSON files
- repository documentation

## MCP token recovery

If an MCP token is exposed:

1. Open n8n.
2. Go to **Settings → Instance-level MCP**.
3. Open **Connection details**.
4. Regenerate the access token.
5. Export the replacement token in Terminal.
6. Restart VS Code or Codex from that Terminal session.

## Find the Docker volume

```bash
docker volume ls | grep n8n
```

The volume is likely named:

```text
n8n_n8n_data
```

Verify the exact name before backing up or restoring.

## Create a data-volume backup

```bash
mkdir -p ~/Backups/n8n

docker run --rm \
  -v n8n_n8n_data:/data \
  -v "$HOME/Backups/n8n:/backup" \
  alpine \
  tar czf "/backup/n8n-data-$(date +%Y-%m-%d-%H%M).tar.gz" -C /data .
```

Verify:

```bash
ls -lh ~/Backups/n8n
```

## Restore a backup

Stop n8n:

```bash
cd ~/Development/docker/n8n
docker compose down
```

Restore the selected archive:

```bash
docker run --rm \
  -v n8n_n8n_data:/data \
  -v "$HOME/Backups/n8n:/backup" \
  alpine \
  sh -c 'rm -rf /data/* && tar xzf /backup/REPLACE-WITH-BACKUP-FILENAME.tar.gz -C /data'
```

Restart:

```bash
docker compose up -d
```

## Recover after a failed image update

If the previous custom image still exists:

```bash
cd ~/Development/docker/n8n
docker compose up -d --no-build
```

Verify:

```bash
docker compose ps
docker exec -it n8n n8n --version
docker exec -it n8n ffmpeg -version
```
