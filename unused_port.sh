#!/bin/bash

# Define the range of NodePort values you want to consider
PORT_RANGE_START=30000
PORT_RANGE_END=32767

# Get the currently used NodePort values
used_ports=$(kubectl get svc --all-namespaces -o jsonpath='{.items[*].spec.ports[*].nodePort}' | tr ' ' '\n' | sort -n)

# Find the minimum unused port within the specified range
unused_port=$PORT_RANGE_START
for port in $used_ports; do
    if [ "$port" -eq "$unused_port" ]; then
        ((unused_port++))
    else
        break
    fi
done

echo "$unused_port"
