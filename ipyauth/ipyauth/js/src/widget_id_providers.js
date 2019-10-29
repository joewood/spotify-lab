import axios from 'axios';

import util from './widget_util';

const spotify = {
    name: 'spotify',
    authorize_endpoint: 'https://accounts.spotify.com/authorize',
    url_params: {
        response_type: 'token',
        redirect_uri: 'my-redirect-uri',
        client_id: 'my-client-id',
        scope: 'my-scopes',
        state: 'my-state',
    },
    scope_separator: ' ',
    isJWT: false,
    isValid: (params, creds) => {
        return new Promise((resolve, reject) => {
            // same nonce
            const b = creds.statusAuth === "ok"
            creds.username = "User" // tbd
            creds.expiry = new Date(new Date().getTime() + parseInt(creds.expires_in)*1000)
            creds.scope = params.url_params.scope;
            resolve([b,creds])
        });
    },
};


const sgconnectPRD = {
    name: 'sgconnectPRD',
    authorize_endpoint: 'https://sso.sgmarkets.com/sgconnect/oauth2/authorize',
    url_params: {
        response_type: '',
        redirect_uri: 'my-redirect-url',
        client_id: 'my-client-id',
        scope: 'my-scopes',
        nonce: 'my-nonce',
        state: 'my-state',
        acr_values: 'L2',
    },
    scope_separator: ' ',
    isJWT: false,
    isValid: (params, creds) => {
        const { url_params } = params;
        return new Promise((resolve, reject) => {
            // same nonce
            const b = url_params.nonce === creds.id_token.nonce;
            resolve([b, creds]);
            // set expiry
            const now = new Date();
            creds.expiry = new Date(now.getTime() + creds.expires_in * 1000);
            // set username
            creds.username = creds.id_token.sub;
            resolve([b, creds]);
        });
    },
};

const sgconnectHOM = Object.assign({}, sgconnectPRD);
sgconnectHOM.name = 'sgconnectHOM';
sgconnectHOM.authorize_endpoint = 'https://sgconnect-hom.fr.world.socgen/sgconnect/oauth2/authorize';
sgconnectHOM.acr_values = 'L1';

const auth0 = {
    name: 'auth0',
    authorize_endpoint: 'https://my-domain.[zone].auth0.com/authorize',
    url_params: {
        response_type: '',
        redirect_uri: 'my-redirect-uri',
        client_id: 'my-client-id',
        audience: 'my-audience',
        scope: 'my-scopes',
        nonce: 'mynonce',
        state: 'mystate',
    },
    scope_separator: ' ',
    isJWT: true,
    isValid: (params, creds) => {
        const { url_params } = params;
        return new Promise((resolve, reject) => {
            // same nonce
            util.debug('url_params.nonce', url_params.nonce);
            util.debug('creds.id_token.nonce', creds.id_token.nonce);
            const b = url_params.nonce === creds.id_token.nonce;
            // scope is not returned if all requested granted
            if (!creds.scope) {
                creds.scope = url_params.scope;
            }
            // set username
            creds.username = creds.id_token.nickname;
            // set expiry
            const now = new Date();
            creds.expiry = new Date(now.getTime() + creds.expires_in * 1000);
            // return creds
            resolve([b, creds]);
        });
    },
};

// https://developers.google.com/identity/protocols/OAuth2WebServer#formingtheurl
const google = {
    name: 'google',
    authorize_endpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
    url_params: {
        response_type: '',
        redirect_uri: 'my-redirect-uri',
        client_id: 'my-client-id',
        scope: 'my-scope',
        access_type: 'online',
        state: 'my-state',
        include_granted_scopes: 'false',
    },
    scope_separator: ' ',
    isJWT: false,
    isValid: (params, creds) => {
        const { url_params } = params;
        return new Promise((resolve, reject) => {
            function useEmpty(error) {
                console.log('Response tokeninfo or userinfo: ERROR');
                util.debug('error', error);
                return {};
            }

            const options = [
                {
                    // tokeninfo request
                    method: 'get',
                    url: `https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=${
                        creds.access_token
                    }`,
                    headers: {
                        Accept: 'text/html,application/xhtml+xml,application/xml',
                    },
                },
                {
                    // userinfo request
                    method: 'get',
                    url: `https://www.googleapis.com/oauth2/v3/userinfo?access_token=${
                        creds.access_token
                    }`,
                    headers: {
                        Accept: 'text/html,application/xhtml+xml,application/xml',
                    },
                },
            ];

            axios
                .all([
                    axios.request(options[0]).catch(useEmpty),
                    axios.request(options[1]).catch(useEmpty),
                ])
                .then(
                    axios.spread((resTokenInfo, resUserInfo) => {
                        console.log('Analyze response tokeninfo and userinfo');

                        creds.tokeninfo = resTokenInfo.data;
                        creds.userinfo = resUserInfo.data;

                        if (!creds.tokeninfo) {
                            resolve([false, creds]);
                        }

                        if (!creds.userinfo) {
                            resolve([false, creds]);
                        }

                        // check aud = client_id
                        const b = url_params.client_id === creds.tokeninfo.aud;
                        // collect scope from tokeninfo
                        creds.scope = creds.tokeninfo.scope;
                        // set expiry
                        const now = new Date();
                        creds.expiry = new Date(now.getTime() + creds.expires_in * 1000);
                        // set username
                        creds.username = creds.userinfo.name;
                        resolve([b, creds]);
                    })
                );
        });
    },
};

export default {
    sgconnectPRD,
    sgconnectHOM,
    spotify,
    auth0,
    google,
};
