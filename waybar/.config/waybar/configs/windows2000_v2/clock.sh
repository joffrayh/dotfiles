#!/bin/sh
# Windows 2000 style clock: "3:45 PM  18/10/2026", full date in the tooltip
printf '{"text":"%s","tooltip":"%s"}\n' "$(LC_TIME=C date '+%-I:%M %p  %d/%m/%Y')" "$(date '+%A, %d %B %Y')"
