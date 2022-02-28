import re

pattern = '\d+\.\d+\.\d+'
result = ''
with open('./cfngiam/version.py', encoding='utf-8') as f:
    v_str = f.read()
    preversion = re.search(pattern, v_str).group()
    sp_version = preversion.split('.')
    major = int(sp_version[0])
    miner = int(sp_version[1])
    patch = int(sp_version[2])
    patch = patch + 1
    if patch > 9:
        patch = 0
        miner = miner + 1
    if miner > 9:
        miner = 0
        major = major + 1
    result = v_str.replace(preversion, "{}.{}.{}".format(major, miner, patch))
with open('./cfngiam/version.py', 'w', encoding='utf-8') as f:
    f.write(result)
