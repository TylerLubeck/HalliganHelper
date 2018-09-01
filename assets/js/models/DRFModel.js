var Backbone = require( 'backbone' );

var DRFModel = Backbone.Model.extend( {
    url: function() {
        var _url = Backbone.Model.prototype.url.call( this );
        if ( _url.charAt( _url.length - 1 ) != '/' ) {
            _url += '/';
        }

        return  _url;
    },
} );

module.exports = DRFModel;
