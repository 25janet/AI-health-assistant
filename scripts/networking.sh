#!/bin/bash
active_interface=$(ip route | awk '/default/ {print $5; exit}')
echo "Active interface : $active_interface"
interface_status=$(ip link show "$active_interface" | awk '/state/ {print $9}')
echo "Interface status : $interface_status"
if  ping -c 8 -W 2 8.8.8.8 > /dev/null 2>&1 ]; then
	echo "Connectivity: ONLINE"
else
	echo "Connectivity: OFFLINE"
fi

