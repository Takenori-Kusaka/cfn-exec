#!/bin/bash
aws cloudformation describe-type --type RESOURCE --type-name $1 --query Schema --output text | jq .handlers
