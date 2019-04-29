/**
 * Custom javascript for all pages of Marketplaces ELE
 * Jeroen van Oorschot, Kolibri Solutions 2016-2018
 */
// function roll(name) {
//     $(name).removeClass("roll");
//     setTimeout(function () {
//         $(name).removeClass('roll');
//     }, 5000);
//     $(name).addClass("roll");
// }

//global
var sidebar = null;
var sidebarVisible = true;

//display warning for unsupported browsers
window.onload = function () {
    if (!("MutationObserver" in window)) {
        document.body.innerHTML += "<div style=\"warning-banner\">" +
            "Your browser is outdated and may not be compatible with this website. Please update your browser or use another browser." +
            "</div>"
    }
};
$(function () {
        $('#toggleSidebarButton')[0].addEventListener('click', function () {
            toggleSidebar()
        });
        $('#cellSidebar')[0].addEventListener('transitionend', function () {
            if (!sidebarVisible) {
                sidebar = $('#cellSidebar').detach();
            } else {
                sidebar = null;
            }
        }, false);
        $('#cellContent')[0].addEventListener('transitionend', function () {
            $(window).trigger('resize');  // trigger the window resize event, to let jquery.DoubleScroll resize the second bar.
            $('#cellContent').removeClass('transitionWidth')
        }, false);

        //init markdownx custom event handlers.
        let element = document.getElementsByClassName('markdownx');
        //
        // Object.keys(element).map(key =>
        //     element[key].addEventListener('markdownx.update', event => console.log('updated!', event.detail))
        // );
        Object.keys(element).map(function (key) {
            element[key].addEventListener('markdownx.updateError', function (event) {
                $.Notify({
                    caption: 'Markdown preview error.',
                    content: 'Please refresh the page to continue.',
                    type: 'alert'
                })
            })
        });
        Object.keys(element).map(function (key) {
            element[key].addEventListener('markdownx.fileUploadEnd', function (event) {
                $.Notify({
                    caption: 'File uploaded!',
                    content: event.detail[0].image_code,
                    type: 'success'
                })
            })
        });
        Object.keys(element).map(function (key) {
            element[key].addEventListener('markdownx.fileUploadError', function (event) {
                $.Notify({
                    caption: 'File upload failed!',
                    content: event.detail[0].__all__.concat().toString(),
                    type: 'alert'
                })
            })
        });
    }
);

function toggleSidebar() {
    if (sidebarVisible) {
        hideSidebar();
    } else {
        showSidebar();
    }
}

function hideSidebar() {
    var c = $('#cellContent');
    $('#cellSidebar').css('opacity', 0);
    $('#toggleSidebarButtonIcon').css('transform', 'rotate(180deg)');
    sidebarVisible = false;
    window.setTimeout(function () {
        c.addClass('transitionWidth');
        c.removeClass('colspan4').addClass('colspan5');
    }, 400);
}

function hideSidebarFast() {
    var c = $('#cellSidebar');
    c.css('opacity', 0);
    $('#toggleSidebarButtonIcon').css('transform', 'rotate(180deg)');
    sidebarVisible = false;
    $('#cellContent').removeClass('colspan4').addClass('colspan5');
    $(window).trigger('resize');  // trigger the window resize event, to let jquery.DoubleScroll resize the second bar.
    if (!sidebar) { //don't overwrite sidebar on second time calling this function.
        sidebar = c.detach();
    }
}

function showSidebar() {
    var c = $('#cellContent');
    c.addClass('transitionWidth');
    c.removeClass('colspan5').addClass('colspan4');
    $('#toggleSidebarButtonIcon').css('transform', '');
    sidebar.appendTo('#contentGrid');
    sidebarVisible = true;
    window.setTimeout(function () {
        $('#cellSidebar').css('opacity', 1);
    }, 400);
}

