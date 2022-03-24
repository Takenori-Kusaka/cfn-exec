"""This is a cfn-exec main program."""
import logging
import resource
logger = logging.getLogger(__name__)

try:
    import requests
    import json
    import os
    import argparse
    import re
    import boto3
    from pathlib import Path
    import uuid
    import glob
    try:
        from cfnexec import version
    except:
        import version
    import yaml
    import traceback
    from awscli.customizations.cloudformation.yamlhelper import yaml_parse
    from tabulate import tabulate
except Exception as e:
    logger.error(e)


def isUrl(path: str):
    pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    result = ''
    if re.match(pattern, path):
        return True
    else:
        return False

def read_s3_file(url: str):
    s3 = boto3.resource('s3')
    url_sp = url.split('/')
    domain_sp = url_sp[2].split('.')
    bucket = s3.Bucket(domain_sp[0])
    obj  = bucket.Object('/'.join(url_sp[3:]))
    response = obj.get()    
    body = response['Body'].read()

    return body.decode('utf-8')

def create_s3():
    bucket_name = 'cfn-exec-' + boto3.session.Session().region_name + '-' + str(uuid.uuid4())
    logger.debug('Create s3 bucket: ' + bucket_name)
    s3 = boto3.resource('s3', region_name=boto3.session.Session().region_name)
    bucket = s3.Bucket(bucket_name)
    bucket.create(CreateBucketConfiguration={'LocationConstraint': boto3.session.Session().region_name})
    return bucket_name

def upload_file_to_s3(bucket_name: str, filepath_list: list, root_path: str):
    s3 = boto3.resource('s3', region_name=boto3.session.Session().region_name)
    root_path_str = str(Path(root_path).resolve())
    for f in filepath_list:
        logger.debug('Upload s3 bucket: ' + f)
        f_str = str(Path(f).resolve())
        s3.Object(bucket_name, f_str.replace(root_path_str, '')[1:]).upload_file(f)

def get_public_url(bucket, target_object_path):
    s3 = boto3.client('s3', region_name=boto3.session.Session().region_name)
    bucket_location = s3.get_bucket_location(Bucket=bucket)
    return "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location['LocationConstraint'],
        bucket,
        target_object_path)

def delete_bucket(bucket_name, dryrun=False):
    contents_count = 0
    next_token = ''
    client = boto3.client('s3')

    while True:
        if next_token == '':
            response = client.list_objects_v2(Bucket=bucket_name)
        else:
            response = client.list_objects_v2(Bucket=bucket_name, ContinuationToken=next_token)

        if 'Contents' in response:
            contents = response['Contents']
            contents_count = contents_count + len(contents)
            for content in contents:
                if not dryrun:
                    logger.debug("Deleting: s3://" + bucket_name + "/" + content['Key'])
                    client.delete_object(Bucket=bucket_name, Key=content['Key'])
                else:
                    logger.debug("DryRun: s3://" + bucket_name + "/" + content['Key'])

        if 'NextContinuationToken' in response:
            next_token = response['NextContinuationToken']
        else:
            break
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.delete()


def find_cfn_files(base_folder_path: str):
    filepath_list = []
    filepath_list.extend(list(glob.glob(os.path.join(base_folder_path + "/**/*.json"), recursive=True)))
    filepath_list.extend(list(glob.glob(os.path.join(base_folder_path + "/**/*.yml"), recursive=True)))
    filepath_list.extend(list(glob.glob(os.path.join(base_folder_path + "/**/*.yaml"), recursive=True)))
    filepath_list.extend(list(glob.glob(os.path.join(base_folder_path + "/**/*.template"), recursive=True)))
    return filepath_list

def upload_cfn(input_path: str):
    
    bucket_name = create_s3()
    filepath_list = find_cfn_files(str(Path(input_path).parent))
    upload_file_to_s3(bucket_name, filepath_list, str(Path(input_path).parent))
    return get_public_url(bucket_name, Path(input_path).name), bucket_name


