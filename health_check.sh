#!/bin/bash
echo "==========SYSTEM HEALTH CHECK=========="

echo "Hostname: $(hostname)"
echo "User: $USER"
echo "Date: $(date)"


check_memory() {
	echo"------MEMORY USAGE------"
        mem_total=$(free -m | awk '/Mem:/{print $2}')
        mem_used=$(free -m | awk '/Mem:/{print $3}')
        mem_perc=$((mem_used *100 /mem_total))
        echo "Memory usage: ${mem_perc}%"

        if [ "$mem_perc" -ge 80 ];then
	       echo 'WARNING: Memory usage high!'
        else
	       echo 'Memory status: OK'
        fi
}
check_disk(){
	echo "------DISK USAGE------"
        disk_perc=$(df / | awk 'NR==2 {print $5}' | tr -d' %')
        echo "Disk Usage: ${disk_perc}%"
        if [ "$disk_perc" -ge 80 ];then
	        echo 'WARNING: Disk usage high!'
        else 
	        echo 'Disk Status: OK'
        fi
}
check_network(){
	echo "----NETWORK----"
	echo "Hostname :$(hostname)"
	echo "Host IP address: $(hostname -I)"
	echo "Ip address:"
	ip addr show | grep "inet" | grep -v "127.0.0.1"
	echo "Default Route:"
	ip route | grep "default"
	echo "Routing tables:"
        ip route | grep -v "default"
        echo "Listening ports:"
        ss -tulpn |  grep -iE "HTTP/HTTPS"
}	
echo "=========CHECK COMPLETE========="
check_memory
check_disk
check_network
