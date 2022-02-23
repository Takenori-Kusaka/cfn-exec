import subprocess
import json
import sys
import os
import glob

export_folder = sys.argv[1]

result = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudformationFullAccess",
            "Effect": "Allow",
            "Action": [
                "cloudformation:*"
            ],
            "Resource": "*"
        }
    ]
}
for filepath in glob.glob(os.path.join(export_folder + "/**/*.json"), recursive=True):
    policy_dict = {}
    with open(filepath, encoding="utf-8") as f:
        json_str = f.read()
        policy_dict = json.loads(json_str)

    for ps in policy_dict['Statement']:
        exists = False
        for rs in result['Statement']:
            if ps['Sid'] == rs['Sid']:
                exists = True
                break
        if exists == False:
            result['Statement'].append(ps)

with open(os.path.join(export_folder, 'MasterPolicy.json'), 'w', encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(result)
