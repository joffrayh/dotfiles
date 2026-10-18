#!/bin/bash

# State file remembers the last threshold we notified for, so we only
# notify once per threshold crossing instead of on every waybar update.
STATE_FILE="${XDG_RUNTIME_DIR:-/tmp}/waybar-battery-notify-state"
LAST=$(cat "$STATE_FILE" 2>/dev/null || echo "none")

# Detect if the system uses energy or charge files
if [ -f /sys/class/power_supply/BAT0/charge_now ]; then
    NOW="charge_now"
    FULL="charge_full"
else
    NOW="energy_now"
    FULL="energy_full"
fi

# Check if we are unplugged
if [ "$(cat /sys/class/power_supply/AC/online)" -eq 0 ]; then
    # Calculate combined percentage
    NOW_0=$(cat /sys/class/power_supply/BAT0/$NOW 2>/dev/null || echo 0)
    NOW_1=$(cat /sys/class/power_supply/BAT1/$NOW 2>/dev/null || echo 0)
    FULL_0=$(cat /sys/class/power_supply/BAT0/$FULL 2>/dev/null || echo 1)
    FULL_1=$(cat /sys/class/power_supply/BAT1/$FULL 2>/dev/null || echo 0)

    PERCENT=$(echo "($NOW_0 + $NOW_1) * 100 / ($FULL_0 + $FULL_1)" | bc)

    # Trigger notifications only when newly crossing a threshold downward
    if [ "$PERCENT" -le 10 ]; then
        if [ "$LAST" != "10" ]; then
            notify-send -u critical 'BATTERY CRITICAL' "Total battery is at ${PERCENT}%. Plug in immediately!"
            echo "10" > "$STATE_FILE"
        fi
    elif [ "$PERCENT" -le 20 ]; then
        if [ "$LAST" != "20" ] && [ "$LAST" != "10" ]; then
            notify-send -u normal 'Battery Low' "Total battery is at ${PERCENT}%."
            echo "20" > "$STATE_FILE"
        fi
    else
        # Above 20% — clear state so a future drop notifies again
        echo "none" > "$STATE_FILE"
    fi
else
    # Plugged in — reset so the next discharge cycle notifies again
    echo "none" > "$STATE_FILE"
fi
