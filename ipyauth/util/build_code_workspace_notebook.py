
import os
import json
import subprocess as sp


cmd = "jupyter --paths"
p = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
out = p.communicate()[0]

output_cmd = [e.strip() for e in out.decode('utf-8').split('\n')]
output_cmd = [e for e in output_cmd if e != '']

paths = [{'path': '.'}]
scopes = ['--user', '--sys-prefix', '--system', 'default']
for k, e in enumerate(output_cmd):
    if e.endswith(':'):
        cat = e.split(':')[0]
        i = -1
    else:
        i += 1
        if cat in ['config', 'data']:
            dic = {
                'name': cat + ' ' + scopes[i],
                'path': e,
            }
            paths.append(dic)
        if cat in ['runtime']:
            dic = {
                'name': cat,
                'path': e,
            }
            # paths.append(dic)

content = json.dumps({'folders': paths,
                      'settings': {}},
                     indent=4)

print(content)

root_repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(root_repo,
                    'ipyauth-ext-folders-notebook.code-workspace')
with open(path, 'w') as f:
    f.write(content)

abs_path = os.path.abspath(path)
print('\nfile saved on disk: {}'.format(abs_path))
