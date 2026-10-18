#!/usr/bin/env bash
# Refresh packages/*.txt from what's installed on this machine.
# Run after installing/removing things, then commit the diff.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/packages"

pacman -Qqen | grep -vxFf hardware.txt > pacman.txt
pacman -Qqem | grep -v -- '-debug$' > aur.txt
command -v code >/dev/null && code --list-extensions > vscode-extensions.txt

git -C .. --no-pager diff --stat -- packages
