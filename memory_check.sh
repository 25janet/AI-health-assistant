#!/bin/bash
echo "Total Memory: $(free -m | awk 'NR==2{print $2}') MB"
echo "Used Memory: $(free -m | awk 'NR==2{print $3}') MB"
echo "Free Memory: $(free -m | awk 'NR==2{print $4}') MB"
