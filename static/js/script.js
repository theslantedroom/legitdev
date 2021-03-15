$(function() {
    // bind to button, specifies a function that should run when the user clicked on the element. If that function returns false, the default behavior will not kick in (in this case, navigate to the # URL).
    $('a#calculate').bind('click', function() {

        // sends a GET request to url and will send the contents of the data object as query parameters. Once the data arrived, it will call the given function with the return value as argument. Note that we can use the $SCRIPT_ROOT variable here that we set earlier.
        $.getJSON($SCRIPT_ROOT + '/serverAI', {
            newItem: $('input[name="newItem"]').val(),
            b: $('input[name="b"]').val()
        }, function(data) {
            $("#result").text(data.result);
            console.log('result', data.result);
            $( "#inventoryCard" ).append( "<p class='cardName textmedieval'>" + data.result + "</p>" );
        });
        return false;
    });
});


// COUNTER
// var myVar = setInterval(myTimer, 100);
// var t = 0
// function myTimer() {
// var d = new Date();
// document.getElementById("demo").innerHTML = t;
// t += 1;
// }
//   function myStopFunction() {
//     clearInterval(myVar);
//   }