#!/bin/bash

# Check if the number of arguments is correct
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <service_name>"
    exit 1
fi

service_name="$1"

# Check if the service exists
if kubectl -n sapujagad2 get statefulset "$service_name" &> /dev/null; then
    echo "1"
else
    echo "0"
fi
