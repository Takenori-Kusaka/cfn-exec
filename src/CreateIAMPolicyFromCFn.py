import subprocess
import json
import os
import argparse
import glob
import re
import boto3

def load_cfn(filepath: str):
    typename_list = []
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
        pattern = '\w+::\w+::\w+'
        typename_list = re.findall(pattern, content)
    only_typename_list = list(set(typename_list))
    return only_typename_list

def create_IAMPolicy(target_type_list: list):
    result = {
        "Version": "2012-10-17",
        "Statement": []
    }
    client = boto3.client('cloudformation')
    for typename in target_type_list:
        try:
            response = client.describe_type(
                Type='RESOURCE',
                TypeName='AWS::EC2::VPCGatewayAttachment'
            )
            schema = json.loads(response['Schema'])
            handler = schema['handlers']
            actions = []
            for k, v in handler.items():
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
        except:
            continue
    return result

def generate_filepath(basefilepath: str, input_folder: str, output_folder: str):
    idx = basefilepath.find(input_folder)
    r = basefilepath[idx+2:]
    return os.path.join(output_folder, r.replace('.yaml', '.json').replace('.yml', '.json'))

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

def convert_cfn_to_iampolicy(args, filepath: str):
    target_type_list = load_cfn(filepath)
    print(target_type_list)
    iampolicy_dict = create_IAMPolicy(target_type_list)
    print(iampolicy_dict)
    output_filepath = generate_filepath(filepath, args.input_path, args.output_folder)
    print(output_filepath)
    output_IAMPolicy(output_filepath, iampolicy_dict)

def with_input_folder(args):
    if os.path.isdir(args.input_path):
        for filepath in glob.glob(os.path.join(args.input_path + "/**/*.*"), recursive=True):
            convert_cfn_to_iampolicy(args, filepath)
        master_policy = create_master_policy(args.output_folder)
        print(master_policy)
    else:
        convert_cfn_to_iampolicy(args, args.input_path)

def with_input_list(args):
    iampolicy_dict = create_IAMPolicy(args.input_list.split(','))
    print(iampolicy_dict)
    output_IAMPolicy(os.path.join(args.output_folder, 'IAMPolicy.json'), iampolicy_dict)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input-path",
        type=str,
        action="store",
        help="Cloudformation file or Folder path having Cloudformation files. Supported yaml and json. If this path is a folder, it will be detected recursively.",
        dest="input_path"
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
        type=str,
        action="store",
        dest="output_folder",
        help="Output IAM policy files root folder.If not specified, it matches the input-path. Moreover, if input-path is not specified, it will be output to the current directory."
    )
    args = parser.parse_args()

    if args.input_path == None and args.input_list == None:
        raise argparse.ArgumentError("Missing input filename and list. Either is required.")
    elif args.input_path != None and args.input_list != None:
        raise argparse.ArgumentError("Conflicting input filename and list. Do only one.")

    if args.output_folder == None:
        if args.input_path != None:
            basename = os.path.basename(args.input_path)
            args.output_folder = args.input_path.replace(basename, "")
        else:
            args.output_folder = './'
    
    print('Start to create IAM Policy file')
    if args.input_path != None:
        with_input_folder(args)
    else:
        with_input_list(args)
    print('Successfully to create IAM Policy files')

if __name__ == "__main__":
    # execute only if run as a script
    main()
