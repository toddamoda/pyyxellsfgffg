





$(document).ready(function() {

    // set bootstrap styles
    $('.pe-table td:nth-child(2) div').addClass('form-control')
    $('.pe-table td:nth-child(2) div').addClass('pe-output')

    $('.pe-table td input').addClass('form-control')
    $('.pe-table td select').addClass('form-control')
    $('.pe-table td select').addClass('custom')
    $('.pe-table td button').addClass('btn')
    $('.pe-table td button').addClass('btn-primary')

    // define the section event handlers
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

    // define the row enablement checkboxs
    $('.pe-table .enable-row').change(function() {
        $(this).parents('tr').set_enabled($(this).is(":checked"));
    });
    $('.pe-table .enable-row').change();

    // define the getter/setters
    $('.setting button').click(function() {
        var id = $(this).parents('tr').attr('id');
        var value = $(this).parents('tr').get_value();
        connection.emit('api', 'SET-SETTING', [id, value])
    });
    $('#setting-set-all').click(function() {
        $('.setting button').click();
    });
    $('.setting .indicator').click(function() {
        var id = $(this).parents('tr').attr('id');
        connection.emit('api', 'GET-SETTING', [id]);
    });
    $('#setting-get-all').click(function() {
        console.log('get-all')
        $('.setting .indicator').click();
    });

    // define the application action handlers
    $('#connection_status button').click(function() {
        connection.toggle();
    });
    $('#output_file button').click(function() {
        $('.sequence').each(function(index) {
            var is_enabled = $(this).is_enabled();
            var key = $('select', $(this)).val();
            var range = $('input[type="text"]', $(this)).val();
            connection.emit('api', 'SET-SEQUENCE', [index, key, range, is_enabled])
        });
        var value = $(this).get_value();
        connection.emit('api', 'RUN-PIPELINE', [value]);
    });

    $('#setting-reset').click(function() {
        alert('To be implemented');
    });
    $('#start-imager').click(function() {
        alert('To be implemented');
    });

    $('#pyxel').on('message:progress', function(event, selector, fields) {
        $('.pe-table').trigger('message:get', [selector, fields]);
        var label_color = {'pause': 'orange', 'error': 'red'};
        $(selector).progress(fields.state > 0, label_color[fields.label]);
    });
    $('#pyxel').on('message:get', function(event, selector, fields) {
        var text = $.format('%(value)s', fields);
        $(selector).highlight(text);
    });

    connection.init($('#connection_status'), $('#pyxel'))
    connection.open();

});
