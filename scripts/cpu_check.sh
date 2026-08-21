#!/bin/bash
grep -m 1 -i "model name" /proc/cpuinfo
grep -iE "cpu cores" /proc/cpuinfo | head -n 1
echo "Load  average:"
echo "1 minute: $(awk '{print $1}' /proc/loadavg)"
echo "5 minute: $(awk '{print $2}' /proc/loadavg)"
echo "15 minute: $(awk '{print $3}' /proc/loadavg)"
hour_uptime=$(uptime -p | awk '{print $2}')
minute_uptime=$(uptime -p | awk '{print $4}')
echo "Uptime: $hour_uptime hours, $minute_uptime minutes "