def load_parameter_file(param_path: str):
    root, ext = os.path.splitext(param_path)
    content = ''
    if isUrl(param_path):
        if 's3.' in param_path and '.amazonaws.com' in param_path:
            content = read_s3_file(param_path)
        else:
            res = requests.get(param_path)
            content = res.text
    else:
        with open(param_path, encoding='utf-8') as f:
            content = f.read()
    if ext == '.json':
        result = json.loads(content)
    else:
        result = yaml.safe_load(content)
    return result

def generate_parameter(param_path: str, s3_bucket_url_parameter_key_name: str, bucket_name: str):
    param = load_parameter_file(param_path)

    result = []
    if isinstance(param, list):
        if len(list(filter(lambda p: 'ParameterKey' in p and 'ParameterValue' in p, param))) == len(param):
            result = param
        else:
            raise('Not support parameter file')
    elif isinstance(param, dict):
        result = []
        for k, v in param.items():
            if isinstance(v, dict) or isinstance(v, list):
                raise('Not support parameter file')
            result.append({
                'ParameterKey': k,
                'ParameterValue': v
            })
    else:
        raise('Not support parameter file')
    if s3_bucket_url_parameter_key_name != None:
        for r in list(filter(lambda p: p['ParameterKey'] == s3_bucket_url_parameter_key_name, result)):
            r['ParameterValue'] = 'https://{}.s3.amazonaws.com'.format(bucket_name)
    return result

def view_resources(resources: list):
    result = ''
    success = True
    headers=["Index", "Timestamp", "ResourceStatus", "LogicalResourceId", "PhysicalResourceId", "ResourceStatusReason"]
    d = []
    i = 0
    for r in resources:
        t = []
        t.append(str(i))
        t.append(r['Timestamp'])
        t.append(r['ResourceStatus'])
        t.append(r['LogicalResourceId'])
        t.append(r['PhysicalResourceId'])
        t.append(r['ResourceStatusReason'] if 'ResourceStatusReason' in r else '')
        d.append(t)
        if r['ResourceStatus'] != "CREATE_COMPLETE" and r['ResourceStatus'] != "UPDATE_COMPLETE" and r['ResourceStatus'] != "IMPORT_COMPLETE":
            success = False
        i = i + 1
    result = '\n' + str(tabulate(d, headers=headers)) + '\n'
    logger.info(result)
    return success

def get_resouces(stack_name: str):
    result = []
    client = boto3.client('cloudformation')
    response = client.describe_stack_resources(
        StackName=stack_name
    )
    for r in response['StackResources']:
        if "arn:aws:cloudformation" in r['PhysicalResourceId']:
            result.extend(get_resouces(r['PhysicalResourceId']))
        else:
            result.append(r)
    return result    

def create_stack(stack_name: str, cfn_url: str, param_list: list,
                disable_rollback: bool,
                delete_stack: bool,
                role_arn: str
    ):
    client = boto3.client('cloudformation')
    logger.info("Create a new {}.".format(stack_name))
    if role_arn != None:
        response = client.create_stack(
            StackName=stack_name,
            TemplateURL=cfn_url,
            Parameters=param_list,
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_NAMED_IAM',
                'CAPABILITY_AUTO_EXPAND'
            ],
            DisableRollback=disable_rollback,
            RoleARN=role_arn
        )
    else:
        response = client.create_stack(
            StackName=stack_name,
            TemplateURL=cfn_url,
            Parameters=param_list,
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_NAMED_IAM',
                'CAPABILITY_AUTO_EXPAND'
            ],
            DisableRollback=disable_rollback
        )
    stack_id = response['StackId']
    logger.info("Creating to stack... : " + stack_name)
    try:
        waiter = client.get_waiter('stack_create_complete')
        waiter.wait(StackName=stack_name) # スタック完了まで待つ
        resources = get_resouces(stack_name)
    except Exception as e:
        logger.warning(e)
    if view_resources(resources):
        logger.info("Creation to stack completed successfully!! : {}".format(stack_name))
    else:
        logger.info("Attempted to create but failed... : {}".format(stack_name))
    if delete_stack:
        if role_arn != None:
            response = client.delete_stack(
                StackName=stack_name,
                RoleARN=role_arn
            )
        else:
            response = client.delete_stack(
                StackName=stack_name
            )
        logger.info("Deleting to stack... : " + stack_name)
        waiter = client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name)
        logger.info("Deletion to stack completed. : {}".format(stack_name))
    return stack_id

