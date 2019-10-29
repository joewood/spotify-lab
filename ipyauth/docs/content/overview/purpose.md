# Purpose

### Why ?

The goal of this [ipywidget](https://ipywidgets.readthedocs.io/en/latest/) is to allow a notebook user to authenticate with third party ID providers without storing secrets, like a regular SPA, so as to be able to tap protected APIs.

Indeed Jupyter notebooks are the ideal platform to tap APIs when flexibility is required, as they combine 2 useful capacities:

-   Web page for OAuth2 authentication
-   Python scripting for data manipulation, HTTP requests, postprocessing and visualization

For a more developed case for the **Jupyter notebook as the ultimate "API for Humans" tookit**, read this [article](https://medium.com/@olivier.borderies/oauth2-from-inside-a-jupyter-notebook-5f5e61ec5d38).

### How ?

This library contains a [custom ipywidget](https://blog.jupyter.org/authoring-custom-jupyter-widgets-2884a462e724) and a [notebook server extension](https://jupyter-notebook.readthedocs.io/en/stable/extending/handlers.html#writing-a-notebook-server-extension).

The ipywidget has 2 parts:

-   The Python part: It validates user input and exposes the access token and its characteristics (scopes, expiry date)
-   The Javascript part: It performs the authentication as an SPA does - i.e. via the [OAuth2 implicit grant type](https://oauth.net/2/grant-types/implicit/), without any interaction with the server. The credentials obtained are synchronized to the Python part via the [ipywidget standard mechanism](https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Low%20Level.html#Synchronized-state).

The server extension is a new endpoint `/callback` that is used to receive the redirection from the authentication server. In essence it reads the query string which contains the credentials minted by the authentication server, and passes them to its it parent window.

When the flow starts, the redirection to the authentication server is first attempted in a hidden iframe with `prompt=none` which may provide an access token immediately .If it does not work, either because the authentication server pages refuses to be displayed in an iframe (typically due to a forbidding `X-Frame-Options`) or the authentication server demands a `consent` from the user, then a popup appears to allow the user to type in their credentials, or at least confirm their identify, and grant access to the requested scopes. Subsequently the popup closes and the ipywidget contains the credentials.

This library is designed to be quite generic and easy to extend to various ID providers.

