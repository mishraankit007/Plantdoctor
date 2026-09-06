#!/bin/bash
# Invoked by launchd on a schedule (see ~/Library/LaunchAgents/com.plantdoctor.autoblogpost.plist).
# Pulls latest, runs the RSS-based auto-poster, logs everything.
set -euo pipefail

REPO_DIR="/Users/ankitmishra/Documents/Projects/plant-doctor-site"
LOG_DIR="$REPO_DIR/scripts/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/auto-blog-post-$(date +%Y-%m-%d-%H%M%S).log"

{
  echo "=== Auto blog post run: $(date) ==="
  cd "$REPO_DIR"
  git pull origin main
  python3 scripts/auto_blog_post.py
  echo "=== Done: $(date) ==="
} >> "$LOG_FILE" 2>&1
