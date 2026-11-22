#!/bin/sh
# Vercel's install step: mise, and of the tools in mise.toml only node, which `mise run web` needs.
# The rest are for the data pipeline, which the website does not run.
set -eu
curl -fsSL https://mise.run | sh
mise="$HOME/.local/bin/mise"
"$mise" trust
MISE_ENABLE_TOOLS=node "$mise" install
