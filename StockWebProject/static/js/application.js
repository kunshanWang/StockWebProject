
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var numbers_received = [];
    console.log("[stockwebunityly] document ready");
    //receive details from server
    socket.on('log', function (msg) {
        console.log("Received log");
        $('#log').html(msg);
    });

    socket.on('Progress', function (msg) {
        console.log("Progress update");
        var res = msg.split("/");
        var precent = (parseInt(res[0]) / parseInt(res[1]) * 100).toPrecision(2);
        precent = (precent > 100) ? 100 : precent;

        $("#progress-bar").css("width", precent + "%")
        $("#progress-span").text(msg + "(" + precent +"%)")
    });


    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        //maintain a list of ten numbers
        if (numbers_received.length >= 10){
            numbers_received.shift()
        }            
        numbers_received.push(msg.number);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }
        $('#log').html(numbers_string);
    });

    $('input[type=button]').click(function () {
        var name = $(this).attr('name');
        socket.emit('AddWatch', name);
        console.log(name);
        //var name = $(this).name;
        //console.log(name);
    });

});