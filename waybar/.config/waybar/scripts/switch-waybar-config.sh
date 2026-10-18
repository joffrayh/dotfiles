#!/bin/bash

CONFIG_DIR="$HOME/.config/waybar"
CONFIGS_DIR="$CONFIG_DIR/configs"

# Collect available config directories
mapfile -t CONFIGS < <(find "$CONFIGS_DIR" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)

if [ "${#CONFIGS[@]}" -eq 0 ]; then
  echo "No configs found in $CONFIGS_DIR."
  exit 1
fi

THEME="$1"

# No argument: show a numbered menu and read the user's choice
if [ -z "$THEME" ]; then
  echo "Available configs:"
  for i in "${!CONFIGS[@]}"; do
    printf "  %d) %s\n" "$((i + 1))" "${CONFIGS[$i]}"
  done

  read -rp "Select a config (number): " CHOICE

  # Validate: must be a number within range
  if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt "${#CONFIGS[@]}" ]; then
    echo "Invalid selection."
    exit 1
  fi

  THEME="${CONFIGS[$((CHOICE - 1))]}"
fi

THEME_DIR="$CONFIGS_DIR/$THEME"

if [ ! -d "$THEME_DIR" ]; then
  echo "Theme '$THEME' does not exist."
  exit 1
fi

# Point the live config at the theme instead of copying it, so the theme
# folder stays the only copy. style.css @imports the theme (rather than being a
# symlink) so url()s in the theme resolve relative to the theme's own folder.
ln -sf "configs/$THEME/config" "$CONFIG_DIR/config"
printf '@import url("configs/%s/style.css");\n' "$THEME" > "$CONFIG_DIR/style.css"

echo "Switched to theme '$THEME'. Restarting Waybar..."

pkill waybar && waybar &

echo "Waybar restarted with theme '$THEME'."
