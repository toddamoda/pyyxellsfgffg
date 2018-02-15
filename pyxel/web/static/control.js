var cfg = null;
var ws = null;

function send_signal(sender, signal, params) {

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
    ws.send(msg_str);
}


function get(json_obj, att_name, att_value) {
    for (i in json_obj) {
        if (att_name in json_obj[i] && json_obj[i][att_name] == att_value) {
            return json_obj[i];
        }
    }
    return null;
}


function keys(obj) {
    var keys = [];
    for (key in obj) {
        keys.push(key);
    }
    return keys;
}


function on_highlight_indicator(ind, ind_text) {
    ind.text(ind_text);
    ind.prop('title', ind_text);
    ind.addClass('indicator-hilite');
    setTimeout(function() { ind.removeClass('indicator-hilite'); }, 500);
}


function on_connect_state_change(ind_text, btn_text) {
    var btn = $('#connection_status button');
    var ind = $('#connection_status .indicator');
    btn.text(btn_text)
    on_highlight_indicator(ind, ind_text)
}


function on_update_indicator(measurement, fields) {

    var messages = cfg.messages;
    var msg = get(messages, 'name', measurement);
    if (!msg) {
        return;
    }
    if (msg.format) {
        var text = $.format(msg.format, fields)
        var ind = $(msg.ind_selector);
        on_highlight_indicator(ind, text)
    }
    if (msg.state_field && msg.state_map) {
        var state = fields[msg.state_field];
        var state_obj = get(msg.state_map, 'state', state);
        if (!state_obj) {
            state_obj = get(msg.state_map, 'state', 'default')
        }
        for (var i in state_obj.selector) {
            $(state_obj.selector[i]).text(state_obj.label[i]);
        }
    }
}


function on_response(data) {

    var obj = JSON.parse(data);
    if (obj.type == 'progress') {
        var id = obj.id;
        var fields = obj.fields;
        var label = fields.label;
        var selector = '#' + obj.id.replace(/\./g, '\\.') + ' .indicator'
        var ind_text = $.format('%(value)s', fields);
        var ind = $(selector);
        on_highlight_indicator(ind, ind_text)
        $('.pe-progress .pe-progress-running').css('background-color', '')
        if (label == 'pause') {
            ind.css('background-color', 'orange');
        } else if (label == 'abort') {
            ind.css('background-color', 'red');
        }
        $('.pe-progress .pe-progress-running').removeClass('pe-progress-running')
        ind.addClass('pe-progress-running');
    }
    if (obj.type == 'hk') {
        var measurement = obj.measurement;
        var fields = obj.fields;
        on_update_indicator(measurement, fields)
        //$('.pe-progress .pe-progress-running').removeClass('pe-progress-running')
    }

    if (obj.type == 'get') {
        var id = obj.id;
        var fields = obj.fields;
        var selector = '#' + obj.id.replace(/\./g, '\\.') + ' .indicator'
        var ind_text = 'None'
        if (fields.value) {
            ind_text = $.format('%(value)s', fields);
        }
        var ind = $(selector);
        on_highlight_indicator(ind, ind_text)
        //$('.pe-progress .pe-progress-running').removeClass('pe-progress-running')
    }
}

function get_value(context) {
    var value = null;
    if ($('select', context).length) {
        value = $('select', context).val();
    } else if ($('input', context).length == 1) {
        value = $('input', context).val();
    } else if ($('input', context).length > 1) {
        value = [];
        $('input', context).each(function() {
            value.push($(this).val());
        });
    }
    return value;
}

function init_controls() {

    $('#connection_status button').click(function() {
        var text = $('#connection_status button').text();
        if (text == 'Connect') {
            init_socket_stream()
        } else {
            ws.close()
        }
    });

    $('#output_file button').click(function() {
        var value = $('#output_file input').val();
        send_signal('api', 'RUN-PIPELINE', [value]);
    });

    $('.setting .indicator').click(function() {
        console.log('get')
        var row_elem = $(this).parents('tr');
        var id = row_elem.attr('id');
        console.log('Sending signal: %s, %s, %s','api', 'GET-SETTING', [id])
        send_signal('api', 'GET-SETTING', [id]);
    });

    $('#setting-set-all').click(function() {
        console.log('set-all')
        $('.setting button').click();
    });
    $('#setting-get-all').click(function() {
        console.log('get-all')
        $('.setting .indicator').click();
    });

    $('.pe-table button').click(function() {
        var signals = cfg.actions;
        var i;
        var params = [];
        var action = null;
        var row_elem = $(this).parents('tr');
        var id = row_elem.attr('id');
        var cls = row_elem.attr('class');
        var signal = get(signals, "id", id);
        if (signal && signal.toggle) {
            var text = $(this).text();
            action = get(signal.toggle, "label", text);
            for (i in action.args_selector) {
                params.push($(action.args_selector[i]).val());
            }
        }
        var signal = get(signals, "class", cls);
        if (signal && signal.click) {
            action = signal.click;
            for (i in action.args) {
                var value = null;
                var to_eval = action.args[i];
                var expr = to_eval.charAt(0);
                if (to_eval == '@value') {
                    value = get_value(row_elem)
                } else if (to_eval == '@id') {
                    value = id;
                } else if (expr == '#' || expr == '.') {
                    value = $(to_eval).val();
                }
                params.push(value);
            }
        }
        if (action) {
            console.log('Sending signal: %s, %s, %s', action.sender, action.signal, params)
            send_signal(action.sender, action.signal, params);
        }
    });
}


function init_socket_stream() {
    var protocol = 'ws:';
    if (window.location.protocol === 'https:') {
        protocol = 'wss:';
    }
    var host = window.location.host;
    var path = window.location.pathname;
    var url = protocol + '//' + host + path + 'websocket';  // rpc
    ws = new WebSocket(url);
    console.log('ws=' + ws);

    ws.onmessage = function(e) {
        console.log(e.data);
        on_response(e.data);
    };
    ws.onerror = function() {
        console.log('error...');
        on_connect_state_change('Error', 'Close')
    };

    ws.onopen = function() {
        console.log('connected...');
        on_connect_state_change('Connected', 'Close')
    };

    ws.onclose = function() {
        console.log('closed');
        on_connect_state_change('Not Connected', 'Connect')
        ws = null;
    };

    return ws;
}


$(document).ready(function() {

    ws = init_socket_stream();

    $('.pe-table td:nth-child(2) div').addClass('form-control')
    $('.pe-table td:nth-child(2) div').addClass('pe-output')

    $('.pe-table td input').addClass('form-control')
    $('.pe-table td select').addClass('form-control')
    $('.pe-table td select').addClass('custom')
    $('.pe-table td button').addClass('btn')
    $('.pe-table td button').addClass('btn-primary')

    $('#pe-expand').click(function() {
        $('.pe-section-hide').find('caption').click();
    });
    $('#pe-collapse').click(function() {
        $('.pe-table').not('.pe-section-hide').find('caption').click();
    });
    $('.pe-section').each(function() {
        $(this).prop('title', $(this).text());
        $(this).html('&#x25BC ' + $(this).text());
    });
    $('.pe-section').click(function() {
        $(this).closest('table').toggleClass('pe-section-hide');
        var is_hidden = $(this).closest('table').hasClass('pe-section-hide');
        var arrow = is_hidden ? '&nbsp;&#x25B6; ' : '&nbsp;&#x25BC ';
        $(this).html(arrow + $(this).prop('title'));
    });

    $.getJSON('/static/control.json', function(data) {
        cfg = data;
        init_controls();
    });
});
