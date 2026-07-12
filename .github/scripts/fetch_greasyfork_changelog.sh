#!/usr/bin/env bash
set -euo pipefail

: "${CURRENT_VERSION:?CURRENT_VERSION is required}"
: "${PREVIOUS_VERSION:?PREVIOUS_VERSION is required}"

DIRECT_HISTORY_URLS=(
  "https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit/versions?show_all_versions=1&list_all=1"
  "https://greasyfork.org/en/scripts/586018/versions?show_all_versions=1&list_all=1"
  "https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit/versions.html?show_all_versions=1&list_all=1"
)
BROWSER_UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
SOURCE_FILE="greasyfork-history-source.txt"
OUTPUT_FILE="greasyfork-changelog.txt"

rm -f "$SOURCE_FILE" "$OUTPUT_FILE" chrome-history.log

parse_source() {
  python3 .github/scripts/extract_greasyfork_changelog.py \
    "$CURRENT_VERSION" \
    "$PREVIOUS_VERSION" \
    "$SOURCE_FILE" \
    "$OUTPUT_FILE"
}

# Try normal HTTP first. Log the actual status so a permanent block is obvious.
for attempt in 1 2; do
  echo "Reading Greasy Fork History directly (attempt $attempt of 2)..."

  for history_url in "${DIRECT_HISTORY_URLS[@]}"; do
    rm -f "$SOURCE_FILE" "$OUTPUT_FILE"

    http_code="$(
      curl \
        --silent \
        --show-error \
        --location \
        --compressed \
        --http1.1 \
        --max-time 30 \
        --retry 1 \
        --retry-delay 3 \
        --header "Accept: text/html,application/xhtml+xml" \
        --header "Accept-Language: en-GB,en;q=0.9" \
        --header "Cache-Control: no-cache" \
        --header "Pragma: no-cache" \
        --referer "https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit" \
        --user-agent "$BROWSER_UA" \
        --output "$SOURCE_FILE" \
        --write-out "%{http_code}" \
        "${history_url}&cache_bust=$(date +%s%N)" || true
    )"

    echo "Direct History response: HTTP ${http_code:-000} from $history_url"

    if [[ "$http_code" == "200" && -s "$SOURCE_FILE" ]]; then
      echo "Downloaded direct History source: $(wc -c < "$SOURCE_FILE") bytes"
      if parse_source; then
        exit 0
      fi
    fi
  done

  if [[ "$attempt" -lt 2 ]]; then
    sleep 8
  fi
done

# Greasy Fork may return HTTP 403 to curl on GitHub-hosted runners. Render the
# same public page with the browser already installed on the runner.
chrome_bin="$(
  command -v google-chrome ||
  command -v google-chrome-stable ||
  command -v chromium ||
  command -v chromium-browser ||
  true
)"

if [[ -z "$chrome_bin" ]]; then
  echo "No Chrome or Chromium executable is available on this runner." >&2
  exit 1
fi

for attempt in 1 2; do
  echo "Reading Greasy Fork History with headless Chrome (attempt $attempt of 2)..."

  for history_url in "${DIRECT_HISTORY_URLS[@]}"; do
    rm -f "$SOURCE_FILE" "$OUTPUT_FILE" chrome-history.log

    if timeout 60 "$chrome_bin" \
      --headless=new \
      --disable-gpu \
      --no-sandbox \
      --disable-dev-shm-usage \
      --disable-extensions \
      --user-agent="$BROWSER_UA" \
      --dump-dom \
      "${history_url}&cache_bust=$(date +%s%N)" \
      > "$SOURCE_FILE" 2>chrome-history.log; then

      echo "Downloaded Chrome History source: $(wc -c < "$SOURCE_FILE") bytes"
      if [[ -s "$SOURCE_FILE" ]] && parse_source; then
        exit 0
      fi
    else
      echo "Headless Chrome did not return a usable page."
      tail -n 10 chrome-history.log 2>/dev/null || true
    fi
  done

  if [[ "$attempt" -lt 2 ]]; then
    sleep 8
  fi
done

exit 1
