var $ = require('jquery');
require('jquery.cookie');

var Utils = {
    ajaxSetup: function() {
       var csrftoken = $.cookie('csrftoken'); 

        function csrfSafeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    },
    notify: function( notificationTitle, message, options ) {
        if ( ! ( "Notification" in window ) ) {
            return;
        }
        
        options = options || {};

        var notificationOptions = {
            'icon': 'https://placekitten.com/g/101/101',
        };

        $.extend( notificationOptions, options );

        notificationOptions.body = message; 

        try {
            Notification.requestPermission( function( permission ) {

                if ( permission === "granted" ) {
                    new Notification( notificationTitle, notificationOptions );
                }

            } );
        } catch ( e ) {
            console.error( e );
        }

    }

};

module.exports = Utils;
