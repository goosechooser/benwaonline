function handleClick(cb) {
    if ($(cb).is(":checked")) {
        $.ajax({
            url: window.location.pathname + '/like',
            type: 'POST',
            success: function (result) {
                alert("it worked?", url);
            },
            error: function (jqxhr, status, exception) {
                alert('Exception: ', exception);
            }
        });
    } else {
        $.ajax({
            url: window.location.pathname + '/like',
            type: 'DELETE',
            success: function (result) {
                alert("it worked?", url);
            },
            error: function (jqxhr, status, exception) {
                alert('Exception: ', exception);
            }
        });
    }
}