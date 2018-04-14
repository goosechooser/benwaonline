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