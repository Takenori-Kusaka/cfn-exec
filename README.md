# cfn-exec

This is Wrapper tool for aws cloudformation create stack.

## Installation

1. Open AWS Cloudshell or any terminal configured with aws cli.
2. Install cfn-exec
```sh
pip3 install cfnexec
```
3. Create stack with CFn file or url and parameter file or url
```sh
cfn-exec -n $your_stack_name -i $your_cfn_url -p $your_cfn_parameter_url 
```
note: If you are using the nested call function of Cloudformation, you need to make the called file accessible in advance.

### cli options

**TBD**

### parameter file format

Support "Cloudformation official format" or "Simple format"
**Cloudformation official format**
```json
[
  {
    "ParameterKey": "ParameterKeyName1",
    "ParameterValue": "ParameterValue1"
  },
  {
    "ParameterKey": "ParameterKeyName2",
    "ParameterValue": "ParameterValue2"
  },
  ...
],
```
```yaml
---
- ParameterKey: ParameterKeyName1
  ParameterValue: ParameterValue1
- ParameterKey: ParameterKeyName2
  ParameterValue: ParameterValue2
  ...
```
**Simple format**
```json
{
  "ParameterKeyName1": "ParameterValue1",
  "ParameterKeyName2": "ParameterValue2",
  ...
}
```
```yaml
---
ParameterKeyName1: ParameterValue1
ParameterKeyName2: ParameterValue2
...
```
