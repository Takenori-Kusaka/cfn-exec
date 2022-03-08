"""This is a cfn-giam main program."""
import argparse

def main():
    """cfn-giam main"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input-path",
        type=str,
        action="store",
        help="Cloudformation file, folder or url path having Cloudformation files. \
            Supported yaml and json. If this path is a folder, it will be detected recursively.",
        dest="input_path"
    )
    parser.add_argument(
        "-l", "--input-resource-type-list",
        type=str,
        action="store",
        help="AWS Resouce type name list of comma-separated strings. e.g. \
            \"AWS::IAM::Role,AWS::VPC::EC2\"",
        dest="input_list"
    )
    parser.add_argument(
        "-o", "--output-folderpath",
        type=str,
        action="store",
        dest="output_folder",
        help="Output IAM policy files root folder.If not specified, it matches the input-path. \
            Moreover, if input-path is not specified, it will be output to the current directory."
    )
    parser.add_argument(
        "-p", "--policy",
        type=str,
        action="store",
        dest="policy",
        help="Create IAM Policy on your AWS. If empty, the name will be automatically generated based on the input contents."
    )
    parser.add_argument(
        "-r", "--role",
        type=str,
        action="store",
        dest="role",
        help="Create IAM Role on your AWS. If empty, the name will be automatically generated based on the input contents."
    )
    parser.add_argument(
        "-V", "--verbose",
        action='store_true',
        dest="detail",
        help="give more detailed output"
    )
    args = parser.parse_args()
    print(args.policy)
    print(args.role)

if __name__ == "__main__":
    # execute only if run as a script
    main()
