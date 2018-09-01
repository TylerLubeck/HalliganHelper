var Backbone = require( 'backbone' );
var _ = require('underscore');
var $ = require('jquery');

var Course = require('./../models/Course');
var Request = require('./../models/Request');
var OfficeHour = require('./../models/OfficeHour');

var Requests = require('./../collections/Requests');
var TAs = require('./../collections/TAs');
var OfficeHours = require( './../collections/OfficeHours' );

var TAsView = require( './TAsView' );
var RequestsView = require( './RequestsView' );
var OfficeHoursView = require( './OfficeHoursView' );
var MakeRequestView = require('./MakeRequestView');

var utils = require( './../components/utils' );

var CourseView = Backbone.View.extend({
    template: _.template( require( './../templates/course-template' ) ),
    loadingTemplate: _.template( require( './../templates/loading-template' ) ),

    initialize: function( options ) {

        this.user = options.user;
        this.webSocketHandler = options.webSocketHandler;
        this.course = new Course();

        this.initCollections();
        this.initSubViews();
        this.initListeners();

    },
    initCollections: function() {
        this.requests = new Requests( [], { 'course': this.course } );
        this.officeHours = new OfficeHours( [], { 'course': this.course } );
        this.tas = new TAs( [], { 'course': this.course } );
    },
    initSubViews: function() {
        this.requestsView = new RequestsView( {
            'collection': this.requests,
        } );
        this.makeRequestView = new MakeRequestView( { 
            'course': this.course 
        } );
        this.TAsView = new TAsView( { 
            /*
            'user': this.user, 
            'course': this.course,
            */
            'collection': this.tas,
        } );
        this.officeHoursView = new OfficeHoursView( {
            'course': this.course,
            'collection': this.officeHours,   
        } );
    },
    initListeners: function() {
        this.listenTo( this.course, 'sync', this.render );
        this.listenTo( this.makeRequestView, 'newRequest', this.newRequest );
        this.listenTo( this.webSocketHandler, 
                       'request_created request_updated', 
                       this.newWebSocketRequest );
        this.listenTo( this.webSocketHandler,
                       'request_removed',
                       this.removeWebSocketRequest );
        this.listenTo( this.webSocketHandler,
                       'on_duty',
                       this.newWebSocketOfficeHour );
        this.listenTo( this.webSocketHandler,
                       'off_duty',
                       this.removeWebSocketOfficeHour );
        this.listenTo( this, 'newCourse', _.bind( function( courseID ) {
            this.course.set( 'id', courseID );
            this.course.fetch( { 
                'reset': true,
                'success': _.bind( function() {
                    this.requests.fetch( { 'reset': true } );
                }, this )
            } );
            this.delegateEvents();
        }, this ) );
        this.listenTo( this.course, 'request', this.renderLoading );
    },
    newWebSocketRequest: function( data ) {
        if ( data.course != this.course.get('id' ) ) {
           return; 
        }
        var request = new Request( { 'id': data.id }, { 'course': this.course } );
        request.fetch( {
            'success': _.bind( function( model ) {
                this.requests.add( model, { 'merge': true } ); 
            }, this )
        } );
    },
    removeWebSocketRequest: function( data ) {
        if ( data.course != this.course.get('id' ) ) {
           return; 
        }
        try {
            this.requests.get( data.id ).trigger( 'destroy' );
        } catch ( e ) {
        }
    },
    newWebSocketOfficeHour: function( data ) {
        if ( data.course != this.course.get('id' ) ) {
           return; 
        }

        var officeHour = new OfficeHour( { 'id': data.id }, { 'course': this.course } );
        officeHour.fetch( {
            'success': _.bind( function( model ) {
                this.officeHours.add( model, { 'merge': true } );
            }, this )
        } );

    },
    removeWebSocketOfficeHour: function( data ) {
        if ( data.course != this.course.get('id' ) ) {
           return; 
        }
        
        try {
            this.officeHours.get( data.id ).trigger( 'destroy' );
        } catch ( e ) {
        }
    },
    newRequest: function( request ) {
        this.requests.add( request );
    },
    renderLoading: function( model ) {
        /* If this event is propagated from an inner model, ignore it */
        if ( model !== this.course ) return;
        this.$el.html( this.loadingTemplate() );
    },
    render: function() {
        this.$el.html( this.template( this.course.attributes ) );

        this.$el.find( '.requests-container' ).html( this.requestsView.render().$el );
        this.$el.find( '.make-request-container' ).html( this.makeRequestView.render().$el );
        this.$el.find( '.ta-container' ).html( this.TAsView.render().$el );
        this.$el.find( '.office-hours-container' ).html( this.officeHoursView.render().$el );

        this.delegateEvents();
        return this;
    }
});

module.exports = CourseView;
