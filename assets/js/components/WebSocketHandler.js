var Backbone = require('backbone');
var _ = require('underscore');
var $ = require('jquery');

var WS4Redis = require('./WS4Redis');

var WebSocketHandler = Backbone.Model.extend({
    initialize: function() {
        this.ws4redis = WS4Redis({
            uri: this._buildWebSocketURI(),
            heartbeat_msg: '--heartbeat--',
            receive_message: _.bind( this.receiveMessage, this )
        });
    },
    _buildWebSocketURI: function() {
        var webSocketProtocol = location.protocol === "http:" ? "ws:" : "wss:"; 
        webSocketProtocol += "//";
        var webSocketRoot = location.host + "/ws/ta";
        // var webSocketParams = "?subscribe-broadcast&subscribe-user";
        var webSocketParams = "?subscribe-broadcast";

        return webSocketProtocol + webSocketRoot + webSocketParams;
    },
    receiveMessage: function( msg ) {
        msg = JSON.parse( msg );
        this.trigger( msg.type, msg.data );
    }
});

module.exports = WebSocketHandler;
