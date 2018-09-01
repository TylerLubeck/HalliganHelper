var Backbone = require( 'backbone' );
var _ = require( 'underscore' );

var moment = require( 'moment' );

var OfficeHourView = require( './OfficeHourView' );
var OfficeHour = require( './../models/OfficeHour' );

var OfficeHoursView = Backbone.View.extend({
    className: 'oh-grid',
    template: _.template( require( './../templates/office-hours-template' ) ),
    loadingTemplate: _.template( require( './../templates/loading-template' ) ),

    events: {
        'click .button': 'goOnDuty',
        'keyup input': 'inputChanged',
        'change select': 'inputChanged',
    },

    initialize: function( options ) {
        this.course = options.course;
        this.listenTo( this.collection, 'add', this.renderOfficeHour );
        this.listenTo( this.collection, 'reset', this.render );
        this.listenTo( this.collection, 'request', this.renderLoading );
    },
    
    inputChanged: function( e ) {
        $( e.target ).parents( 'label' ).removeClass( 'error' );
        this.submitButton.removeAttr( 'disabled' );
    },
    goOnDuty: function() {
        this.submitButton.attr( 'disabled', 'disabled' );
        var loc = this.onDutyLocation.val();
        var hours = this.onDutyHours.val();
        var minutes = this.onDutyMinutes.val();
        var now = moment();
        now = now.add( hours, 'hours' ).add( minutes, 'minutes' );

        var officeHour = new OfficeHour( 
            {
                'location': loc,
                'end_time': now.toISOString()
            },
            { 'course': this.course }
        );

        var collection = this.collection;
        officeHour.save( {}, {
            'success': _.bind( function( model ) {
                this.submitButton.removeAttr( 'disabled' );
                collection.add( model );
                this.onDutyLocation.val( '' );
                this.onDutyLocation.parent().removeClass( 'error' );
                this.onDutyHours.val( 0 );
                this.onDutyMinutes.val( 0 );
                this.onDutyHours.parents( 'label' ).removeClass( 'error' );
                this.$el.find( '.submission-error' ).empty();
            }, this ),
            'error': _.bind( function( model, response, options ) {
                var err = '';
                if ( 'location' in response.responseJSON ) {
                    err = response.responseJSON.location[0];
                    this.onDutyLocation.parent().addClass( 'error' ); 
                    this.$el.find( '.location-error' ).text( err );
                }
                if( 'end_time' in response.responseJSON ) {
                    err = response.responseJSON.end_time[0];
                    this.onDutyHours.parents( 'label' ).addClass( 'error' );
                    this.$el.find( '.hours-error' ).text( 'This needs to be in the future' );
                }
                if( 'non_field_errors' in response.responseJSON ) {
                    err = response.responseJSON.non_field_errors[0];
                    this.$el.find( '.submission-error' ).text( err );
                    this.submitButton.removeAttr( 'disabled' );
                } else {
                    this.$el.find( '.submission-error' ).empty();
                }
            }, this )
        } );
    },
    renderLoading: function( collection ) {
        /* If this event is propagated from an inner model, ignore it */
        if ( collection !== this ) return;
        this.$el.html( this.loadingTemplate() );
    },
    renderOfficeHour: function( officeHour ) {
        var ohView = new OfficeHourView( { 'model': officeHour } );
        this.$el.append( ohView.render().$el );
    },
    render: function() {
        this.$el.html( this.template( { 
            'am_a_ta': this.course.get( 'am_a_ta' )
        }) );
        this.submitButton = this.$el.find( '.button' );
        this.onDutyLocation = this.$el.find( '.on-duty-location' );
        this.onDutyHours = this.$el.find( '.on-duty-hours' );
        this.onDutyMinutes = this.$el.find( '.on-duty-minutes' );

        this.collection.each( this.renderOfficeHour, this );
        this.delegateEvents();
        return this;
    }
});

module.exports = OfficeHoursView;



