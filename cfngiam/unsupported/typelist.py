import boto3
import json

client = boto3.client('cloudformation')

typesummaries = []
next_token = ''
response = client.list_types(
    Visibility='PUBLIC',
    Type='RESOURCE',
    MaxResults=100
)
typesummaries.extend(response['TypeSummaries'])
if 'NextToken' not in response:
    pass
else:
    next_token = response['NextToken']
while 'NextToken' in response:
    response = client.list_types(
        Visibility='PUBLIC',
        Type='RESOURCE',
        MaxResults=100,
        NextToken=next_token
    )
    typesummaries.extend(response['TypeSummaries'])
    if 'NextToken' in response:
        break
    else:
        next_token = response['NextToken']
result = []
print('| Not support Resource types |')
print('|----------------------------|')
for types in typesummaries:
    try:
        response = client.describe_type(
            Type='RESOURCE',
            TypeName=types['TypeName']
        )
    except:
        print('Fail to connect aws')
        continue
    try:
        schema = json.loads(response['Schema'])
        if 'handlers' in schema:
            handler = schema['handlers']
            if bool(handler) == False:
                print('| {} |'.format(types['TypeName']))
        else:
            print('| {} |'.format(types['TypeName']))
            result.append(types['TypeName'])
    except:
        print('| {} |'.format(types['TypeName']))
        result.append(types['TypeName'])
