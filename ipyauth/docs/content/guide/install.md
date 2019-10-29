
# Install


## Classic Notebook

From terminal:

```bash
$ pip install ipyauth

# if notebook<5.3 - but why would you not upgrade ??
$ jupyter nbextension enable --py --sys-prefix ipyauth.ipyauth_widget
$ jupyter serverextension enable --py --sys-prefix ipyauth.ipyauth_callback
```

## JupyterLab

From terminal:

```bash
$ pip install ipyauth
$ jupyter labextension install ipyauth

# if not already installed
$ jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

## Check

If you want to check your install see the [Dev Install - Check Extensions](../dev/dev_install.html#check-extensions) section.

## Uninstall

+ Classic Notebook

```bash
# if notebook<5.3 - but why would you not upgrade ??
$ jupyter serverextension disable --py --sys-prefix ipyauth.ipyauth_callback
$ jupyter nbextension uninstall --py --sys-prefix ipyauth.ipyauth_widget

$ pip uninstall ipyauth
```

+ JupyterLab:

```bash
$ jupyter labextension uninstall ipyauth
$ pip uninstall ipyauth
```
