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
In that case, Update to [GithubOIDCRole-ReadOnly.yml](./GithubOIDCRole-ReadOnly.yml) after get new thumbprint with [GetGithubOIDCThumbprint.sh](src/GetGithubOIDCThumbprint.sh).
```sh
sh GetGithubOIDCThumbprint.sh
```


