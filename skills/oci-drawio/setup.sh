#!/usr/bin/env bash
#
# setup.sh - OCI/AWS draw.io Skill setup
#
# Downloads official OCI and AWS SVG icon packages, converts them to draw.io
# shape libraries, and generates provider-specific component dictionaries.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICONS_DIR="${SCRIPT_DIR}/icons"
COMPONENTS_DIR="${SCRIPT_DIR}/components"
SCRIPTS_DIR="${SCRIPT_DIR}/scripts"
TMP_DIR="${SCRIPT_DIR}/.tmp"

OCI_SVG_ZIP_URL="https://docs.oracle.com/en-us/iaas/Content/Resources/Assets/OCI_Icons_PNG_SVG.zip"
AWS_ARCH_PAGE_URL="https://aws.amazon.com/architecture/icons/"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $1" >&2; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1" >&2; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

usage() {
    cat <<'EOF'
Usage: bash setup.sh [--provider oci|aws|all] [--keep-tmp]

Options:
  --provider  Which provider assets to generate. Default: all
  --keep-tmp  Keep downloaded archives and extracted icons under .tmp/
  -h, --help  Show this help
EOF
}

PROVIDER="all"
KEEP_TMP="0"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider)
            PROVIDER="${2:-}"
            shift 2
            ;;
        --keep-tmp)
            KEEP_TMP="1"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            error "Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
done

case "$PROVIDER" in
    oci|aws|all) ;;
    *)
        error "--provider must be one of: oci, aws, all"
        exit 1
        ;;
esac

check_deps() {
    local missing=()
    for cmd in curl unzip base64 uv; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing+=("$cmd")
        fi
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing required commands: ${missing[*]}"
        exit 1
    fi
}

download_with_retry() {
    local url="$1"
    local output="$2"
    local max_retries=3
    local retry_delay=2

    for ((i = 1; i <= max_retries; i++)); do
        if curl -fSL --connect-timeout 30 --max-time 300 -o "$output" "$url" 2>/dev/null; then
            return 0
        fi
        if [[ $i -lt $max_retries ]]; then
            warn "Download attempt $i failed for $url. Retrying in ${retry_delay}s..."
            sleep "$retry_delay"
            retry_delay=$((retry_delay * 2))
        fi
    done
    return 1
}

find_oci_svg_root() {
    local search_dir="$1"
    local svg_dir

    svg_dir=$(find "$search_dir" -maxdepth 4 -type d -iname "SVG" 2>/dev/null | head -1 || true)
    if [[ -n "$svg_dir" ]]; then
        echo "$svg_dir"
        return 0
    fi

    svg_dir=$(find "$search_dir" -name "*.svg" -print0 2>/dev/null \
        | xargs -0 -I{} dirname "{}" \
        | sort | uniq -c | sort -rn | head -1 | awk '{print $2}' || true)

    if [[ -n "$svg_dir" ]]; then
        echo "$(dirname "$svg_dir")"
        return 0
    fi

    return 1
}

resolve_aws_zip_url() {
    local page_file="${TMP_DIR}/aws-architecture-icons.html"

    info "Resolving latest AWS Architecture Icons package..."
    download_with_retry "$AWS_ARCH_PAGE_URL" "$page_file" || return 1

    grep -o 'https://d1\.awsstatic\.com[^"]*Icon-package[^"]*\.zip' "$page_file" | head -1
}

generate_outputs() {
    local provider="$1"
    local input_root="$2"
    local icons_output="$3"
    local components_output="$4"
    local index_output="$5"
    local category_dir="$6"

    mkdir -p "$(dirname "$icons_output")" "$(dirname "$components_output")" "$(dirname "$index_output")" "$category_dir"

    (
        cd "$SCRIPT_DIR"
        uv run python "${SCRIPTS_DIR}/generate_drawio_assets.py" "$provider" \
            --input-root "$input_root" \
            --icons-output "$icons_output" \
            --components-output "$components_output" \
            --index-output "$index_output" \
            --category-dir "$category_dir"
    )
}

generate_oci() {
    local oci_dir="${TMP_DIR}/oci"
    local svg_root

    info "Downloading OCI icon set from Oracle..."
    mkdir -p "$oci_dir"
    download_with_retry "$OCI_SVG_ZIP_URL" "${oci_dir}/oci_icons.zip" || {
        error "Failed to download OCI icon set."
        return 1
    }

    info "Extracting OCI icons..."
    unzip -qo "${oci_dir}/oci_icons.zip" -d "${oci_dir}/extracted"

    svg_root=$(find_oci_svg_root "${oci_dir}/extracted") || {
        error "Could not find OCI SVG root in the downloaded archive."
        return 1
    }

    info "Generating OCI draw.io assets..."
    generate_outputs \
        "oci" \
        "$svg_root" \
        "${ICONS_DIR}/oci-shapes.xml" \
        "${COMPONENTS_DIR}/oci_components.json" \
        "${COMPONENTS_DIR}/index.json" \
        "${COMPONENTS_DIR}"
}

generate_aws() {
    local aws_dir="${TMP_DIR}/aws"
    local aws_zip_url

    mkdir -p "$aws_dir" "${COMPONENTS_DIR}/aws"

    aws_zip_url=$(resolve_aws_zip_url)
    if [[ -z "$aws_zip_url" ]]; then
        error "Could not resolve the AWS icon package URL from ${AWS_ARCH_PAGE_URL}"
        return 1
    fi

    info "Downloading AWS icon set..."
    info "URL: $aws_zip_url"
    download_with_retry "$aws_zip_url" "${aws_dir}/aws_icons.zip" || {
        error "Failed to download AWS icon set."
        return 1
    }

    info "Extracting AWS icons..."
    unzip -qo "${aws_dir}/aws_icons.zip" -d "${aws_dir}/extracted"

    info "Generating AWS draw.io assets..."
    generate_outputs \
        "aws" \
        "${aws_dir}/extracted" \
        "${ICONS_DIR}/aws-shapes.xml" \
        "${COMPONENTS_DIR}/aws_components.json" \
        "${COMPONENTS_DIR}/aws/index.json" \
        "${COMPONENTS_DIR}/aws"
}

cleanup() {
    if [[ "$KEEP_TMP" == "0" && -d "$TMP_DIR" ]]; then
        info "Cleaning up temporary files..."
        rm -rf "$TMP_DIR"
    fi
}

main() {
    info "========================================="
    info "  OCI/AWS draw.io Skill - Setup"
    info "========================================="
    echo

    check_deps
    mkdir -p "$TMP_DIR" "$ICONS_DIR" "$COMPONENTS_DIR"

    if [[ "$PROVIDER" == "oci" || "$PROVIDER" == "all" ]]; then
        generate_oci
    fi

    if [[ "$PROVIDER" == "aws" || "$PROVIDER" == "all" ]]; then
        generate_aws
    fi

    cleanup

    echo
    info "Generated files:"
    if [[ "$PROVIDER" == "oci" || "$PROVIDER" == "all" ]]; then
        info "  icons/oci-shapes.xml"
        info "  components/oci_components.json"
        info "  components/index.json"
        info "  components/{category}.json"
    fi
    if [[ "$PROVIDER" == "aws" || "$PROVIDER" == "all" ]]; then
        info "  icons/aws-shapes.xml"
        info "  components/aws_components.json"
        info "  components/aws/index.json"
        info "  components/aws/{category}.json"
    fi
}

trap cleanup EXIT
main "$@"
