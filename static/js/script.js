let charge = 0

// specifies code that should run once the browser is done loading the basic parts of the page.
$(function() {
    // // bind to button, specifies a function that should run when the user clicked on the element. If that function returns false, the default behavior will not kick in (in this case, navigate to the # URL).
    // $('a#calculate').bind('click', function() {

    //     // sends a GET request to url and will send the contents of the data object as query parameters. Once the data arrived, it will call the given function with the return value as argument. Note that we can use the $SCRIPT_ROOT variable here that we set earlier. calls serverAI in app.py
    //     $.getJSON($SCRIPT_ROOT + '/serverAI', {
    //         newItem: $('input[name="newItem"]').val(),
    //         b: $('input[name="b"]').val()
    //     }, function(data) {
    //         $("#result").text(data.result);
    //         console.log('result', data.result);
    //         $( "#inventoryCard" ).append( "<p class='cardName textmedieval'>" + data.result + "</p>" );
    //     });
    //     return false;
    // });

    // commits charge to DB
    $('a#commitCharge').bind('click', function() {
        // sends a GET request to url and will send the contents of the data object as query parameters. Once the data arrived, it will call the given function with the return value as argument. Note that we can use the $SCRIPT_ROOT variable here that we set earlier. calls serverAI in app.py
        $.getJSON($SCRIPT_ROOT + '/commitCharge', {
            newCharge: charge
        }, function(data) {
            let currentCharge = parseInt(document.getElementById('cardChargeTotal').innerHTML);
            console.log('currentCHarge', currentCharge);
            let updatedCharge = charge + currentCharge;
            console.log('updatedCharge',updatedCharge);
            $( "#cardChargeTotal" ).text(updatedCharge);
            charge = 0;
        });
        return false;
    });
});

// Charge Display
let chargeDisplay = document.getElementById("chargeHtml");


// COUNTER

var chargeInterval = setInterval(indexTimer, 100);
function indexTimer() {
    chargeDisplay.innerHTML = charge;
    charge += 1;
}
  function myStopFunction() {
    clearInterval(chargeInterval);
  }

