#!/usr/bin/env bash
# Package staging WordPress site bundles under sites/staging-wp/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="${ROOT}/dist"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

usage() {
  cat <<EOF
Usage: $(basename "$0") [wowtherapies|slpwow|all]

Creates zip archives in sites/staging-wp/dist/.
Each site zip contains themes/, content/, DEPLOY.md, and README.md.
Theme-only zips are also emitted for direct wp-content/themes upload.
EOF
}

package_site() {
  local name="$1"
  local site_dir="${ROOT}/${name}"
  if [[ ! -d "${site_dir}" ]]; then
    echo "Missing site directory: ${site_dir}" >&2
    exit 1
  fi

  mkdir -p "${DIST}"

  local full_zip="${DIST}/${name}-staging-${STAMP}.zip"
  local latest_zip="${DIST}/${name}-staging.zip"
  (
    cd "${site_dir}"
    zip -qr "${full_zip}" . -x "*.DS_Store" -x "*__MACOSX*"
  )
  cp -f "${full_zip}" "${latest_zip}"

  local theme_dir
  case "${name}" in
    wowtherapies) theme_dir="wowtherapies-gp-child" ;;
    slpwow) theme_dir="slpwow-gp-child" ;;
    *) echo "Unknown site: ${name}" >&2; exit 1 ;;
  esac

  local theme_zip="${DIST}/${name}-theme-${STAMP}.zip"
  local theme_latest="${DIST}/${name}-theme.zip"
  (
    cd "${site_dir}/themes/${theme_dir}"
    zip -qr "${theme_zip}" . -x "*.DS_Store"
  )
  cp -f "${theme_zip}" "${theme_latest}"

  echo "Created ${latest_zip}"
  echo "Created ${theme_latest}"
}

main() {
  local target="${1:-all}"
  case "${target}" in
    wowtherapies|slpwow)
      package_site "${target}"
      ;;
    all)
      package_site wowtherapies
      package_site slpwow
      local bundle="${DIST}/staging-wp-all-${STAMP}.zip"
      local bundle_latest="${DIST}/staging-wp-all.zip"
      (
        cd "${ROOT}"
        zip -qr "${bundle}" wowtherapies slpwow README.md SCOPE.md scripts/package-sites.sh -x "*/dist/*"
      )
      cp -f "${bundle}" "${bundle_latest}"
      echo "Created ${bundle_latest}"
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage >&2
      exit 1
      ;;
  esac
}

main "$@"
