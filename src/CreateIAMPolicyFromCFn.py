import subprocess
import json
import yaml
import sys
import os

filepath = sys.argv[1]
export_folder = sys.argv[2]

cfn_dict = {}
root_ext_pair = os.path.splitext(filepath)
if 'json' in root_ext_pair[1]:
    with open(filepath, encoding="utf-8") as f:
        json_str = f.read()
        cfn_dict = json.loads(json_str)
elif 'yaml' in root_ext_pair[1] or 'yml' in root_ext_pair[1]:
    with open(filepath, encoding="utf-8") as f:
        yml_str = f.read()
        cfn_dict = yaml.full_load(yml_str.replace("!", ""))
print(cfn_dict)

typename_list = []
for k, v in cfn_dict['Resources'].items():
    typename_list.append(v['Type'])
print(typename_list)

only_typename_list = list(set(typename_list))
print(only_typename_list)

result = {
    "Version": "2012-10-17",
    "Statement": []
}
for typename in only_typename_list:
    cmd = "sh ./src/GetSchema.sh " + typename
    print(cmd)
    type_actions = subprocess.run(cmd.split(" "), capture_output=True, text=True).stdout
    print(type_actions)
    type_actions_dict = {}
    type_actions_dict = json.loads(type_actions)
    print(type_actions_dict)
    actions = []
    for k, v in type_actions_dict.items():
        if k == 'create':
            actions.extend(v['permissions'])
        elif k == 'delete':
            actions.extend(v['permissions'])

    statement = {
        "Sid": typename.replace(":", "") + "Access",
        "Effect": "Allow",
        "Action": actions,
        "Resource": "*"
    }
    result['Statement'].append(statement)

basename_without_ext = os.path.splitext(os.path.basename(filepath))[0]
os.makedirs(export_folder, exist_ok=True)
with open(os.path.join(export_folder, basename_without_ext + '.json'), 'w', encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(result)
