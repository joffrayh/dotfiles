#!/usr/bin/env bash
# Set up this config on a fresh Arch install. Safe to re-run.
# Usage: git clone <repo> ~/dotfiles && ~/dotfiles/install.sh
set -euo pipefail
DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DOTFILES"

STOW_PACKAGES=(zsh git starship foot hypr waybar fuzzel swaync keyd btop theme scripts nvim zed vscode mime neofetch oculante)

list() { grep -vE '^\s*(#|$)' "$1"; }
ask()  { read -rp "$1 [y/N] " r; [[ $r == [yY]* ]]; }
step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

step "Official packages"
mapfile -t pkgs < <(list packages/pacman.txt)
sudo pacman -S --needed "${pkgs[@]}"
if ask "Install Intel/ThinkPad hardware packages (packages/hardware.txt)?"; then
  mapfile -t pkgs < <(list packages/hardware.txt)
  sudo pacman -S --needed "${pkgs[@]}"
fi

step "AUR packages"
if ! command -v paru >/dev/null; then
  tmp=$(mktemp -d)
  git clone https://aur.archlinux.org/paru-bin.git "$tmp/paru-bin"
  (cd "$tmp/paru-bin" && makepkg -si --noconfirm)
  rm -rf "$tmp"
fi
# paru itself is already present (as paru-bin) by this point
mapfile -t pkgs < <(list packages/aur.txt | grep -vx paru)
paru -S --needed "${pkgs[@]}"

step "Linking dotfiles with stow"
if git diff --quiet && git diff --cached --quiet; then
  # --adopt pulls any pre-existing files (e.g. app defaults) into the repo so
  # stow doesn't conflict; checkout then restores the repo's versions.
  stow --adopt -t "$HOME" "${STOW_PACKAGES[@]}"
  git checkout -- .
else
  echo "Repo has uncommitted changes; linking without --adopt (conflicts will be reported)."
  stow -t "$HOME" "${STOW_PACKAGES[@]}"
fi

step "System files"
if ask "Copy files from system/ into / (existing files get a numbered backup)?"; then
  (cd system && find . -type f -printf '%P\n') | while read -r f; do
    sudo cp --backup=numbered "system/$f" "/$f"
    echo "  /$f"
  done
  sudo locale-gen
  echo "  GRUB config copied but not applied. If wanted: sudo grub-mkconfig -o /boot/grub/grub.cfg"
fi
sudo mkdir -p /etc/keyd
sudo ln -sfn "$HOME/.config/keyd/default.conf" /etc/keyd/default.conf

step "Services"
list packages/services.txt | while read -r unit; do
  if [[ $unit == user:* ]]; then
    systemctl --user enable "${unit#user:}" || true
  elif systemctl list-unit-files "$unit" --no-legend | grep -q .; then
    sudo systemctl enable "$unit"
  else
    echo "  skipping $unit (not installed)"
  fi
done
getent group docker >/dev/null && sudo usermod -aG docker "$USER"

step "VS Code extensions"
if command -v code >/dev/null; then
  list packages/vscode-extensions.txt | xargs -rn1 code --install-extension
fi

step "Shell"
[[ $SHELL == */zsh ]] || chsh -s /usr/bin/zsh

step "Done"
cat <<'EOF'
Per-machine things to check:
  - Monitors: edit the MONITORS section of ~/.config/hypr/hyprland.lua
  - Lock screen: if the resolution isn't 1920x1080, run
      python3 ~/.config/hypr/lock/make-lock.py WIDTH HEIGHT
  - GTK 4 theme: open nwg-look and click Apply (recreates ~/.config/gtk-4.0 links)
  - Reboot (or log out) so the shell, groups and services take effect.
EOF
