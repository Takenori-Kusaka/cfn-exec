# AWSPolicyCheckerFromCFn

Automatically extract the required IAM policies from your Cloudformation file

![](img/architecture.drawio.svg)

## Manual procedure

1. Open Cloudhell on your AWS Account
2. Install pyyaml
```sh
pip3 install cpyyaml
```
3. Clone this repository
```sh
git clone https://github.com/Takenori-Kusaka/AWSPolicyCheckerFromCFn.git
cd AWSPolicyCheckerFromCFn
```
4. Check the IAM Policy required to execute the cloudformation file
```sh
python src/CreateIAMPolicyFromCFn.py $yourcfn $exportfolder
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
