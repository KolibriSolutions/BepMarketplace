/**
 * Custom javascript for all pages of Marketplaces ELE
 * Jeroen van Oorschot, Kolibri Solutions 2016-2019
 */
"use strict";
//global
let sidebar = null;
let sidebarVisible = true;

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
    let c = $('#cellContent');
    $('#cellSidebar').css('opacity', 0);
    $('#toggleSidebarButtonIcon').css('transform', 'rotate(180deg)');
    sidebarVisible = false;
    window.setTimeout(function () {
        c.addClass('transitionWidth');
        c.removeClass('colspan4').addClass('colspan5');
    }, 400);
}

function hideSidebarFast() {
    let c = $('#cellSidebar');
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
    let c = $('#cellContent');
    c.addClass('transitionWidth');
    c.removeClass('colspan5').addClass('colspan4');
    $('#toggleSidebarButtonIcon').css('transform', '');
    sidebar.appendTo('#contentGrid');
    sidebarVisible = true;
    window.setTimeout(function () {
        $('#cellSidebar').css('opacity', 1);
    }, 400);
}

