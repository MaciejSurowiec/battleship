var decline = function(value,csrf_token) {
    $.ajax({
        type: 'DELETE',
        url: '/battleships/invite/' + value,
        headers: {'X-CSRFToken': csrf_token},
    }).always(function() {
    location.reload()
 })
}

var accept = function(value,csrf_token) {
    $.ajax({
        type: 'POST',
        url: '/battleships/invite/' + value,
        headers: {'X-CSRFToken': csrf_token},
    }).always(function() {
    location.reload()
 })
}