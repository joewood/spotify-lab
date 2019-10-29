function debug(name, variable) {
    console.log(name);
    console.log(variable);
}

function display(obj, id = 'authStatus', reset = false) {
    const e = document.getElementById(id);
    if (reset) {
        e.innerHTML = `${obj}<br/><br/>`;
    } else {
        e.innerHTML += `${obj}<br/><br/>`;
    }
}

///////////////////////////////////////////////////////

function getDataFromCallbackUrl() {
    const url1 = window.location.href.split('#')[1];
    const url2 = window.location.href.split('?')[1];
    const url = url1 ? url1 : url2;
    const urlParams = new URLSearchParams(url);
    const data = Object.assign(
        ...Array.from(urlParams.entries()).map(([k, v]) => ({ [k]: v }))
    );
    return data;
}

function parseJwt(id_token) {
    const base64Url = id_token.split('.')[1];
    const base64 = base64Url.replace('-', '+').replace('_', '/');
    return JSON.parse(window.atob(base64));
}

function containsError(urlData) {
    let e = false;
    if ('error' in urlData) e = true;
    if ('error_description' in urlData) e = true;
    if (!('access_token' in urlData) && !('code' in urlData)) e = true;
    if (!('state' in urlData)) e = true;
    return e;
}

function sendMessageToParent(window, objMsg) {
    // debug('window.parent', window.parent);
    window.parent.postMessage(objMsg, '*');
    if (window.parent.opener) {
        // debug('window.parent.opener', window.parent.opener);
        window.parent.opener.postMessage(objMsg, '*');
    }
}
