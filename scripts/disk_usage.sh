#!/bin/bash
echo "Total disk usage: $(df -h --total | awk 'NR==20{print $2}')"
echo "Used Disk space: $(df -h --total |  awk 'NR==20{print $3}')"
echo "Available Disk space: $(df -h --total | awk 'NR==20{print $4}')"

