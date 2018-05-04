$.extend({
    hook: function(hookName) {
        var selector;
        if(!hookName || hookName === '*') {
            // select all data-hooks
            selector = '[data-hook]';
        } else {
            // select specific data-hook
            selector = '[data-hook~="' + hookName + '"]';
        }
        return $(selector);
    }
});

function handleClick(cb) {
    if ($(cb).is(":checked")) {
        $.post(window.location.pathname + '/like');
    } else {
        $.ajax({
            url: window.location.pathname + '/like',
            type: 'DELETE'
        });
    }
}

function toggleMenu(menuElement) {
    const removeClickListener = function() {
        $(document).off('click', outsideMenuListener)
    }

    const outsideMenuListener = function(event) {
        if (!$(event.target).is($(menuElement).prev())) {
            if($(menuElement).is(':visible')) {
                $(menuElement).attr('aria-expanded', 'false')
                $(menuElement).prev().attr('aria-expanded', 'false')
                removeClickListener()
            }
        }
    }

    $(menuElement).attr('aria-expanded', function(i, expanded) {
        return expanded === 'false';
    });
    $(menuElement).prev().attr('aria-expanded', function(i, expanded) {
        return expanded === 'false';
    });

    $(document).on('click', outsideMenuListener)

}