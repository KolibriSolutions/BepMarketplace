/*
 * Bep Marketplace ELE
 * Copyright (c) 2016-2022 Kolibri Solutions
 * License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
 */

/**
 * Custom javascript for all pages of Marketplaces ELE
 * Jeroen van Oorschot, Kolibri Solutions 2016-2019
 */
"use strict";
//global
let sidebar = null;
let sidebarVisible = true;

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

