require('./../scss/extend_foundation.scss');

var $ = require('jquery');

var Utils = require('./components/utils');

var SchoolView = require('./views/SchoolView');
var LoginView = require('./views/LoginView');
var User = require('./models/User');
var School = require('./models/School');

var Backbone = require( 'backbone' );

Utils.ajaxSetup();
var user = new User();
var lv = new LoginView( { 'model': user } );

user.fetch({
    'success': function( model, response, options ) {
        user.trigger( 'loggedIn' );
    },
    'error': function( model, response, options ) {
        $( 'body' ).html( lv.render().$el );
    }
});

user.on( 'loggedIn', function() {
    lv.remove();
    var school = new School();
    school.fetch( {
        'success': function( school ) {
            var sv = new SchoolView( { model: school, 'user': user } );
            $( 'body' ).html( sv.render().$el );
            user.off( 'loggedIn' );
        }
    } );
} );
