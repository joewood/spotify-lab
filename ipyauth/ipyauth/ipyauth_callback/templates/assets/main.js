console.log('start callback');

// extract urlData
const urlData = getDataFromCallbackUrl();
debug('urlData', urlData);
window.urlData = urlData;

// build id_token: JWT by openid spec
let id_token;
if (urlData.id_token) {
    id_token = parseJwt(urlData.id_token);
    urlData.id_token = id_token;
}
debug('id_token', id_token);

debug('urlData', urlData);
window.urlData = urlData;

// check if urlData means an authentication error
if (containsError(urlData)) {
    // error in authentication
    console.log('error in urlData');

    // display
    display('Authentication failed.', 'msg', true);
    display('urlData:', 'msg');
    display(JSON.stringify(urlData), 'msg');

    // build message
    objMsg = Object.assign({ statusAuth: 'error' }, urlData);
} else {
    // no error
    console.log('No error in urlData');

    // get access_token and code
    const access_token = urlData.access_token || null;
    const code = urlData.code || null;
    debug('access_token', access_token);
    debug('code', code);

    // display
    display('Authentication completed.', 'msg');
    display(`The access_token is ${access_token}`, 'msg', true);
    display(`The code is ${code}`, 'msg');

    // build message
    objMsg = Object.assign({ statusAuth: 'ok' }, urlData);
}

// post message back to parent window
sendMessageToParent(window, objMsg);

// display
display('Close this tab/popup and start again.', 'msg');

console.log('done');
