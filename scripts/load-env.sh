#!/usr/bin/env bash

# Sourced by repository startup scripts. Never print secret values.

load_repository_env() {
  local repository_root="$1"
  local env_file="$repository_root/.env"
  local line name index
  local -a existing_names=()
  local -a existing_values=()

  if [[ ! -f "$env_file" ]]; then
    echo "Missing $env_file. Copy .env.example to .env and configure it." >&2
    return 2
  fi

  # Preserve explicit process-environment overrides while loading defaults
  # from .env. Values are retained in memory and are never printed.
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^[[:space:]]*(export[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)= ]]; then
      name="${BASH_REMATCH[2]}"
      if declare -p "$name" &>/dev/null; then
        existing_names+=("$name")
        existing_values+=("${!name}")
      fi
    fi
  done < "$env_file"

  set -a
  # shellcheck disable=SC1090
  source "$env_file"
  set +a

  for ((index = 0; index < ${#existing_names[@]}; index++)); do
    name="${existing_names[$index]}"
    printf -v "$name" '%s' "${existing_values[$index]}"
    export "$name"
  done
}

require_factory_auth_env() {
  if [[ -z "${AI_FACTORY_SERVICE_TOKEN:-}" || ${#AI_FACTORY_SERVICE_TOKEN} -lt 32 ]]; then
    echo "AI_FACTORY_SERVICE_TOKEN must be set to at least 32 characters." >&2
    return 2
  fi
  if [[ -z "${AI_FACTORY_REVIEW_TOKEN:-}" || ${#AI_FACTORY_REVIEW_TOKEN} -lt 32 ]]; then
    echo "AI_FACTORY_REVIEW_TOKEN must be set to at least 32 characters." >&2
    return 2
  fi
  if [[ "$AI_FACTORY_SERVICE_TOKEN" == "$AI_FACTORY_REVIEW_TOKEN" ]]; then
    echo "AI_FACTORY_SERVICE_TOKEN and AI_FACTORY_REVIEW_TOKEN must differ." >&2
    return 2
  fi
}
