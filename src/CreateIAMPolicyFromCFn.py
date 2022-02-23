import subprocess
import json
import yaml
import os
import argparse
import glob

def load_cfn(filepath: str):
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
    return cfn_dict

def extract_resouce_type_name_list(cfn_dict: dict):
    typename_list = []
    for v in cfn_dict['Resources'].values():
        typename_list.append(v['Type'])
    only_typename_list = list(set(typename_list))
    return only_typename_list

def create_IAMPolicy(target_type_list: list):
    result = {
        "Version": "2012-10-17",
        "Statement": []
    }
    for typename in target_type_list:
        cmd = "sh ./src/GetSchema.sh " + typename
        type_actions = subprocess.run(cmd.split(" "), capture_output=True, text=True).stdout
        type_actions_dict = {}
        type_actions_dict = json.loads(type_actions)
        actions = []
        for k, v in type_actions_dict.items():
            if k == 'create':
                actions.extend(v['permissions'])
            if k == 'update':
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
    return result

def generate_filepath(basefilepath: str, input_folder: str, output_folder: str):
    idx = basefilepath.find(input_folder)
    r = basefilepath[idx+len(input_folder):]
    return os.path.join(output_folder, r.replace('yaml', 'json').replace('yml', 'json'))

def output_IAMPolicy(filepath: str, iampolicy_dict: dict):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding="utf-8") as f:
        json.dump(iampolicy_dict, f, indent=2)

def create_master_policy(output_folder: str):
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
    for filepath in glob.glob(os.path.join(output_folder + "/**/*.json"), recursive=True):
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

    with open(os.path.join(output_folder, 'MasterPolicy.json'), 'w', encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result

def with_input_folder(args):
    for filepath in glob.glob(os.path.join(args.input_folder + "/**/*.*"), recursive=True):
        cfn_dict = load_cfn(filepath)
        if bool(cfn_dict) == False:
            continue
        print(cfn_dict)
        target_type_list = extract_resouce_type_name_list(cfn_dict)
        print(target_type_list)
        iampolicy_dict = create_IAMPolicy(target_type_list)
        print(iampolicy_dict)
        output_filepath = generate_filepath(filepath, args.input_folder, args.output_folder)
        print(output_filepath)
        output_IAMPolicy(output_filepath, iampolicy_dict)
    
    master_policy = create_master_policy(args.output_folder)
    print(master_policy)

def with_input_list(args):
    iampolicy_dict = create_IAMPolicy(args.input_list.split(','))
    print(iampolicy_dict)
    output_IAMPolicy(os.path.join(args.output_folder, 'IAMPolicy.json'), iampolicy_dict)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input-folderpath",
        type=str,
        action="store",
        help="Folder path having Json or Yaml Cloudformation files.",
        dest="input_folder"
    )
    parser.add_argument(
        "-l", "--input-resource-type-list",
        type=str,
        action="store",
        help="AWS Resouce type name list of comma-separated strings. e.g. \"AWS::IAM::Role,AWS::VPC::EC2\"",
        dest="input_list"
    )
    parser.add_argument(
        "-o", "--output-folderpath",
        required=True,
        type=str,
        action="store",
        dest="output_folderpath",
        help="Output IAM policy files root folder",
        default="./IAMPolicyFiles"
    )
    args = parser.parse_args()


    if args.input_folder == None and args.input_list == None:
        raise argparse.ArgumentError("Missing input filename and list. Either is required.")
    elif args.input_folder != None and args.input_list != None:
        raise argparse.ArgumentError("Conflicting input filename and list. Do only one.")
    
    print('Start to create IAM Policy file')
    if args.input_folder != None:
        with_input_folder(args)
    else:
        with_input_list(args)
    print('Successfully to create IAM Policy files')

if __name__ == "__main__":
    # execute only if run as a script
    main()
