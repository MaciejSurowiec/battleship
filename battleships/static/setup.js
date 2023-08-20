    function allowDrop(ev) {
        ev.preventDefault();
    }

    function rotate(id) {
        switch($("#"+id).attr('class')) {
            case 'block boat2 color2':
                if(document.getElementById(id).style.transform == "rotate(90deg) translateY(21px) translateX(21px)") {
                    document.getElementById(id).setAttribute("style","transform: rotate(0) translateY(0) translateX(0)");
                } else {
                    document.getElementById(id).setAttribute("style","transform: rotate(90deg) translateY(21px) translateX(21px)");
                }
            break;
            case 'block boat3 color3':
                 if(document.getElementById(id).style.transform == "rotate(90deg) translateY(43px) translateX(42px)") {
                    document.getElementById(id).setAttribute("style","transform: rotate(0) translateY(0) translateX(0)");
                } else {
                    document.getElementById(id).setAttribute("style","transform: rotate(90deg) translateY(43px) translateX(42px)");
                }
            break;
            case 'block boat4 color4':
                if(document.getElementById(id).style.transform == "rotate(90deg) translateY(63px) translateX(63px)") {
                    document.getElementById(id).setAttribute("style","transform: rotate(0) translateY(0) translateX(0)");
                } else {
                    document.getElementById(id).setAttribute("style","transform: rotate(90deg) translateY(63px) translateX(63px)");
                }
            break;
            case 'block boat5 color5':
                if(document.getElementById(id).style.transform == "rotate(90deg) translateY(84px) translateX(84px)") {
                    document.getElementById(id).setAttribute("style","transform: rotate(0) translateY(0) translateX(0)");
                } else {
                    document.getElementById(id).setAttribute("style","transform: rotate(90deg) translateY(84px) translateX(84px)");
                }
            break;
        }
    }

    function drop(ev) {
        ev.preventDefault();
        var data = ev.dataTransfer.getData("text");
        ev.target.appendChild(document.getElementById(data));
    }

    function drag(ev) {
        ev.dataTransfer.setData("text", ev.target.id);
    }

    function checkAndSend(csrf_token) {
        for (let i = 2; i <= 5; i++) {
            if ($("#boats"+i).html().replace(/\s+/g, '') != "") {
                return;
            }
        }

        var array = Array(10).fill().map(() => Array(10).fill(0));
        for (let i = 1; i <= 10; i++) {
            var object = document.getElementById("drag"+i)
            var length = object.getAttribute("class").replace(/\D/g, '') / 11
            var position = object.parentElement.getAttribute("id")
            var pivot = position.indexOf('x')
            var x = parseInt(position.substring(0, pivot)) - 1
            var y = parseInt(position.substring(pivot, position.length).replace(/\D/g, '')) - 1
            var r = object.getAttribute("style","transform") != null &&
                object.getAttribute("style","transform") != "transform: rotate(0) translateY(0) translateX(0)"

            for (let j = 0; j < length; j++){
                if (r) { // block is rotated
                    if (y + j <= 9) {
                        if (array[y + j][x] == 0) {
                            array[y + j][x] = length
                        } else {
                            return //error boats are overlaping
                        }
                    } else {
                        return //error boat outside of board
                    }
                } else { // block is in default position
                    if (x + j <= 9) {
                        if (array[y][x + j] == 0) {
                            array[y][x + j] = length
                        } else {
                            return //error boat outside of board
                        }
                    } else {
                        return //error boat outside of board
                    }
                }
            }
        }

        let jsonArray = JSON.stringify(array) // for some reason this array is other way around
        data = {"array": jsonArray}

        $.post({
            type: "POST",
            url: window.location.href + "/setup/",
            headers: {'X-CSRFToken': csrf_token},
            data: data
        }).always(function() {
    location.reload()
 })
    }