def view_changes(change: list):
    result = ''
    headers=["Index", "Type", "Action", "LogicalResourceId", "PhysicalResourceId", "ResourceType", "Replacement"]
    d = []
    i = 0
    for c in change:
        t = []
        t.append(str(i))
        t.append(c['Type'])
        t.append(c['ResourceChange']['Action'])
        t.append(c['ResourceChange']['LogicalResourceId'])
        t.append(c['ResourceChange']['PhysicalResourceId'])
        t.append(c['ResourceChange']['ResourceType'])
        t.append(c['ResourceChange']['Replacement'])
        d.append(t)
        i = i + 1
    result = '\n' + str(tabulate(d, headers=headers)) + '\n'
    logger.info(result)

def get_changes(stack_name: str, change_set_name: str):
    result = []
    client = boto3.client('cloudformation')
    response = client.describe_change_set(
        ChangeSetName=change_set_name,
        StackName=stack_name
    )
    for r in response['Changes']:
        if "arn:aws:cloudformation" in r['ResourceChange']['PhysicalResourceId']:
            result.extend(get_changes(r['ResourceChange']['PhysicalResourceId'], r['ResourceChange']['ChangeSetId']))
        else:
            result.append(r)
    return result 

def create_change_set(stack_name: str, cfn_url: str, param_list: list,
                role_arn: str,
                change_set_force_deploy: bool
    ):
    client = boto3.client('cloudformation')
    logger.info("Since {} already exists, create new change set.".format(stack_name))
    change_set_name = stack_name + str(uuid.uuid4())
    if role_arn != None:
        response = client.create_change_set(
            StackName=stack_name,
            TemplateURL=cfn_url,
            UsePreviousTemplate=False,
            Parameters=param_list,
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_NAMED_IAM',
                'CAPABILITY_AUTO_EXPAND'
            ],
            RoleARN=role_arn,
            ChangeSetName=change_set_name,
            IncludeNestedStacks=True
        )
    else:
        response = client.create_change_set(
            StackName=stack_name,
            TemplateURL=cfn_url,
            UsePreviousTemplate=False,
            Parameters=param_list,
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_NAMED_IAM',
                'CAPABILITY_AUTO_EXPAND'
            ],
            ChangeSetName=change_set_name,
            IncludeNestedStacks=True
        )
    stack_id = response['StackId']
    logger.info("Creating to change set... : " + change_set_name)
    try:
        waiter = client.get_waiter('change_set_create_complete')
        waiter.wait(
            ChangeSetName=change_set_name,
            StackName=stack_name
        )
        logger.info("Creation to change set completed successfully!! : {}".format(change_set_name))
    except Exception as e:
        logger.warning(e)
        
    response = client.describe_change_set(
        ChangeSetName=change_set_name,
        StackName=stack_name
    )
    if response['Status'] == 'CREATE_COMPLETE':
        logger.info("Creation to change set completed successfully!! : {}".format(change_set_name))
        if 'StatusReason' in response:
            logger.info('Reason: ' + response['StatusReason'])
        changes = get_changes(stack_name, change_set_name)
        if len(changes) == 0:
            logger.info("Nothing differents from the current.")
        else:
            view_changes(changes)
            if change_set_force_deploy:
                logger.info("Execute to change set: " + change_set_name)
                response = client.execute_change_set(
                    ChangeSetName=change_set_name,
                    StackName=stack_name
                )
                logger.info("Executing change set...")
                waiter = client.get_waiter('stack_update_complete')
                waiter.wait(
                    StackName=stack_name
                )
                logger.info("Execution to change set completed successfully!! : {}".format(change_set_name))
    else:
        logger.info("Attempted to create but failed... : {}".format(change_set_name))
        if 'StatusReason' in response:
            logger.info('Reason: ' + response['StatusReason'])
    return stack_id

