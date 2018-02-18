$.fn.extend({
    highlight: function(text) {
        var ind = $('.indicator', $(this));
        ind.text(text).prop('title', text).addClass('indicator-hilite');
        setTimeout(function() { ind.removeClass('indicator-hilite'); }, 500);
        return $(this);
    },

    progress: function(enabled, color) {
        var ind = $('.indicator', $(this));
        var run = $('.pe-progress .pe-progress-running');
        run.removeClass('pe-progress-running').css('background-color', '')
        if (color) {
            ind.css('background-color', color);
        }
        if (enabled) {
            ind.addClass('pe-progress-running');
        }
    },

    set_enabled: function(enabled) {
        var disabled = enabled ? false : 'disabled';
        $('select', $(this)).prop('disabled', disabled);
        $('input[type="text"]', $(this)).prop('disabled', disabled);
    },

    is_enabled: function() {
        return $('input[type="checkbox"]', $(this)).is(":checked");
    },

    set_button_text: function(text) {
        //console.log(this, $(this))
        var btn = $('button', this);
        btn.text(text);
        return $(this);
    },

    get_value: function() {
        context = $(this);
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
    },

    set_value: function(value) {
        var context = $(this);
        if ($('select', context).length) {
            $('select', context).val(value);
        } else if ($('input', context).length == 1) {
            $('input', context).val(value);
        } else if ($('input', context).length > 1) {
            $('input', context).each(function(index) {
                $(this).val(value[index]);
            });
        }
        return $(this);
    }
});
