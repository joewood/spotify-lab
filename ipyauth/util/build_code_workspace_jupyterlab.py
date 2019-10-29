
import os
import json
import subprocess as sp


cmd = "jupyter lab paths"
p = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
out = p.communicate()[0]

output_cmd = [e.strip() for e in out.decode('utf-8').split('\n')]
output_cmd = [e for e in output_cmd if e != '']

paths = [{'path': '.'}]
categories = ['application', 'user-settings', 'workspaces']
for k, line in enumerate(output_cmd):
    cat = categories[k]
    print (line)
    if ':' in line:
        path = line.split(':')[1].strip()
    else:
        path = line.split(' ')[1]
    dic = {
        'name': cat,
        'path': path,
    }
    paths.append(dic)

content = json.dumps({'folders': paths,
                      'settings': {}},
                     indent=4)

print(content)

root_repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(root_repo,
                    'ipyauth-ext-folders-jupyterlab.code-workspace')
with open(path, 'w') as f:
    f.write(content)

abs_path = os.path.abspath(path)
print('\nfile saved on disk: {}'.format(abs_path))