def view_param(param_list: list):
    result = ''
    headers=["Index", "ParameterKey", "ParameterValue"]
    d = []
    i = 0
    for p in param_list:
        t = []
        t.append(str(i))
        t.append(p['ParameterKey'])
        t.append(p['ParameterValue'])
        d.append(t)
        i = i + 1
    result = '\n' + str(tabulate(d, headers=headers)) + '\n'
    logger.info(result)

def request_stack(stack_name: str, cfn_url: str, param_list: list,
                disable_rollback: bool,
                delete_stack: bool,
                role_arn: str,
                change_set_force_deploy: bool
    ):
    client = boto3.client('cloudformation')
    logger.info('StackName: ' + stack_name)
    logger.info('CFn URL: ' + cfn_url)
    logger.info('Parameters: ')
    view_param(param_list)
    
    stack_id = ''

    response = client.validate_template(
        TemplateURL=cfn_url
    )
    
    stack_exists = False
    try:
        response = client.describe_stacks(
            StackName=stack_name
        )
        if len(response['Stacks']) > 0:
            stack_exists = True
    except Exception as e:
        logger.debug(e)
        pass
    if not stack_exists:
        stack_id = create_stack(stack_name, cfn_url, param_list, disable_rollback, delete_stack, role_arn)
    else:
        stack_id = create_change_set(stack_name, cfn_url, param_list, role_arn, change_set_force_deploy)
        
    return stack_id

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
        "--role-arn",
        type=str,
        action="store",
        dest="role_arn",
        help="The Amazon Resource Name (ARN) of an Identity and Access Management (IAM) role that CloudFormation assumes to create the stack. CloudFormation uses the role's credentials to make calls on your behalf. CloudFormation always uses this role for all future operations on the stack. Provided that users have permission to operate on the stack, CloudFormation uses this role even if the users don't have permission to pass it. Ensure that the role grants least privilege.\nIf you don't specify a value, CloudFormation uses the role that was previously associated with the stack. If no role is available, CloudFormation uses a temporary session that's generated from your user credentials."
    )
    parser.add_argument(
        "-s3", "--s3-bucket-url-parameter-key-name",
        type=str,
        action="store",
        dest="s3_bucket_url_parameter_key_name",
        help="Set the parameter key name to this, if the input path is a local file and you want to reflect the S3 bucket name to be uploaded in the parameter."
    )
    parser.add_argument(
        "-csf", "--change-set-force-deploy",
        action="store_true",
        dest="change_set_force_deploy",
        help="When the target Stack already exists and is to be deployed as a change set, enabling this option will apply the change set to the stack as is."
    )
    parser.add_argument(
        "-dr", "--disable-roleback",
        action="store_true",
        dest="disable_rollback",
        help="Disable rollback on stack creation failure."
    )
    parser.add_argument(
        "-del", "--delete-stack",
        action="store_true",
        dest="delete_stack",
        help="After creating a stack, the stack is deleted regardless of success or failure."
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
        
    logger.debug('Start to create stack')

    bucket_name = ''
    if isUrl(args.input_path):
        cfn_url = args.input_path
    else:
        cfn_url, bucket_name = upload_cfn(args.input_path)
    try:
        param = generate_parameter(args.param, args.s3_bucket_url_parameter_key_name, bucket_name)
        request_stack(args.stack_name, cfn_url, param, args.disable_rollback, args.delete_stack, args.role_arn, args.change_set_force_deploy)
    except Exception as e:
        logger.error(e)
        logger.error('Fail to create or update stack')
    if isUrl(args.input_path):
        pass
    else:
        delete_bucket(bucket_name)

if __name__ == "__main__":
    # execute only if run as a script
    main()
