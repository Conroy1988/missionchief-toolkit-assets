#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


def replace_block(path: Path, start_marker: str, end_marker: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def main() -> int:
    release_block = '''      - name: Post verified release to Discord
        env:
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_RELEASE_WEBHOOK }}
          RELEASE_VERSION: ${{ inputs.version }}
          RELEASE_URL: ${{ github.server_url }}/${{ github.repository }}/releases/tag/v${{ inputs.version }}
          BACKUP_COMMIT: ${{ steps.private_backup.outputs.backup_commit }}
        shell: bash
        run: |
          set -euo pipefail
          [[ -n "${DISCORD_WEBHOOK_URL:-}" ]] || { echo "::error::DISCORD_RELEASE_WEBHOOK is not configured."; exit 1; }
          [[ -n "${BACKUP_COMMIT:-}" ]] || { echo "::error::Private backup commit was not recorded."; exit 1; }
          SCRIPT_URL="$(jq -r '.greasyFork.scriptUrl' .github/release-settings.json)"
          INSTALL_URL="$(jq -r '.greasyFork.installUrl' .github/release-settings.json)"
          HASH="$(jq -r '.sha256' "release-bundle/release-manifest-v${RELEASE_VERSION}.json")"

          python3 .github/scripts/build_discord_release_payload.py \\
            --mode primary \\
            --version "$RELEASE_VERSION" \\
            --changelog "release-bundle/CHANGELOG-v${RELEASE_VERSION}.md" \\
            --output discord-release-payload.json \\
            --release-url "$RELEASE_URL" \\
            --script-url "$SCRIPT_URL" \\
            --install-url "$INSTALL_URL" \\
            --sha256 "$HASH" \\
            --backup-commit "$BACKUP_COMMIT"

          curl --fail --silent --show-error --max-time 30 --retry 2 --retry-delay 5 \\
            --request POST --header "Content-Type: application/json" \\
            --data @discord-release-payload.json "${DISCORD_WEBHOOK_URL}?wait=true"

'''
    replace_block(
        Path(".github/workflows/release-toolkit.yml"),
        "      - name: Post verified release to Discord\n",
        "      - name: Record successful release in dashboard\n",
        release_block,
    )

    fallback_block = '''      - name: Post fallback release notification
        if: steps.pending.outputs.pending == 'true'
        env:
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_RELEASE_WEBHOOK }}
          CURRENT_VERSION: ${{ steps.version.outputs.live }}
          PREVIOUS_VERSION: ${{ steps.version.outputs.announced }}
        shell: bash
        run: |
          set -euo pipefail
          if [[ -z "${DISCORD_WEBHOOK_URL:-}" ]]; then
            echo "::error::The DISCORD_RELEASE_WEBHOOK repository secret is not configured."
            exit 1
          fi

          SCRIPT_URL="https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit"
          HISTORY_URL="${SCRIPT_URL}/versions"
          INSTALL_URL="https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js"

          python3 .github/scripts/build_discord_release_payload.py \\
            --mode fallback \\
            --version "$CURRENT_VERSION" \\
            --previous-version "$PREVIOUS_VERSION" \\
            --changelog greasyfork-changelog.txt \\
            --output discord-payload.json \\
            --script-url "$SCRIPT_URL" \\
            --history-url "$HISTORY_URL" \\
            --install-url "$INSTALL_URL"

          curl --fail --silent --show-error --max-time 30 --retry 2 --retry-delay 5 \\
            --request POST --header 'Content-Type: application/json' \\
            --data @discord-payload.json "${DISCORD_WEBHOOK_URL}?wait=true"

'''
    replace_block(
        Path(".github/workflows/greasyfork-release-monitor.yml"),
        "      - name: Post fallback release notification\n",
        "      - name: Record announced version\n",
        fallback_block,
    )

    print("Discord release notification workflows redesigned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
