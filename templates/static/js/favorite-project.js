/*
 * Bep Marketplace ELE
 * Copyright (c) 2016-2022 Kolibri Solutions
 * License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
 */

// include after websocketbridge !
$(document).ready(function () {
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';

    const favoriteSocket = new WebSocket(
        scheme + '://'
        + window.location.host
        + '/projects/favorite/'
    );

    if (typeof (project_id) === 'undefined') {    // when called from projects list, ask and set all favorites
        favoriteSocket.addEventListener('open', (event) => {
            favoriteSocket.send(JSON.stringify({'req': 'all',}));
        });

    } else {// when called from a single project (project detail page), ask the status of this project favorite.
        favoriteSocket.addEventListener('open', (event) => {
            favoriteSocket.send(JSON.stringify({'req': 'ask', 'proj': project_id}));
        });
    }

    favoriteSocket.onmessage = function (e) {
        const data = JSON.parse(e.data)
        if (data['req'] === 'all') {  // when in projects list, set all project favorite according to the received list
            var favs = data['list']
            for (var i = 0; i < favs.length; i++) {
                $('#fav-' + favs[i]).removeClass('mif-star-empty').addClass('mif-star-full');
            }
        } else {  // set project favorite for single project. Either set or ask.
            if (data['fav'] === true) {
                // favorite
                $('#fav-' + data['proj']).removeClass('mif-star-empty mif-star-half').addClass('mif-star-full');
                if (data['req'] === 'set') {  // only notify if changed, not if only asked.
                    $.Notify({
                        caption: 'Favorite set',
                        content: 'Project added to favorites.',
                        icon: "<span class='mif-star-full'></span>",
                        type: 'succes'
                    });
                }
            } else {
                //unfavorite
                $('#fav-' + data['proj']).removeClass('mif-star-full mif-star-half').addClass('mif-star-empty');
                if (data['req'] === 'set') {  // only notify if changed, not if only asked.
                    $.Notify({
                        caption: 'Favorite removed',
                        content: 'Project removed from favorites.',
                        icon: "<span class='mif-star-empty'></span>",
                        type: 'succes'
                    });
                }
            }
        }

    }
    favoriteSocket.onclose = function (e) {
        $('span.star-favorite').removeClass('mif-star-full mif-star-empty').addClass('mif-star-half');  // set fav to undefined.
        console.error('favorite socket closed');
    };
    $('.star-favorite').click(function () {
        favoriteSocket.send(JSON.stringify({'req': 'set', 'proj': parseInt(this.id.substr(4))}));
    })
});
