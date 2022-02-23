# AWSPolicyCheckerFromCFn

Cloudformationファイルから必要なIAMポリシーを自動的に抽出する

![](img/architecture.drawio.svg)

## Dependency

* [cfn_flip](https://github.com/awslabs/aws-cfn-template-flip)
* [cfnlp](https://github.com/iann0036/aws-leastprivilege)

## Manual procedure

1. Open Cloudhell on your AWS Account
2. Install cfn_flip
```sh
pip3 install cfn_flip
```
3. Install cfnlp
```sh
pip3 install cfnlp
```
4. Check the IAM Policy required to execute the cloudformation file
```sh
cfnlp -i file.yml
```

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

aws cloudformation describe-type --type RESOURCE --type-name AWS::IAM::OIDCProvider --query Schema --output text | jq .handlers