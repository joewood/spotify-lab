
# New ID provider

It should be quite easy to add a new ID provider that serves the [OAuth2 implicit grant](https://oauth.net/2/grant-types/implicit/) type.  

However note that most ID providers tend to prefer serving [Authorization code grant](https://oauth.net/2/grant-types/authorization-code/) type only as it is considered more secure since it involves a trusted party, the web server, on the client side.  

To add a new provider:
+ Add an object in the file `ipyauth/js/widget_id_providers.js` with the properties:
    + `name`: name of the ID provider in lowercase
    + `authorize_endpoint`: either exact, as for Google, or a template as for Auth0
    + `scope_separator`: often a space
    + `isJWT`: boolean to indicate if the token is JWT
    + `url_params`: object with the params that must be in the authorize endpoint url
    + `isValid`: a function that return the credentials and a boolean (if they are valid) from the ID provider params and the credentials returned by the authorization server. See the examples.
+ Add a file `_params_[name].py` in `ipyauth/ipyauth_widget` containing a class `Params[Name]`
+ Update the upsteam `__ini__.py` files with the new file and class.
+ Add a logo in the folder `ipyauth/ipyauth_widget/img` with the same dimensions as the others.
+ Update the file `ipyauth/ipyauth_widget/_config.py` with the logo file name.

That should be it.
