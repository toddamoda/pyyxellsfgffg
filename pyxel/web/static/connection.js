// The module pattern
var connection = (function() {

    var ws = null;
    var connection_element = null;
    var main_element = null;
    var on_open_callback = null;

    var init = function(ctrl_element, container, on_open_handler) {
        connection_element = ctrl_element;
        main_element = container;
        on_open_callback = on_open_handler;
    };

    var on_ws_message = function(evt) {
        console.log('on_ws_message', evt.data);
        var obj = JSON.parse(evt.data);
        var selector = '#' + obj.id.replace(/\./g, '\\.');
        main_element.trigger('message:' + obj.type, [selector, obj.fields]);
    };

    var on_ws_state_change = function(ind_text, btn_text) {
        console.log('on_ws_state_change', ind_text, btn_text);
        if (connection_element) {
            connection_element.set_button_text(btn_text);
            connection_element.highlight(ind_text)
        }
    };

    var toggle = function () {
        if (ws) {
            close();
        } else {
            open();
        }
    };

    var close = function() {
        ws.close();
    };

    var open = function() {
        var protocol = 'ws:';
        if (window.location.protocol === 'https:') {
            protocol = 'wss:';
        }
        var host = window.location.host;
        var path = '/';  // window.location.pathname;
        var url = protocol + '//' + host + path + 'websocket';
        ws = new WebSocket(url);

        ws.onmessage = function(evt) {
            on_ws_message(evt);
        };
        ws.onerror = function() {
            on_ws_state_change('Error', 'Close')
        };

        ws.onopen = function() {
            on_ws_state_change('Connected', 'Close')
            if (on_open_callback != null) {
                on_open_callback();
            }
        };

        ws.onclose = function() {
            on_ws_state_change('Not Connected', 'Connect')
            ws = null;
        };
    };

    // Private variables and functions
    var emit = function(sender, signal, params) {
        if (ws == null) {
            this.open()
            setTimeout(function () { connection.emit(sender, signal, params);}, 1000);
            return;
        }
        var kwargs = {};
        var args = [];
        if (params) {
            if (Array.isArray(args)) {
                args = params;
            } else {
                kwargs = params;
            }
        }
        var msg = {
            'sender': sender,
            'signal': signal,
            'args': args,
            'kwargs': kwargs
        }
        msg_str = JSON.stringify(msg);
        console.log('send_signal:', msg_str)
        ws.send(msg_str);
    };

    // Public API
    return {
        init: init,
        emit: emit,
        open: open,
        close: close,
        toggle: toggle,
    };
})();