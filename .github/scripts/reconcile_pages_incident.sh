#!/usr/bin/env bash
set -euo pipefail

: "${GH_TOKEN:?GH_TOKEN is required}"
: "${HEALTH_EXIT:?HEALTH_EXIT is required}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
: "${GITHUB_RUN_ID:?GITHUB_RUN_ID is required}"
: "${GITHUB_SERVER_URL:?GITHUB_SERVER_URL is required}"

TITLE='[Automated] GitHub Pages production health incident'
MARKER='<!-- missionchief-pages-production-health -->'
SEARCH_QUERY='"GitHub Pages production health incident" in:title'
ISSUE_JSON="$(gh issue list --state all --search "$SEARCH_QUERY" --json number,state,title --limit 20)"
ISSUE_NUMBER="$(jq -r --arg title "$TITLE" '.[] | select(.title == $title) | .number' <<< "$ISSUE_JSON" | head -n 1)"
ISSUE_STATE="$(jq -r --arg title "$TITLE" '.[] | select(.title == $title) | .state' <<< "$ISSUE_JSON" | head -n 1)"

post_discord() {
  local heading="$1"
  local description="$2"
  local color="$3"
  [[ -n "${DISCORD_WEBHOOK:-}" ]] || return 0
  jq -n \
    --arg title "$heading" \
    --arg description "$description" \
    --arg url "${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}" \
    --argjson color "$color" \
    '{embeds:[{title:$title,description:$description,url:$url,color:$color,footer:{text:"MissionChief Map Command Toolkit · GitHub Pages monitor"}}]}' |
    curl --fail --silent --show-error \
      --header 'Content-Type: application/json' \
      --data-binary @- \
      "$DISCORD_WEBHOOK" >/dev/null
}

if [[ "$HEALTH_EXIT" != "0" ]]; then
  {
    echo "$MARKER"
    echo
    cat pages-production-health.md
    echo
    echo "Workflow: ${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
  } > /tmp/pages-incident.md

  if [[ -z "$ISSUE_NUMBER" ]]; then
    ISSUE_URL="$(gh issue create \
      --title "$TITLE" \
      --body-file /tmp/pages-incident.md \
      --label 'bug' \
      --label 'needs-triage' \
      --label 'priority: high' \
      --label 'area: release pipeline')"
    post_discord '❌ GitHub Pages health incident' "The public Toolkit documentation site failed one or more live production checks. Incident: ${ISSUE_URL}" 15158332
  elif [[ "$ISSUE_STATE" == "CLOSED" ]]; then
    gh issue reopen "$ISSUE_NUMBER"
    gh issue edit "$ISSUE_NUMBER" --body-file /tmp/pages-incident.md
    gh issue comment "$ISSUE_NUMBER" --body "The production health incident has recurred. See the updated diagnostic body and workflow run."
    post_discord '❌ GitHub Pages incident recurred' "The public Toolkit documentation site has failed live checks again. Incident #${ISSUE_NUMBER}." 15158332
  else
    gh issue edit "$ISSUE_NUMBER" --body-file /tmp/pages-incident.md
    gh issue comment "$ISSUE_NUMBER" --body "Scheduled recheck still fails. Diagnostic state was refreshed by workflow run ${GITHUB_RUN_ID}."
  fi
  exit 1
fi

if [[ -n "$ISSUE_NUMBER" && "$ISSUE_STATE" == "OPEN" ]]; then
  gh issue comment "$ISSUE_NUMBER" --body "✅ Live GitHub Pages checks recovered successfully in workflow run ${GITHUB_RUN_ID}."
  gh issue close "$ISSUE_NUMBER" --reason completed
  post_discord '✅ GitHub Pages recovered' "The public Toolkit documentation site has passed all live production checks. Incident #${ISSUE_NUMBER} was closed." 5763719
fi
