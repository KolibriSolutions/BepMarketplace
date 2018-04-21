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
    //global
    var sidebar = null;
    var sidebarVisible = true;

    //display warning for unsupported browsers
    window.onload = function() {
        if (!("MutationObserver" in window)) {
            document.body.innerHTML += "<div style=\"background-color: #e00;text-align: center;position:absolute;top:0;width:100%;color:#FFF;\">" +
                "Your browser is outdated and may not be compatible with this website. Please update your browser or use another browser." +
                "</div>"
        }
    };
    $(function(){
        $('#toggleSidebarButton')[0].addEventListener('click', function(){toggleSidebar()});
        $('#cellSidebar')[0].addEventListener('transitionend', function () {
            if(!sidebarVisible){
                sidebar = $('#cellSidebar').detach();
            }else{
                sidebar = null;
            }
        }, false);
        $('#cellContent')[0].addEventListener('transitionend', function () {
            $(window).trigger('resize');  // trigger the window resize event, to let jquery.DoubleScroll resize the second bar.
            $('#cellContent').removeClass('transitionWidth')
        }, false);
    });
    function toggleSidebar(){
        if(sidebarVisible){
            hideSidebar();
        }else{
            showSidebar();
        }
    }
    function hideSidebar(){
        var c = $('#cellContent');
        $('#cellSidebar').css('opacity', 0);
        $('#toggleSidebarButtonIcon').css('transform', 'rotate(180deg)');
        sidebarVisible = false;
        window.setTimeout(function() {
            c.addClass('transitionWidth');
            c.removeClass('colspan4').addClass('colspan5');
        }, 400);
    }

    function showSidebar(){
        var c = $('#cellContent');
        c.addClass('transitionWidth');
        c.removeClass('colspan5').addClass('colspan4');
        $('#toggleSidebarButtonIcon').css('transform', '');
        sidebar.appendTo('#contentGrid');
        sidebarVisible = true;
        window.setTimeout(function(){
            $('#cellSidebar').css('opacity', 1);
        }, 400);
    }