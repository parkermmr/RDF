[ -n "${arg_domain}" ] && DOMAIN="$arg_domain"
TOKEN="${arg_token:-${PAT-}}"
[ -n "${TOKEN:-}" ] || { echo "Missing token: provide --token or set PAT." >&2; exit 2; }

trim() { printf "%s" "$1" | awk '{$1=$1;print}'; }

csv_rows() {
  printf "%s\n" "$PROJECT_MAP_CSV" \
  | grep -v '^[[:space:]]*$' \
  | grep -v '^[[:space:]]*#' \
  | awk -F',' '
      {for(i=1;i<=NF;i++){gsub(/^[ \t]+|[ \t]+$/, "", $i)}}
      NF>=3 {printf "%s,%s,%s\n", $1, $2, $3}
    '
}

lookup_rows() {
  g="$1"; p="$2"
  if [ -n "$g" ] && [ -n "$p" ]; then
    csv_rows | awk -F',' -v g="$g" -v p="$p" 'tolower($1)==tolower(g) && tolower($2)==tolower(p)'
  elif [ -n "$g" ]; then
    csv_rows | awk -F',' -v g="$g" 'tolower($1)==tolower(g)'
  elif [ -n "$p" ]; then
    csv_rows | awk -F',' -v p="$p" 'tolower($2)==tolower(p)'
  else
    csv_rows
  fi
}

trigger_one() {
  pid="$1"
  url="${DOMAIN%/}/api/v4/projects/${pid}/pipeline"
  code="$(curl -sS -o /tmp/pl.out.$$ -w "%{http_code}" \
    --request POST \
    --header "PRIVATE-TOKEN: ${TOKEN}" \
    --form ref=main \
    "$url" || true)"
  if [ "$code" -ge 200 ] && [ "$code" -lt 300 ]; then
    id="$(awk -F'"'"'" '/"id":/{print $4; exit}' /tmp/pl.out.$$ || true)"
    web_url="$(awk -F'"'"'" '/"web_url":/{print $4; exit}' /tmp/pl.out.$$ || true)"
    echo "OK  project_id=${pid}  pipeline_id=${id:-?}  ${web_url:-}"
  else
    echo "ERR project_id=${pid}  http=${code}  body=$(cat /tmp/pl.out.$$)" >&2
    rm -f /tmp/pl.out.$$
    return 1
  fi
  rm -f /tmp/pl.out.$$
}

main() {
  rows="$(lookup_rows "${arg_group:-}" "${arg_project:-}")"
  [ -n "$rows" ] || { echo "No matching projects. Check --group/--project and mapping." >&2; exit 3; }

  echo "$rows" | while IFS=, read -r grp proj pid; do
    grp="$(trim "$grp")"; proj="$(trim "$proj")"; pid="$(trim "$pid")"
    [ -n "$grp" ] && [ -n "$proj" ] && [ -n "$pid" ] || continue
    echo "Triggering: group=${grp} project=${proj} id=${pid}"
    trigger_one "$pid"
  done
}

main
