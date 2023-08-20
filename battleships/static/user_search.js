const user_input = $("#user-input")
const users_div = $('#replaceable-content')
const endpoint = '/battleships'
const delay_by_in_ms = 700
let scheduled_function = false
console.log(user_input)
let ajax_call = function (endpoint, request_parameters) {
    $.getJSON(endpoint, request_parameters)
        .done(response => {
            users_div.fadeTo('fast', 0).promise().then(() => {
                users_div.html(response['html_from_view'])
                users_div.fadeTo('slow', 1)
            })
        })
}


user_input.on('keyup', function () {
    const request_parameters = {
        q: $(this).val()
    }

    if (scheduled_function) {
        clearTimeout(scheduled_function)
    }

    scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})