#!/usr/bin/env bash
# Store Bitwarden Secrets Manager machine token (m1-runtime) in macOS Keychain.
# Interactive only — token is never written to disk, shell history, or repo files.
set -euo pipefail

KEYCHAIN_SERVICE="${OCTA_BWS_KEYCHAIN_SERVICE:-pl.octadecimal.m1-runtime.BWS_ACCESS_TOKEN}"
KEYCHAIN_ACCOUNT="${OCTA_BWS_KEYCHAIN_ACCOUNT:-m1-runtime}"

cd "$(dirname "$0")/.."

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Ten skrypt działa tylko na macOS (Keychain)." >&2
  exit 1
fi

if ! command -v security >/dev/null 2>&1; then
  echo "Brak narzędzia security." >&2
  exit 1
fi

_bws_bin() {
  if command -v bws >/dev/null 2>&1; then
    command -v bws
    return 0
  fi
  if [[ -x ".venv/bin/bws" ]]; then
    echo ".venv/bin/bws"
    return 0
  fi
  return 1
}

_read_token() {
  local prompt=$1
  local token=""
  local tty="/dev/tty"

  if [[ ! -r "$tty" ]]; then
    echo "Brak TTY — uruchom skrypt interaktywnie w terminalu (nie przez pipe)." >&2
    exit 1
  fi

  # Best-effort: do not record typed token in shell history.
  set +o history 2>/dev/null || true

  printf '%s' "$prompt" >"$tty"
  IFS= read -rs token <"$tty" || true
  printf '\n' >"$tty"

  if [[ -z "$token" ]]; then
    echo "Pusty token — przerwano." >&2
    exit 1
  fi
  printf '%s' "$token"
}

_verify_bws_token() {
  local token=$1
  local bws_bin
  if ! bws_bin="$(_bws_bin)"; then
    echo "Uwaga: bws niedostępne — pomijam weryfikację API (token i tak zostanie zapisany)." >&2
    return 0
  fi

  if ! BWS_ACCESS_TOKEN="$token" "$bws_bin" project list >/dev/null 2>&1; then
    echo "Token odrzucony przez BSM API — nie zapisano do Keychain." >&2
    return 1
  fi
  return 0
}

_store_in_keychain() {
  local token=$1
  security delete-generic-password -s "$KEYCHAIN_SERVICE" -a "$KEYCHAIN_ACCOUNT" >/dev/null 2>&1 || true
  security add-generic-password \
    -a "$KEYCHAIN_ACCOUNT" \
    -s "$KEYCHAIN_SERVICE" \
    -w "$token" \
    -U \
    >/dev/null
}

echo "Bitwarden SM — zapis tokenu machine account: ${KEYCHAIN_ACCOUNT}"
echo "Keychain service: ${KEYCHAIN_SERVICE}"
echo ""
echo "Token z panelu: Machine accounts → m1-runtime → Access Tokens → Create"
echo "Wklej token poniżej (input ukryty, nie trafia do historii shell)."
echo ""

token="$(_read_token "BWS access token: ")"

if ! _verify_bws_token "$token"; then
  unset token
  exit 1
fi

_store_in_keychain "$token"
unset token

if security find-generic-password -s "$KEYCHAIN_SERVICE" -a "$KEYCHAIN_ACCOUNT" >/dev/null 2>&1; then
  echo "OK — token zapisany w Keychain."
  echo ""
  echo "Użycie przy starcie Workspace:"
  echo '  export BWS_ACCESS_TOKEN="$(security find-generic-password -s '"'"'${KEYCHAIN_SERVICE}'"'"' -a '"'"'${KEYCHAIN_ACCOUNT}'"'"' -w)"'
  echo "  export LLM_PROVIDER=minimax"
  echo "  ./scripts/octa-mvp-up.sh"
else
  echo "Błąd: wpis Keychain nie został znaleziony po zapisie." >&2
  exit 1
fi
