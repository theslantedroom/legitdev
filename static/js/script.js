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
    $('a#pocketCash').bind('click', function() {
        let chargeFrozen = charge;
        document.getElementById('pocketCash').style.display = 'none';
        document.getElementById('chargeHtmlspan').style.display = 'none';
        document.getElementById('pocketCashLoading').style.display = 'block';


        // sends a GET request to url and will send the contents of the data object as query parameters. Once the data arrived, it will call the given function with the return value as argument. Note that we can use the $SCRIPT_ROOT variable here that we set earlier. calls serverAI in app.py
        $.getJSON($SCRIPT_ROOT + '/pocketCash', {
            newCharge: charge
        }, function(data) {
            let currentCharge = parseInt(document.getElementById('cardChargeTotal').innerHTML);
            console.log('currentCHarge', currentCharge);
            let updatedCharge = chargeFrozen + currentCharge - 1;
            console.log('updatedCharge',updatedCharge);
            $( "#cardChargeTotal" ).text(updatedCharge);
            setTimeout(function(){ 
                document.getElementById('pocketCash').style.display = 'block'; 
                document.getElementById('pocketCashLoading').style.display = 'none';
                charge = 0;
                document.getElementById('chargeHtmlspan').style.display = 'block';

            }, 3000);
            
        });
        return false;
    });
});

// Charge Display
let chargeDisplay = document.getElementById("chargeHtml");




