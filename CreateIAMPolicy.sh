#!/bin/bash

# Setup
echo "Setup cfn_flip"
pip install cfn_flip
echo "Setup cfn_flip"
pip install cfnlp

# Run
echo "Start to create IAM Policy files"
echo "Export dir: IAMPoliciyFiles"
dirpath = "./IAMPoliciyFiles/"

find . -name "*.json" | while read -r fname
do
  echo "Find: $fname"
  echo "Export: $dirpath`basename $fname`-IAMPolicy.json"
  cfnlp -i $fname | tee $dirpath`basename $fname`-IAMPolicy.json
done

find . -name "*.yaml" | while read -r fname
do
  echo "Find: $fname"
  echo "Export: $dirpath`basename $fname`-IAMPolicy.json"
  cfnlp -i $fname | tee $dirpath`basename $fname`-IAMPolicy.json
done

find . -name "*.yml" | while read -r fname
do
  echo "Find: $fname"
  echo "Export: $dirpath`basename $fname`-IAMPolicy.json"
  cfnlp -i $fname | tee $dirpath`basename $fname`-IAMPolicy.json
done
