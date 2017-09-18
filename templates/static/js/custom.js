/**
 * Created by Jeroen on 5-11-2016.
 */
    //Call with show= true, false or 'toggle'
    /*function toggleLogos(show){
        if(($("#cellLogos").is(":visible") && show=='toggle') || show===false){
            $("#cellLogos").hide();
            $("#cellContent").removeClass("colspan3").addClass("colspan4")
        }else{
            $("#cellLogos").show();
            $("#cellContent").removeClass("colspan4").addClass("colspan3")
        }
    }
    */
    function roll(name)
    {
        $(name).removeClass("roll");
        setTimeout(function () {
             $(name).removeClass('roll');
        }, 5000);
        $(name).addClass("roll");
    }


    //display warning for unsupported browsers
    $().ready(function(){
        if (! ("MutationObserver" in window)){
            document.body.innerHTML += '<div style="background: #e00; text-align: center; position: absolute; top: 0px; width: 100%; color: #FFF;">This website may not be compatible with your browser. Please update your browser or use another browser.</div>'
        }
    });
