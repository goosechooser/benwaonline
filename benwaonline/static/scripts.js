function handleLike() {
    if ($(this).is(":checked")) {
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

// event handlers
$('[data-hook="nav-menu-toggle"]').click(function() {
    toggleMenu($('[data-hook="nav-menu-content"]'));
});

$('[data-hook="like-check"]').click(handleLike);
// document.getElementById('checkBox').addEventListener('click', handleClick);
