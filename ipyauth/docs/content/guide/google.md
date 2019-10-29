---
sidebarDepth: 1
---


# Google

## Overview

To use [Google](https://developers.google.com/identity/) as an authorisation server you need
+ a Google account
+ to create a client id in the Google Console - see [Config](#config) section


## Params

The following params are expected to instantiate a `ParamsGoogle` object. Some or all of these params can be made available in a dotenv file. If params are input via the dotenv file and directly, then the latter prevails. 

The params given below are mapped to the Google authorize endpoint. See the [docs](https://developers.google.com/identity/protocols/OAuth2UserAgent).

### response_type

+ type: `string`

This must be `token` as only the implicit flow is supported.

### client_id

+ type: `string`

The Google clientId field.

### redirect_uri

+ type: `string`

A URI that is listed the Google Console Restrictions / Authorized Redirect URIs section.  
**IMPORTANT**: it must be `host:port/callback/` where `host:port` are your notebook servers'.

### scope

+ type: `string`
+ default: Empty string

A space separated list of requested scopes.

### include_granted_scopes

+ type: `string`
+ value: `true` or `false`
+ default: `false`

Keeps previously obtained scopes.

### dotenv_folder

+ type: `string`
+ default: `.`

The folder in which a `dotenv_file` may be located.

### dotenv_file

+ type: `string`

The dotenv file name, if any, containing some of the authentication params above.



## Config

+ Go to the [API & Services > Credentials](https://console.cloud.google.com/apis/credentials) menu in the Google Cloud Console.
+ Create an **OAuth client ID** of type **Web Application**
+ Configure the **Authorized Redirect URIs** so with http://[your-host]:[your-port] - You can have several
+ Get the clientID

The screen shots below show the relevant Google Cloud console dashboards:
+ the API > Credentials menu

 <img src="../img/google-console-api.png" style="width: 50%; display: block; margin: auto"> 

+ the OAuth Client ID menu

 <img src="../img/google-console-credentials.png" style="width: 90%; display: block; margin: auto"> 

+ the OAuth Client screen

 <img src="../img/google-console-client.png" style="width: 80%; display: block; margin: auto"> 

## Example

There are tons of Google APIs. See the [Google API discover page](https://developers.google.com/apis-explorer).

In this example we will the use the [Drive API](https://developers.google.com/drive/api/v3/reference/) And [Sheet API](https://developers.google.com/sheets/api/reference/rest/) to create a spreadsheet, put data in, update it, and finally share it with other people.  

See the [demo notebook](https://nbviewer.jupyter.org/urls/gitlab.com/oscar6echo/ipyauth/raw/master/notebooks/demo-ipyauth-google.ipynb) for the full example.  

First create a `ipyauth-Google.env` file containing at least the following info:

```bash
# file ./ipyauth-Google-demo.env
client_id=[your-client-id]
scope=https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets
```

If these are not present in this file, they can be passed as direct params to the authentication widget. If they are the direct params will override the dotenv file params.

```python
from ipyauth import ParamsGoogle, Auth

scope = ' '.join(['https://www.googleapis.com/auth/drive', 
                  'https://www.googleapis.com/auth/spreadsheets'])
p = ParamsGoogle(dotenv_file='ipyauth-Google-demo.env', scope=scope)
a = Auth(params=p)
a
```

The authentication takes place in a popup (which you browser must allow).  
You will
+ enter you login/password
+ need to confirm through your mobile if you have 2-factor authentication on
+ grant access to your application the scopes its requests
Then
+ the popup closes
+ the widget displays the auth info and the Python kernel has it too

```python
token = a.access_token

# to see the Auth widget variables
a.show()
```

In case you want to inspect the token, click on the **Inspect** button.

You are now ready to make the API requests. Let us examine the first one, in which you list all files/folders with name "WIP" - which is assumed to exist and be unique - if not create it manually:

```python
# header containing the access token
headers = {
    'Authorization': 'Bearer {}'.format(a.access_token),
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}
# target url
url = 'https://www.googleapis.com/drive/v3/files'
print(url)
# params: filter request
params = {'q': 'name = "WIP"'}
# make request
r = rq.get(url, headers=headers, params=params)

# unpack response
print(r.status_code)
data = json.loads(r.content.decode('utf-8'))
folder_id = data['files'][0]['id']
folder_id
```

For the full sequence, see the [demo notebook](https://nbviewer.jupyter.org/urls/gitlab.com/oscar6echo/ipyauth/raw/master/notebooks/demo-ipyauth-google.ipynb).

