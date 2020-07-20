/*
 * Bep Marketplace ELE
 * Copyright (c) 2016-2020 Kolibri Solutions
 * License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
 */

// include after websocketbridge !
$(document).ready(function () {
    const webSocketBridgeFavorite = new channels.WebSocketBridge();
    webSocketBridgeFavorite.connect('/projects/favorite/');
    webSocketBridgeFavorite.listen(function (action, stream) {
        // console.log(action);
        //s[0] //project
        //s[1] //status
        if (action[1] === true) {
            // favorite
            $('#fav-' + action[0]).removeClass('mif-star-empty').addClass('mif-star-full');
            $.Notify({
                caption: 'Favorite set',
                content: 'Project added to favorites.',
                icon: "<span class='mif-star-full'></span>",
                type: 'succes'
            });
        } else {
            //unfavorite
            $('#fav-' + action[0]).removeClass('mif-star-full').addClass('mif-star-empty');
            $.Notify({
                caption: 'Favorite removed',
                content: 'Project removed from favorites.',
                icon: "<span class='mif-star-empty'></span>",
                type: 'succes'
            });
        }


    });

    $('.star-favorite').click(function () {
        webSocketBridgeFavorite.send(parseInt(this.id.substr(4))); //send number of the proposal, without 'fav-'
    })
});
