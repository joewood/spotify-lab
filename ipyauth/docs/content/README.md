---
home: true
description: 'Authenticate from inside Jupyter notebooks'
heroImage: /jupyter-plus-oauth2.png
heroText: 'ipyauth'
actionText: Get Started →
actionLink: /guide/install
features:
- title: Versatile
  details: Works in all flavors of Jupyter notebooks - Classic and JupyterLab, Desktop and JupyterHub.
- title: Simple
  details: Get an access token in 3 lines - Clear display of the scopes granted and token expiry.
- title: Extensible
  details: Various ID providers are possible - Currently Auth0, Google and SG Connect (Société Générale).
footer: MIT Licensed | Copyright © 2018-present Olivier Borderies
---

### Install

```bash
# for notebook >= 5.3
$ pip install ipyauth

# additionally for jupyterlab
$ jupyter labextension install ipyauth
```

::: warning COMPATIBILITY NOTE
Tested on Chrome and Firefox.
:::
