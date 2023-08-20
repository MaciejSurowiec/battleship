function attack(csrf_token) {
    var position = $('input[name="attack"]:checked').val();
    var pivot = position.indexOf('x')
    var x = parseInt(position.substring(0, pivot)) - 1
    var y = parseInt(position.substring(pivot, position.length).replace(/\D/g, '')) - 1
    data = {"x": x, "y": y}

    $.post({
        type: "POST",
        url: window.location.href + "/move/",
        headers: {'X-CSRFToken': csrf_token},
        data: data
    }).always(function() {
    location.reload()
 })
}
