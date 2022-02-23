#!/bin/bash

# Setup
echo "Setup cfn_flip"
pip install cfn_flip
echo "Setup cfn_flip"
pip install cfnlp

# Run
echo "Start to create IAM Policy files"
echo "Export dir: IAMPoliciyFiles"
DIRPATH="./IAMPoliciyFiles/"
mkdir -p $DIRPATH
find . -name "./CFn/*.json" | while read -r fname
do
  echo "Find: $fname"
  echo "Export: $DIRPATH`basename $fname`-IAMPolicy.json"
  cfnlp -i $fname | tee $DIRPATH`basename $fname`-IAMPolicy.json
done

find . -name "./CFn/*.yaml" | while read -r fname
do
  echo "Find: $fname"
  echo "Export: $DIRPATH`basename $fname`-IAMPolicy.json"
  cfnlp -i $fname | tee $DIRPATH`basename $fname`-IAMPolicy.json
done

find . -name "./CFn/*.yml" | while read -r fname
do
  echo "Find: $fname"
  echo "Export: $DIRPATH`basename $fname`-IAMPolicy.json"
  cfnlp -i $fname | tee $DIRPATH`basename $fname`-IAMPolicy.json
done
