"""This is a cfn-exec main program."""
import requests
import json
import os
import argparse
import glob
import re
import boto3
import logging
from pathlib import Path
import uuid
from datetime import date, datetime
import numpy as np
from cfngiam import version
import uuid
import yaml

logger = logging.getLogger(__name__)

def generate_cfn(input_path: str):
    pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    result = ''
    if re.match(pattern, input_path):
        result = input_path
    elif os.path.isdir(input_path):
        raise('Not support folder path')
    else:
        result = os.path.join('file//', str(Path(input_path).resolve()))
    return result

def load_parameter_file(param_path: str):
    pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    root, ext = os.path.splitext(param_path)
    content = ''
    if re.match(pattern, param_path):
        content = requests.get(param_path)
    else:
        with open(param_path, encoding='utf-8') as f:
            content = f.read()
    if ext == '.json':
        result = json.loads(content)
    else:
        result = yaml.safe_load(content)
    return result

def generate_parameter(param_path: str):
    param = load_parameter_file(param_path)

    if isinstance(param, list):
        if len(list(filter(lambda p: 'ParameterKey' in p and 'ParameterValue' in p, param))) == len(param):
            return param
    elif isinstance(param, dict):
        result = []
        for k, v in param.items():
            if isinstance(v, dict) or isinstance(v, list):
                raise('Not support parameter file')
            result.append({
                'ParameterKey': k,
                'ParameterValue': v
            })
        return result
    else:
        raise('Not support parameter file')

def create_stack(stack_name: str, cfn_url: str, param_list: list, disable_rollback: bool, role_arn: str):
    client = boto3.client('cloudformation')
    response = client.create_stack(
        StackName=stack_name,
        TemplateURL=cfn_url,
        Parameters=param_list,
        DisableRollback=disable_rollback,
        RoleARN=role_arn
    )
    return response

def main():
    """cfn-exec main"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input-path",
        type=str,
        action="store",
        help="Cloudformation file url path having Cloudformation files. \
            Supported yaml and json. If this path is a folder, it will be detected recursively.",
        dest="input_path"
    )
    parser.add_argument(
        "-n", "--stack-name",
        type=str,
        action="store",
        help="The name that's associated with the stack. The name must be unique in the Region in which you are creating the stack.",
        dest="stack_name"
    )
    parser.add_argument(
        "-p", "--parameter-file",
        type=str,
        action="store",
        dest="param",
        help="Parameter file"
    )
    parser.add_argument(
        "--disable-rollback",
        type=bool,
        action="store",
        default=False,
        dest="disable_rollback",
        help="Set to true to disable rollback of the stack if stack creation failed. You can specify either DisableRollback or OnFailure , but not both."
    )
    parser.add_argument(
        "--role-arn",
        type=str,
        action="store",
        dest="role_arn",
        help="The Amazon Resource Name (ARN) of an Identity and Access Management (IAM) role that CloudFormation assumes to create the stack. CloudFormation uses the role's credentials to make calls on your behalf. CloudFormation always uses this role for all future operations on the stack. Provided that users have permission to operate on the stack, CloudFormation uses this role even if the users don't have permission to pass it. Ensure that the role grants least privilege.\nIf you don't specify a value, CloudFormation uses the role that was previously associated with the stack. If no role is available, CloudFormation uses a temporary session that's generated from your user credentials."
    )
    parser.add_argument(
        "-v", "--version",
        action='version',
        version=version.__version__,
        help="Show version information and quit."
    )
    parser.add_argument(
        "-V", "--verbose",
        action='store_true',
        dest="detail",
        help="give more detailed output"
    )
    args = parser.parse_args()

    if args.detail:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        logger.info('Set detail log level.')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    logger.info('Start to create stack')

    cfn = generate_cfn(args.input_path)
    param = generate_parameter(args.param)
    stack = create_stack(args.stack_name, cfn, param, args.disable_rollback)

    logger.info('Successfully to create stack: ' + stack['StackId'])

if __name__ == "__main__":
    # execute only if run as a script
    main()
