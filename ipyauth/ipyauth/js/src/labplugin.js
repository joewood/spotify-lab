import * as base from '@jupyter-widgets/base';

import * as myWidget from './widget';
import { version } from './index';

const id = 'ipyauth';
const requires = [base.IJupyterWidgetRegistry];
const autoStart = true;

const activate = (app, widgets) => {
    console.log('JupyterLab extension ipyauth is activated!');

    widgets.registerWidget({
        name: 'ipyauth',
        version,
        exports: myWidget,
    });
};

export default {
    id,
    requires,
    activate,
    autoStart,
};
