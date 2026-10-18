#!/usr/bin/env bash
set -euo pipefail

extract() {
  local FORCE=0
  local archive=""
  local base_name=""
  # outdir, success, and lockfile must NOT be local — the cleanup()
  # EXIT trap fires after extract() has returned (when set -e exits the
  # script on a non-zero return code), so local variables would already
  # be out of scope and cleanup would silently skip removing the directory.
  outdir=""
  success=0
  lockfile=""

  # -----------------------------
  # Parse flags (INSIDE function)
  # -----------------------------
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --force)
        FORCE=1
        shift
        ;;
      *)
        break
        ;;
    esac
  done

  # -----------------------------
  # Validate input
  # -----------------------------
  if [ $# -lt 1 ]; then
    echo "Usage: extract [--force] <archive> [target-folder]"
    return 1
  fi

  archive="$1"
  shift || true
  outdir="${1:-}"

  if [ ! -f "$archive" ]; then
    echo "File not found: $archive"
    return 1
  fi

  # -----------------------------
  # Auto folder name
  # -----------------------------
  base_name="$(basename "$archive")"
  base_name="${base_name%.*}"
  case "$archive" in
    *.tar.gz)  base_name="${base_name%.*}" ;;
    *.tar.bz2) base_name="${base_name%.*}" ;;
    *.tar.xz)  base_name="${base_name%.*}" ;;
  esac
  outdir="${outdir:-$base_name}"

  # -----------------------------
  # Overwrite protection
  # -----------------------------
  if [ -e "$outdir" ] && [ "$FORCE" -ne 1 ]; then
    echo "Error: '$outdir' already exists."
    echo "Use --force to overwrite."
    return 1
  fi

  # -----------------------------
  # Cleanup on failure
  # -----------------------------
  cleanup() {
    : "${outdir:?outdir not set}"
    if [ "$success" -ne 1 ]; then
      echo ""
      echo "Extraction failed or was interrupted. Cleaning up..."
      if [ -d "$outdir" ]; then
        rm -rf "$outdir"
        echo "Removed: $outdir"
      fi
    fi
    # Always remove the lockfile
    rm -f "$lockfile"
  }

  # Omit ERR — with set -e, any failure causes an EXIT, so
  # trapping ERR as well would fire cleanup twice (once for ERR,
  # once for EXIT), printing the failure message twice.
  trap cleanup EXIT INT TERM

  mkdir -p "$outdir"

  # -----------------------------
  # Safe lock (no collisions)
  # -----------------------------
  # mktemp is run unconditionally so lockfile is always defined
  # and cleanup can always safely rm -f it.
  lockfile="$(mktemp /tmp/extract.XXXXXX.lock)"

  if command -v flock >/dev/null 2>&1; then
    # Open FD 9 without exec so the file descriptor is not leaked
    # into the shell's global state after the function returns.
    {
      if ! flock -n 9; then
        echo "Another extraction is already running for this archive."
        return 1
      fi
    } 9>"$lockfile"
  fi

  # -----------------------------
  # Detect type
  # -----------------------------
  local type
  type="$(file -b "$archive")"
  echo "Detected: $type"
  echo "Extracting to: $outdir"

  # -----------------------------
  # Extract
  # -----------------------------
  case "$type" in
    *Zip*|*ZIP*)
      unzip -q "$archive" -d "$outdir"
      ;;
    *gzip*)
      tar -xzf "$archive" -C "$outdir"
      ;;
    *bzip2*)
      tar -xjf "$archive" -C "$outdir"
      ;;
    *XZ*|*xz*)
      tar -xJf "$archive" -C "$outdir"
      ;;
    *tar*)
      tar -xf "$archive" -C "$outdir"
      ;;
    *7-zip*|*7z*)
      # -bso1 sends normal output to stdout; -bsp0 suppresses progress
      7z x "$archive" -o"$outdir" -bso1 -bsp0
      ;;
    *RAR*)
      # Trailing slash ensures unrar treats the path as a directory
      # across all versions of unrar
      unrar x -idq "$archive" "$outdir/"
      ;;
    *)
      echo "Unsupported archive type: $type"
      return 1
      ;;
  esac

  success=1
  trap - EXIT INT TERM
  echo "Done."
}

extract "$@"