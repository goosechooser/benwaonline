function handleClick(cb) {
    if ($(cb).is(":checked")) {
        $.post(window.location.pathname + '/like');
    } else {
        $.delete(window.location.pathname + '/like');
    }
}