#!/bin/bash

# Define the wallpaper directory
WALLPAPER_DIR="$HOME/.config/hypr/wallpapers"

# Function to display available wallpapers
list_wallpapers() {
    echo "Available Wallpapers:"
    local i=1
    for file in "$WALLPAPER_DIR"/*; do
        if [[ -f "$file" ]]; then
            echo "$i) $(basename "$file")"
            i=$((i + 1))
        fi
    done
}

# Function to update the hyprpaper.conf file
set_wallpaper() {
    local wallpaper=$1
    for mon in $(hyprctl monitors -j | jq -r '.[].name'); do
        hyprctl hyprpaper wallpaper "$mon,$wallpaper"
    done
}

# If the script is called with a direct wallpaper name
if [[ -n "$1" ]]; then
    # Check if the specified wallpaper exists
    wallpaper_path="$WALLPAPER_DIR/$1"
    if [[ -f "$wallpaper_path" ]]; then
        set_wallpaper "$wallpaper_path"
    else
        echo "Wallpaper '$1' not found in $WALLPAPER_DIR"
        exit 1
    fi
else
    # No argument provided, list available wallpapers and let user choose
    list_wallpapers
    echo -n "Enter the number of the wallpaper you want to set: "
    read -r choice

    # Get the wallpaper from the list based on user choice
    wallpaper=$(ls "$WALLPAPER_DIR" | sed -n "${choice}p")
    if [[ -n "$wallpaper" && -f "$WALLPAPER_DIR/$wallpaper" ]]; then
        set_wallpaper "$WALLPAPER_DIR/$wallpaper"
    else
        echo "Invalid selection."
        exit 1
    fi
fi

