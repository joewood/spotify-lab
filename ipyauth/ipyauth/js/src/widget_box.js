import { extend } from 'lodash';
import * as widgets from '@jupyter-widgets/controls';

import auth from './widget_auth';
import util from './widget_util';

import { version } from '../package.json';

const semver_range = `~${version}`;

const AuthModel = widgets.VBoxModel.extend({
    defaults() {
        return extend(AuthModel.__super__.defaults.call(this), {
            _model_name: 'AuthModel',
            _view_name: 'AuthView',
            _model_module: 'ipyauth',
            _view_module: 'ipyauth',
            _model_module_version: semver_range,
            _view_module_version: semver_range,

            name: '',
            _id: '',

            params: {},

            access_token: '',
            scope: '',
            logged_as: '',
            time_to_exp: '',
            expires_at: '',

            _incr_signout: 0,
            _incr_code: 0,
            _incr_display: 0,
        });
    },

    initialize() {
        console.log('ipyauth start initialize');

        // Use apply() on parent initialize
        AuthModel.__super__.initialize.apply(this, arguments);

        console.log('ipyauth end initialize');
    },
});

const AuthView = widgets.VBoxView.extend({
    render() {
        console.log('ipyauth start render');

        // Use call() on parent render
        AuthView.__super__.render.call(this);

        // explicit
        const that = this;

        const resolved = {};
        const promise1 = this.children_views.views;

        Promise.all(promise1).then(views1 => {
            console.log('views1 callback start');

            const promise2 = [
                views1[0].children_views.views[1],
                views1[0].children_views.views[2],
                views1[0].children_views.views[3],
                views1[0].children_views.views[4],
                views1[0].children_views.views[5],
                views1[1].children_views.views[0],
            ];

            Promise.all(promise2).then(views2 => {
                console.log('views2 callback start');

                resolved.btn_main = views2[0];
                resolved.logged_as = views2[1];
                resolved.time_to_exp = views2[2];
                resolved.expires_at = views2[3];
                resolved.btn_inspect = views2[4];
                resolved.scope = views2[5];

                const btn_main_clicked = function() {
                    console.log('btn_main clicked');
                    if (auth.isLogged(that)) {
                        auth.clear(that);
                    } else {
                        auth.login(that);
                    }
                };
                resolved.btn_main.el.addEventListener('click', btn_main_clicked);

                const btn_inspect_clicked = function() {
                    console.log('btn_inspect clicked');
                    auth.inspect(that);
                };
                resolved.btn_inspect.el.addEventListener('click', btn_inspect_clicked);

                that.form = resolved;

                // iframe
                const ifrm = document.createElement('iframe');
                ifrm.id = 'auth';
                ifrm.width = '600';
                ifrm.height = '300';
                ifrm.src = '';
                ifrm.style.display = 'none';
                that.el.appendChild(ifrm);

                // debug
                window.that = that;

                console.log('views2 callback end');
            });
            console.log('views1 callback end');
        });

        that.model.on('change:_incr_signout', that.incr_signout, that);
        that.model.on('change:_incr_display', that.incr_display, that);
        console.log('ipyauth end render');
    },

    incr_signout() {
        console.log('start incr_signout');
        auth.clearWidget(that);
    },

    incr_display() {
        console.log('start incr_display');
        const objCreds = util.buildObjCreds(that);
        auth.clearWidget(that, objCreds);
    },
});

export { AuthModel, AuthView };
