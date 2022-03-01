# cfn-giam

Automatically generate the required IAM policies from your Cloudformation file

![](img/architecture.drawio.svg)

## Manual procedure

1. Open AWS Cloudshell or any terminal configured with aws cli.
2. Install cfn-giam
```sh
pip3 install cfngiam
```
3. Check the IAM Policy required to execute the cloudformation file or folder
```sh
cfn-giam -i $yourcfn -o $exportfolder
```

### cli options

| CLI option                    | Description                                                                                                                                                                | Require   |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| -i, --input-path              | Cloudformation file, folder or url path having Cloudformation files.   Supported yaml and json. If this path is a folder, it will be detected   recursively.               | yes or -l |
| -l, --input-resouce-type-list | AWS Resouce type name list of comma-separated strings. e.g.   "AWS::IAM::Role,AWS::VPC::EC2"                                                                               | yes or -i |
| -o, --output-folderpath       | Output IAM policy files root folder.If not specified, it matches the   input-path. Moreover, if input-path is not specified, it will be output to   the current directory. | no        |
| -v, --version                 | Show version information and quit.                                                                                                                                         | no        |
| -V, --verbose                 | give more detailed output                                                                                                                                                  | no        |
| --help                        | Show a help synopsis and quit.                                                                                                                                             | no        |

### cli examples

#### **Cloudformation file**
```sh
cfn-giam -i ./CFn/example.yml
```
cfn-giam generates to "./CFn/example.json"

#### **Cloudformation folder**
```sh
cfn-giam -i ./CFn -o ./dist
```
cfn-giam generates to "./dist/CFn/example.json"
cfn-giam generates to "./dist/MasterPolicy.json"

#### **Cloudformation url file**
```sh
cfn-giam -i https://s3.ap-northeast-1.amazonaws.com/cloudformation-templates-ap-northeast-1/Windows_Single_Server_SharePoint_Foundation.template
```
cfn-giam generates to "./Windows_Single_Server_SharePoint_Foundation.json"

#### **Cloudformation resouce type list**
```sh
cfn-giam -l AWS::EC2::Instance,AWS::EC2::SecurityGroup,AWS::EC2::Instance
```
cfn-giam generates to "./Windows_Single_Server_SharePoint_Foundation.json"

## Automatical procedure

### 1. Fork to your Github account from this repository

[Fork a repo](https://docs.github.com/ja/get-started/quickstart/fork-a-repo)

### 2. Create IAM Role and IAM ID Provider for Github Actions

1. Open Cloudformation on your AWS Account.
2. Create stack from [GithubOIDCRole-ReadOnly.yml](./GithubOIDCRole-ReadOnly.yml).
3. Make a note the Roke-Arn created from stack and region's name having stack.

### 3. Register Role-Arn and region name to Github sercrets

1. View Github Actions page on your repository.
2. Register following list to Github secrets.
  * NAME: AWS_REGION, VALUE: your region's name having stack
  * NAME: ROLE_ARN, VALUE: your Roke-Arn created from stack

### 4. Commit and Push your Cloudformation file

1. Add your Cloudformation file in [CFn](./CFn/) folder.
2. Commit and Push your repository.

### 5. Check artifacts on Github Actions

1. View Github Actions page on your repository.
2. Make sure the latest "Check the IAM Policy workflow" is successful.
3. Open the latest workflow.
4. Download artifact on the latest workflow.

## Others

### Github Actions thumbprint

Github Actions thumbprint changes from time to time.  
e.g. [Changelog](https://github.blog/changelog/2022-01-13-github-actions-update-on-oidc-based-deployments-to-aws/)  
In that case, Update to [GithubOIDCRole-ReadOnly.yml](./GithubOIDCRole-ReadOnly.yml) after get new thumbprint with [GetGithubOIDCThumbprint.sh](cfngiam/GetGithubOIDCThumbprint.sh).
```sh
sh GetGithubOIDCThumbprint.sh
```


