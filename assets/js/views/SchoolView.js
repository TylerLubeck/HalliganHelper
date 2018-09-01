var Backbone = require('backbone');
var _ = require('underscore');
var $ = require('jquery');

var School = require('./../models/School');
var CourseView = require('./CourseView');
var DashboardView = require('./DashboardView');
var ProfileView = require('./ProfileView');
var AppRouter = require('./../router');
var WebSocketHandler = require('./../components/WebSocketHandler');
var utils = require( './../components/utils' );


var SchoolView = Backbone.View.extend({
    template: _.template( require( './../templates/school-template' ) ),
    events: {
        'click .menu-item>a': 'mobileNavClick',
    },

    initialize: function( options ) {
        this.user = options.user;
        this.webSocketHandler = new WebSocketHandler();

        this.courseView = new CourseView( { 
            'user': this.user,
            'webSocketHandler': this.webSocketHandler 
        } );

        this.dashboardView = new DashboardView( { 'model': this.model } );
        this.profileView = new ProfileView( { 'model': this.user } );

        this.router = this.initRouter();
        this.initWebSocketListeners();
    },
    updateDashboard: function( data ) {
        /* 
         * When we receive a request, update the course request count
         * so that the dashboard stays valid
         */
        this.model.courses.get( { 'id': data.course } ).fetch();
    },
    requestCheckedOut: function( data ) {
        msg = data.checked_out_by + ' to the rescue!';
        options = {
            'icon': data.headshot,
            'tag': 'incoming_help',
        };
        utils.notify( 'Help is on the way!', msg, options );
    },
    initWebSocketListeners: function() {
        this.listenTo( this.webSocketHandler, 
                       'request_created request_removed on_duty off_duty', 
                       _.bind( this.updateDashboard, this ) );

        this.listenTo( this.webSocketHandler,
                       'checked_out',
                       _.bind( this.requestCheckedOut, this ) );
    },
    initRouter: function() {
        var router = new AppRouter();

        router.on( 'route:course', _.bind(function( id ) {
            this.courseView.trigger( 'newCourse', Number( id ) );
            this.mainContent.html( this.courseView.$el );
        }, this ) );
    
        router.on( 'route:dashboard', _.bind( function() {
            this.mainContent.html( this.dashboardView.render().$el );
        }, this ) );

        router.on( 'route:profile', _.bind( function() {
            this.mainContent.html( this.profileView.render().$el );
        }, this ) );

        router.on( 'route:logout', _.bind( function() {
            this.user.logout( {
                'success': function() {
                    location.replace('/');
                } 
            } ); 
        }, this) );

        return router;
        
    },
    mobileNavClick: function() {
        this.$el.find( '.menu-checkbox' ).attr( 'checked', false );
    },
    render: function() {
        this.$el.html( this.template( this.model.attributes ) ); 
        this.mainContent = this.$el.find( '.main-content' );

        /* Backbone.history.start returns false if the current url doesn't 
         * match any known route. If there's no match, show them the dashboard
         */
        if( ! Backbone.history.start() ) {
            this.router.navigate( 'dashboard', { 'trigger': true } );
        }
        return this;
    },
});

module.exports = SchoolView;
