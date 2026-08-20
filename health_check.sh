#!/bin/bash
echo "==========SYSTEM HEALTH CHECK=========="

echo "Hostname: $(hostname)"
echo "User: $USER"
echo "Date: $(date)"


check_memory() {
	echo "------MEMORY USAGE------"
	#memory used percentage
        mem_total=$(free -m | awk '/Mem:/{print $2}')
        mem_used=$(free -m | awk '/Mem:/{print $3}')
        mem_perc=$((mem_used *100 /mem_total))
        echo "Memory usage: ${mem_perc}%"

        if [ "$mem_perc" -ge 80 ];then
	       echo 'WARNING: Memory usage high!'
        else
	       echo 'Memory status: OK'
        fi
	#total memory
        echo "Total Memory: $(free -m | awk 'NR==2{print $2}') MB"
	#used memory
        echo "Used Memory: $(free -m | awk 'NR==2{print $3}') MB"
	#free memory
        echo "Free Memory: $(free -m | awk 'NR==2{print $4}') MB"
}
check_disk(){
	echo "------DISK USAGE------"
	#Disk percentage usage
        disk_perc=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
        echo "Disk Usage: ${disk_perc}%"
        if [ "$disk_perc" -ge 80 ];then
	        echo 'WARNING: Disk usage high!'
        else 
	        echo 'Disk Status: OK'
        fi
	#total disk space
        echo "Total disk usage: $(df -h --total | awk 'NR==20{print $2}')"
	#used disk space
        echo "Used Disk space: $(df -h --total |  awk 'NR==20{print $3}')"
	#available disk space
        echo "Available Disk space: $(df -h --total | awk 'NR==20{print $4}')"

}
check_network(){
	echo "----NETWORK----"
	#hostname
	echo "Hostname :$(hostname)"
	#ip address
	echo "Host IP address: $(hostname -I)"
	#ipv4 and ipv6 address
	echo "Ip address:"
	ip addr show | grep "inet" | grep -v "127.0.0.1"
	#Deafult gateway route
	echo "Default Route:"
	ip route | grep "default"
	#Routing table
	echo "Routing tables:"
        ip route | grep -v "default"
	#listening ports
        echo "Listening ports:"
        ss -tulpn |  grep -iE "HTTP/HTTPS"
	#active interfaces
        active_interface=$(ip route | awk '/default/ {print $5; exit}')
        echo "Active interface : $active_interface"
	#interface status
        interface_status=$(ip link show "$active_interface" | awk '/state/ {print $9}')
        echo "Interface status : $interface_status"
	#connectivity test
        if  ping -c 8 -W 2 8.8.8.8 > /dev/null 2>&1 ]; then
	        echo "Connectivity: ONLINE"
	else
           	echo "Connectivity: OFFLINE"
	fi

}	
echo "=========CHECK COMPLETE========="
check_memory
check_disk
check_network
