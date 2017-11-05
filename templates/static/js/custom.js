/**
 * Custom javascript for all pages of Marketplaces ELE
 * Jeroen van Oorschot on 2016-2017
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
    window.onload = function(){
        if (! ("MutationObserver" in window)){
            document.body.innerHTML += "<div style=\"background-color: #e00;text-align: center;position:absolute;top:0;width:100%;color:#FFF;\">" +
                "Your browser is outdated and may not be compatible with this website. Please update your browser or use another browser." +
                "</div>"
        }
    };