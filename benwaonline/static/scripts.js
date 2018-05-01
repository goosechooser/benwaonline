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

function menuHandler() {
    $("#dropdown").attr('aria-expanded', function(i, expanded) {
      return expanded === 'false'
    });
  }

  // Close the dropdown if the user clicks outside of it
  window.onclick = function(e) {
    if (!e.target.matches('.menu-button')) {
      $("#dropdown").attr('aria-expanded', 'false')
    }
  }

