---
sidebarDepth: 1
---


# SG Connect

## Overview

To use **SG Connect** as an authorisation server you need
+ an SG Markets account
+ a client id - contact your SGCIB contact


## Params

The following params are expected to instantiate a `ParamsSgConnect` object. Some or all of these params can be made available in a dotenv file. If params are input via the dotenv file and directly, then the latter prevails. 

The params given below are mapped to the SG Connect authorize endpoint.

### mode

+ type: `string`
+ default `PRD`

This must be `PRD` (production) or `HOM` (homologation aka UAT).

### response_type

+ type: `string`

This must be `token` as only the implicit flow is supported.

### client_id

+ type: `string`

The SG Connect client id field.

### redirect_uri

+ type: `string`

One of the redirect URI associated with the client id.  
**IMPORTANT**: it must be `host:port/callback/` where `host:port` are your notebook servers'.

### scope

+ type: `string`
+ default: `openid` and `profile` are added to the user input.

A space separated list of requested scopes.

### dotenv_folder

+ type: `string`
+ default: `.`

The folder in which a `dotenv_file` may be located.

### dotenv_file

+ type: `string`

The dotenv file name, if any, containing some of the authentication params above.



## Config

In order to get a `client_id`, associated `redirect_uri`, and a list of scopes to request, get in touch with your SGCIB contact.

## Example

See the [demo notebook](https://nbviewer.jupyter.org/urls/gitlab.com/oscar6echo/ipyauth/raw/master/notebooks/demo-ipyauth-sgconnect.ipynb).  

First create a `ipyauth-sgconnectPRD.env` or `ipyauth-sgconnectHOM.env` file (depending on the mode) containing at least the following info:

```bash
# example
# file ./ipyauth-sgconnectPRD-demo.env
client_id=[your-client-id]
scope=scopA scopeB
```

If these are not present in this file, they can be passed as direct params to the authentication widget. If they are the direct params will override the dotenv file params.

```python
from ipyauth import ParamsSgConnect, Auth

scope = 'scopeA scopeB'
p = ParamsSgConnect(mode='PRD',
                    dotenv_file='ipyauth-sgconnect-demo.env',
                    scope=scope)
a = Auth(params=p)
a
```

The authentication takes place in a popup (which you browser must allow).  
You will
+ enter you login/password
Then
+ the popup closes
+ the widget displays the auth info and the Python kernel has it too

```python
token = a.access_token

# to see the Auth widget variables
a.show()
```

In case you want to inspect the token, click on the **Inspect** button.

You are now ready to make the API requests. 

See the [demo notebook](https://nbviewer.jupyter.org/urls/gitlab.com/oscar6echo/ipyauth/raw/master/notebooks/demo-ipyauth-sgconnect.ipynb).

