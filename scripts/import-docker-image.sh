#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_IMAGE_TAR="${REPO_ROOT}/dist/mcp-skill-framework-local.tar"
IMAGE_TAR="${1:-${DEFAULT_IMAGE_TAR}}"

if [[ ! -f "${IMAGE_TAR}" ]]; then
  echo "Docker image tar not found: ${IMAGE_TAR}" >&2
  exit 1
fi

docker load -i "${IMAGE_TAR}"
docker image inspect mcp-skill-framework:local >/dev/null

echo "Imported Docker image: mcp-skill-framework:local"
