

# Dev Install

This section is intentionally verbose in order to help ipywidget developer, in the Classic notebook as well as JupyterLab.  
For more info about authoring Jupyter custom ipywidgets, see this [article](https://blog.jupyter.org/authoring-custom-jupyter-widgets-2884a462e724).

## Setup

Download the source:

```bash
$ git clone https://gitlab.com/oscar6echo/ipyauth
cd ipyauth
````

It is tidier hence recommended to work in an isolated environment.  
Create a dedicated environment:

```bash
# create conda env
$ conda create -n dev-ipyauth python=3
# activate env (without source for Windows)
$ source activate dev-ipyauth
# install dependencies
(dev-ipyauth) $ pip install notebook
(dev-ipyauth) $ pip install -r requirements.txt
```

Additionally for JupyterLab:

```bash
# node from conda forge for a compatible version
(dev-ipyauth) $ conda install jupyterlab nodejs -c conda-forge
```

The commands below are assumed to run from this `dev-ipyauth` environment.


## Folders

It is instructing to keep an eye on configuration folders to follow what the install modifies in the file system.

### Classic Notebook

```bash
# list jupyter folders
$ jupyter --paths
# you should see something like:
config:
    /Users/Olivier/.jupyter                              # user
    /usr/local/anaconda3/envs/dev-ipyauth/etc/jupyter    # sys-prefix
    /usr/local/etc/jupyter                               # system
    /etc/jupyter                                         # default
data:
    /Users/Olivier/Library/Jupyter                       # user
    /usr/local/anaconda3/envs/dev-ipyauth/share/jupyter  # sys-prefix
    /usr/local/share/jupyter                             # system
    /usr/share/jupyter                                   # default
runtime:
    /Users/Olivier/Library/Jupyter/runtime
```

### JupyterLab


```bash
# list jupyterlab folders
$ jupyter lab path
# you should see something like:
Application directory:   /usr/local/anaconda3/share/jupyter/lab
User Settings directory: /Users/Olivier/.jupyter/lab/user-settings
Workspaces directory /Users/Olivier/.jupyter/lab/workspaces
```

### VS Code

If you use [Visual Studio Code](https://code.visualstudio.com/) you can build a workspace for all these folders and open it.

+ Classic Notebook:

```bash
# build .code-workspace file
$ python util/build_code_workspace_notebook.py
$ code ipyauth-ext-folders-notebook.code-workspace
```

+ JupyterLab:

```bash
# build .code-workspace file
$ python util/build_code_workspace_jupyterlab.py
$ code ipyauth-ext-folders-jupyterlab.code-workspace
```

## Javascript

Start by building the Javascript modules.  
Build the Javascript part of the ipywidget:

```bash
# from repo top folder

# build ipywidget js
$ cd ipyauth/js
$ npm install

# (optional) auto rebuild js/ upon change - run in new terminal
$ npm run watch
```

## Python


Install the Python package in [dev mode](https://packaging.python.org/tutorials/installing-packages/#installing-from-a-local-src-tree).

```bash
# install Python package
cd ../../..
$ pip install -e .
```


## Extensions

### Server

Install the server extension:

```bash
$ jupyter serverextension enable --py --sys-prefix ipyauth.ipyauth_callback
# you should see something like:
Enabling: ipyauth.ipyauth_callback.server_extension
- Writing config: /usr/local/anaconda3/envs/dev-ipyauth/etc/jupyter
    - Validating...
      ipyauth.ipyauth_callback.server_extension  OK
```


### Notebook

Install the notebook extension:

```bash
$ jupyter nbextension install --py --symlink --sys-prefix ipyauth.ipyauth_widget
# if the target files already exist it will fail: remove them manually
# you should see something like:
Installing /Users/Olivier/Documents/dev/ipyauth-repo/ipyauth/ipyauth_widget/static -> ipyauth
Symlinking: /usr/local/anaconda3/envs/dev-ipyauth/share/jupyter/nbextensions/ipyauth -> /Users/Olivier/Documents/dev/ipyauth-repo/ipyauth/ipyauth_widget/static
- Validating: OK

    To initialize this nbextension in the browser every time the notebook (or other app) loads:

          jupyter nbextension enable ipyauth.ipyauth_widget --py --sys-prefix
```

Enable the notebook extension:

```bash
$ jupyter nbextension enable --py --sys-prefix ipyauth.ipyauth_widget
# you should see something like:
Enabling notebook extension ipyauth/extension...
      - Validating: OK
```


### Lab

Install the JupyterLab extension:

```bash
$ jupyter labextension link ipyauth/js --no-build

# you also must have installed ipywidgets in jupyterlab:
# $ jupyter labextension install @jupyter-widgets/jupyterlab-manager
```


## Check Extensions

### Server

Check the server extension:

```bash
# server extensions status
$ jupyter serverextension list
# for the sys-prefix config folder you should see at least:
config dir: /usr/local/anaconda3/envs/dev-ipyauth/etc/jupyter
    ipyauth.ipyauth_callback.server_extension  enabled 
    - Validating...
      ipyauth.ipyauth_callback.server_extension  OK
```

Open the server extension config file:

```bash
$ cat /usr/local/anaconda3/envs/dev-ipyauth/etc/jupyter/jupyter_notebook_config.json
# you should see at least something like:
{
  "NotebookApp": {
    "nbserver_extensions": {
      "ipyauth.ipyauth_callback.server_extension": true
    }
  }
}
```

### Notebook

Check the notebook extension:

```bash
# notebook extensions status
$ jupyter nbextension list
# for the sys-prefix config folder you should see at least:
Known nbextensions:
  config dir: /usr/local/anaconda3/envs/dev-ipyauth/etc/jupyter/nbconfig
    notebook section
      jupyter-js-widgets/extension  enabled 
      - Validating: OK
      ipyauth/extension  enabled 
      - Validating: OK
```

Open the notebook extension config file:

```bash
$ cat /usr/local/anaconda3/envs/dev-ipyauth/etc/jupyter/nbconfig/notebook.json
# you should see at least something like:
{
  "load_extensions": {
    "jupyter-js-widgets/extension": true,
    "ipyauth/extension": true
  }
}
```

Finally the nbextensions data folder should contain symlinks to the ipyauth static/ folder:

```bash
# (if necessary: brew install tree)
$ tree /usr/local/anaconda3/envs/dev-ipyauth/share/jupyter/nbextensions
# you should see at least:
/usr/local/anaconda3/envs/dev-ipyauth/share/jupyter/nbextensions
├── ipyauth -> /Users/Olivier/Documents/dev/ipyauth-repo/ipyauth/ipyauth_widget/static
└── jupyter-js-widgets
    ├── extension.js
    └── extension.js.map
```

### Lab

Check JupyterLab extensions:

```bash
# jupyterlab extensions status
$ jupyter labextension list
# you should see at least:
JupyterLab v0.32.1
Known labextensions:
   app dir: /usr/local/anaconda3/envs/dev-ipyauth/share/jupyter/lab
@jupyter-widgets/jupyterlab-manager
        @jupyter-widgets/jupyterlab-manager v0.35.0  enabled  OK
ipyauth
        ipyauth v0.1.0-beta.1  enabled  OK
```

## Run

Move the the notebooks folder and launch the notebook server:

```bash
# from repo top folder
$ cd notebooks

# launch notebook server and open browser to the classic file system
$ jupyter notebook

# launch notebook server and open browser jupyterlab
$ jupyter lab --watch # auto rebuild
```

Then open a demo notebook.


## Uninstall


Proceed in the install reverse order.  

1. Remove the frontend extension:

For the classic notebook remove the notebook extension:

```bash
$ jupyter nbextension uninstall --py --sys-prefix ipyauth.ipyauth_widget
```

For the classic notebook remove the notebook extension:

```bash
$ jupyter labextension unlink ipyauth/js
```


2. Remove the server extension:

```bash
$ jupyter serverextension disable --py --sys-prefix ipyauth.ipyauth_callback
```

3. Uninstall the Python package:

```bash
$ pip uninstall ipyauth
```

