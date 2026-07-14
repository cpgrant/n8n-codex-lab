#!/usr/bin/env bash

# Sourced by synthetic API smoke tests. Do not print token values.

load_service_auth() {
  if [[ -z "${AI_FACTORY_SERVICE_TOKEN:-}" || ${#AI_FACTORY_SERVICE_TOKEN} -lt 32 ]]; then
    echo "AI_FACTORY_SERVICE_TOKEN must be set to at least 32 characters." >&2
    return 2
  fi
  SERVICE_AUTH_ARGS=(-H "Authorization: Bearer $AI_FACTORY_SERVICE_TOKEN")
}

load_review_auth() {
  local actor_id="$1"
  if [[ -z "${AI_FACTORY_REVIEW_TOKEN:-}" || ${#AI_FACTORY_REVIEW_TOKEN} -lt 32 ]]; then
    echo "AI_FACTORY_REVIEW_TOKEN must be set to at least 32 characters." >&2
    return 2
  fi
  if [[ ! "$actor_id" =~ ^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$ ]]; then
    echo "Synthetic review actor ID is invalid." >&2
    return 2
  fi
  REVIEW_AUTH_ARGS=(
    -H "Authorization: Bearer $AI_FACTORY_REVIEW_TOKEN"
    -H "X-AI-Factory-Actor-ID: $actor_id"
  )
}
