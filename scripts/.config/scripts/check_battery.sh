#!/bin/bash

# Function to get battery information
get_battery_info() {
    local battery=$1
    local status=$(cat /sys/class/power_supply/${battery}/status)
    local capacity=$(cat /sys/class/power_supply/${battery}/capacity)
    echo "  Status: ${status}"
    echo "  Capacity: ${capacity}%"
}

# Check if both batteries exist and print their information
if [ -d "/sys/class/power_supply/BAT0" ]; then
    echo "Internal Battery (BAT0):"
    get_battery_info "BAT0"
    echo ""
else
    echo "Battery BAT0 (internal) not found."
    echo ""
fi

if [ -d "/sys/class/power_supply/BAT1" ]; then
    echo "External Battery (BAT1):"
    get_battery_info "BAT1"
else
    echo "Battery BAT1 (external) not found."
    echo ""
fi