$(document).ready(function() {
    console.log('loaded pyxel.js');

    $('#get-state').on('click', function() {
        console.log('get-state')
        connection.emit('api', 'GET-STATE', [])
    });

    // define the application action handlers
    $('#connection_status button').on('click', function() {
        connection.toggle();
    });
    $('#pipeline select').on('change', function() {
        var url = '/pipeline/' + $(this).get_value();
        window.location = url;
    });
    $('#generate button').on('click', function() {
        connection.emit('api', 'EXECUTE-CALL', ['save_config', $(this).get_value()]);
    });
    $('#load button').on('click', function() {
        connection.emit('api', 'EXECUTE-CALL', ['load_config', $(this).get_value()]);
    });
    $('#load-module button').on('click', function() {
        connection.emit('api', 'EXECUTE-CALL', ['load_modules', $(this).get_value()]);
        $('#pipeline select').trigger('change');
    });
    $('#registry button').on('click', function() {
        connection.emit('api', 'EXECUTE-CALL', ['load_registry', $(this).get_value()]);
        $('#pipeline select').trigger('change');
    });
    $('#update-from-file button').on('click', function() {
        connection.emit('api', 'EXECUTE-CALL', ['load_defaults', $(this).get_value()]);
    });
    $('#sequence-mode button').on('click', function() {
        var run_mode = $('#sequence-mode input[name=mode]:checked').val();
        connection.emit('api', 'EXECUTE-CALL', ['set_sequence_mode', run_mode])
        $('.sequence').each(function(index) {
            var is_enabled = $(this).is_enabled();
            var key = $('select', $(this)).val();
            var range = $('input[type="text"]', $(this)).val();
            connection.emit('api', 'SET-SEQUENCE', [index, key, range, is_enabled])
        });
    });

    $('#state button').on('click', function() {
        var output_file = $('#output_file').get_value();
        connection.emit('api', 'RUN-PIPELINE', [output_file]);
    });

    $('#setting-reset').on('click', function() {
        alert('To be implemented');
    });
    $('#start-imager').on('click', function(event) {
        event.preventDefault();
        var url = '/js9/js9.html';  //$this.attr("href");
        var name = "JS9 Viewer";
        var specs = 'width=500,height=500'
        viewer = window.open(url, name, specs);
        viewer.focus()
        // setTimeout(function() {viewer.load_fits('/data/pyxel/test2.fits')}, 2000);
    });

    $('.model-state').on('change', function() {
        connection.emit('api', 'SET-MODEL-STATE', [this.id, this.checked]);
    });


    $('.model-state').on('update', function(event) {
        connection.emit('api', 'GET-MODEL-STATE', [this.id]);
    });


    $('body').on('message:progress', function(event, selector, fields) {
        $('.pe-table').trigger('message:get', [selector, fields]);
        var label_color = {'pause': 'orange', 'error': 'red', 'aborted': 'orange'};
        $(selector).progress(fields.state > 0, label_color[fields.value]);
        $('#run button').text(fields.state > 0 ? 'Stop' : 'Run')

        if (fields.file) {
            window.frames['js9viewer'].load_fits(fields.file);
            if (viewer) {
                try {
                    viewer.load_fits(fields.file)
                } catch(e) {
                    viewer = null;
                }
            }
        }
        $('#output_file button').text(fields.state ? 'Stop': 'Run')
    });

    $('body').on('message:state', function(event, selector, fields) {
        for (var key in fields.value) {
            var selector = key.split('.').slice(1).join('.');
            selector = selector.replace('.models', '');
            selector = '#' + selector.replace(/\./g, '\\.');
            console.log('message:state', selector, fields.value[key])

            if (key.match(/steps\.[0-9]\.enabled/g)) {
                // parameteric sequencer row enablement
                $(selector + ' .enable-row').prop('checked', fields.value[key]);
                $(selector + ' .enable-row').trigger('change');

            } else if (key.match(/pipeline\..*\.enabled/g)) {
                // models to be used checkbox settings
                $(selector).prop('checked', fields.value[key]);

            } else if (key == 'parametric.mode') {
                // set the parameteric sequencer mode radio button
                $('input[name=mode]').filter('[value="'+fields.value[key]+'"]').prop('checked', true);

            } else {
                // all other control fields
                $(selector).highlight(fields.value[key], true);
                $(selector).set_value(fields.value[key], false);
            }
        }
    });

});
