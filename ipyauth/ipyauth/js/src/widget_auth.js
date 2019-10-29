import util from './widget_util';
import provider from './widget_id_providers';

const ipyauthStatus = {
    history: [],
    popupIsOpen: false,
    authIsOk: false,
};
window.ipyauthStatus = ipyauthStatus;

const startAuthFlowInIframe = (authUrl, readMessage) => {
    window.addEventListener('message', readMessage);
    const iframe = document.getElementById('auth');
    iframe.src = authUrl;
};

const startAuthFlowInPopup = (authUrl, readMessage, name, windowProps = null) => {
    window.addEventListener('message', readMessage);

    let props = windowProps;
    if (!props) {
        props = {
            menubar: 'yes',
            location: 'no',
            resizable: 'yes',
            scrollbars: 'yes',
            status: 'yes',
            width: '660',
            height: '790',
        };
    }
    props = util.buildWindowProps(props);
    const ref = window.open(authUrl, name, props);
    return ref;
};

function startAuthFlow(that, mode, prompt) {    
    console.log('start startAuthFlow');

    // init
    ipyauthStatus.authIsOk = false;
    const isIframeMode = mode === 'iframe';
    const paramsModel = that.model.get('params');
    const IdProviderName = paramsModel.name;

    console.log(`name=${IdProviderName}, isIframeMode=${isIframeMode}`);
    util.debug('paramsModel', paramsModel);

    // build params
    const paramsTemplate = provider[IdProviderName];
    const paramsFull = Object.assign({}, paramsTemplate, paramsModel);
    const url_params = Object.assign({}, paramsTemplate.url_params, paramsModel.url_params);
    paramsFull.url_params = url_params;
    paramsFull.url_params = util.buildUrlParams(paramsFull, isIframeMode, prompt);
    util.debug('paramsFull', paramsFull);

    // build authorize url
    const authUrl = util.buildAuthorizeUrl(paramsFull);
    util.debug('authUrl', authUrl);

    // build readmessage function
    that.params = paramsFull;
    const readMessage = buidReadMessage(that);

    util.logAuthFlow(ipyauthStatus.history, IdProviderName, mode, prompt);

    if (isIframeMode) {
        util.debug('----------- startAuthFlowInIframe', startAuthFlowInIframe);
        startAuthFlowInIframe(authUrl, readMessage);
    } else {
        util.debug('----------- startAuthFlowInPopup', startAuthFlowInPopup);
        const popupWindowRef = startAuthFlowInPopup(authUrl, readMessage, IdProviderName);
        ipyauthStatus.popupIsOpen = true;
        window.popupWindowRef = popupWindowRef;
    }
}

const buidReadMessage = that => {
    // triggered upon receiving message from callback page
    console.log('start buidReadMessage');

    const { params } = that;

    const readMessage = event => {
        console.log('msg received');

        util.debug('event.data', event.data);

        // extract data from message
        const { data } = event;
        window.data = data;

        util.debug('data', data);
        util.debug('data.state', data.state);

        if (data.statusAuth === undefined) {
            // sso window may send parasite messages
            console.log('invalid data - discarding');
            return;
        }

        // deactivate msg reception
        window.removeEventListener('message', readMessage);

        if (util.isPopup(data.state)) {
            popupWindowRef.close();
            ipyauthStatus.popupIsOpen = false;
        }

        if (data.statusAuth === 'ok') {
            // no error in callback page
            console.log('start callback ok');
            params.isValid(params, data).then(([isValid, creds]) => {
                util.debug('creds', creds);
                if (isValid) {
                    that.creds = creds;
                    // const objCreds = util.buildObjCreds(params, creds);
                    const objCreds = util.buildObjCreds(that);
                    ipyauthStatus.authIsOk = true;
                    updateDisplay(that, objCreds);
                } else {
                    console.log('Error: Callback page params are invalid');
                    alert('ipyauth Error: Invalid Callback - Open console for more info');
                }
            });
        }

        if (data.statusAuth === 'error') {
            // error in callback page
            console.log('start callback error');
            const IdProviderName = util.getIdProviderFromState(data.state);
            const lastLog = util.getLastLog(ipyauthStatus.history, IdProviderName);
            util.debug('lastLog', lastLog);
            if (lastLog) {
                const lastLogWasIframe = lastLog.mode === 'iframe';
                if (lastLogWasIframe) {
                    console.log('Start new auth flow in popup');
                    startAuthFlow(that, 'popup', 'consent');
                } else {
                    console.log('Error: Callback reports 2 errors in a row');
                    alert('ipyauth Error: Authentication Failed - Open console for more info');
                }
            }
        }
    };

    return readMessage;
};

// for now skip iframe step - will revert
const login = that => startAuthFlow(that, 'popup', 'none');

const updateDisplay = (that, objCreds) => {
    console.log('start updateDisplay');
    window.creds = objCreds;

    that.model.set({
        logged_as: objCreds.username,
        expires_at: objCreds.getStrExpiry(),
        scope: objCreds.scope || '',
        access_token: objCreds.getAccessToken(),
        code: objCreds.getCode(),
    });

    that.form.btn_main.model.set_state({ description: 'Clear' });
    that.form.logged_as.model.set({ value: util.toHtml(objCreds.username, 'name') });
    that.form.expires_at.model.set({ value: util.toHtml(objCreds.getStrExpiry(), 'expiry') });
    that.form.btn_inspect.model.set_state({ disabled: false });
    that.form.scope.model.set({
        value: util.toHtml(objCreds.scope, 'scope', objCreds.scope_separator),
    });

    // save state
    that.model.save_changes();

    // countdonw to renew
    startCountdown(that, objCreds);
};

const startCountdown = (that, objCreds) => {
    console.log('start startCountdown');

    let nbSec = objCreds.getSecondsToExp();
    if (nbSec > -1) {
        if (that.timer) {
            clearInterval(that.timer);
        }
        that.timer = setInterval(() => {
            nbSec -= 1;
            if (nbSec >= 0) {
                const time_to_exp = util.toHMS(nbSec);
                that.model.set({ time_to_exp });
                that.form.time_to_exp.model.set({ value: util.toHtml(time_to_exp, 'time-to-exp') });
                // save state
                that.model.save_changes();
            }
            if (nbSec === 0) {
                clear(that);
                login(that);
            }
        }, 1000);
    }
};

const clear = that => {
    console.log('stat clear');

    clearInterval(that.timer);

    that.model.set({
        // _id: '',
        access_token: '',
        logged_as: '',
        time_to_exp: '',
        expires_at: '',
        scope: '',
    });
    that.form.btn_main.model.set_state({ description: 'Sign In' });
    that.form.logged_as.model.set({ value: '' });
    that.form.time_to_exp.model.set({ value: '' });
    that.form.expires_at.model.set({ value: '' });
    that.form.btn_inspect.model.set_state({ disabled: true });
    that.form.scope.model.set({ value: '' });

    // save state
    that.model.save_changes();
};

const { isLogged } = util;

const inspectJwt = token => {
    const url = `https://jwt.io/?token=${token}`;
    util.openInNewTab(url);
};

const inspect = that => {
    const creds = Object.assign({}, that.creds);
    if (creds.id_token) {
        // exception: breaks url encoding
        delete creds.id_token.picture;
    }
    if (that.params.isJWT) {
        inspectJwt(creds.access_token);
        creds.access_token = util.parseJwt(creds.access_token);
    }
    const json = encodeURI(JSON.stringify(creds));
    const url = `https://jsoneditoronline.org/?json=${json}`;
    util.openInNewTab(url);
};

export default {
    login,
    clear,
    isLogged,
    inspect,
};
