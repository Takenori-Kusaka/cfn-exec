#!/bin/bash

# Setup
pip install pyyaml

# Run
echo "Start to create IAM Policy files"
echo "Export dir: IAMPoliciyFiles"
DIRPATH="./IAMPoliciyFiles/"
mkdir -p $DIRPATH
find ./CFn -name "*.json" | while read -r fname
do
  echo "Find: $fname"
  python src/CreateIAMPolicyFromCFn.py $fname ./IAMPoliciyFiles
done

find ./CFn -name "*.yaml" | while read -r fname
do
  echo "Find: $fname"
  python src/CreateIAMPolicyFromCFn.py $fname ./IAMPoliciyFiles
done

find ./CFn -name "*.yml" | while read -r fname
do
  echo "Find: $fname"
  python src/CreateIAMPolicyFromCFn.py $fname ./IAMPoliciyFiles
done

python src/CreateMasterPolicy.py ./IAMPoliciyFiles
