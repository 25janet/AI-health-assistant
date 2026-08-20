#!/bin/bash
echo "==========SYSTEM HEALTH CHECK=========="

echo "Hostname: $(hostname)"
echo "User: $USER"
echo "Date: $(date)"


check_memory() {
	echo "------MEMORY USAGE------"
        mem_total=$(free -m | awk '/Mem:/{print $2}')
        mem_used=$(free -m | awk '/Mem:/{print $3}')
        mem_perc=$((mem_used *100 /mem_total))
        echo "Memory usage: ${mem_perc}%"

        if [ "$mem_perc" -ge 80 ];then
	       echo 'WARNING: Memory usage high!'
        else
	       echo 'Memory status: OK'
        fi
        echo "Total Memory: $(free -m | awk 'NR==2{print $2}') MB"
        echo "Used Memory: $(free -m | awk 'NR==2{print $3}') MB"
        echo "Free Memory: $(free -m | awk 'NR==2{print $4}') MB"
}
check_disk(){
	echo "------DISK USAGE------"
        disk_perc=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
        echo "Disk Usage: ${disk_perc}%"
        if [ "$disk_perc" -ge 80 ];then
	        echo 'WARNING: Disk usage high!'
        else 
	        echo 'Disk Status: OK'
        fi
        echo "Total disk usage: $(df -h --total | awk 'NR==20{print $2}')"
        echo "Used Disk space: $(df -h --total |  awk 'NR==20{print $3}')"
        echo "Available Disk space: $(df -h --total | awk 'NR==20{print $4}')"

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
