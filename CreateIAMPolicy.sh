#!/bin/bash

# Setup
echo "Setup cfn_flip"
pip install cfn_flip
echo "Setup cfn_flip"
pip install cfnlp

# Run
echo "Start to create IAM Policy files"
find . -name "*.yaml" | while read -r fname
do
  echo "Find: $fname"
  cfnlp -i $fname | tee `dirname $fname``basename $fname`-IAMPolicy.json
done

find . -name "*.yml" | while read -r fname
do
  echo "Find: $fname"
  cfnlp -i $fname | tee `dirname $fname``basename $fname`-IAMPolicy.json
done

find . -name "*.json" | while read -r fname
do
  echo "Find: $fname"
  cfnlp -i $fname | tee `dirname $fname``basename $fname`-IAMPolicy.json
done
