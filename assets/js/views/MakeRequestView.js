var Backbone = require('backbone');
var _ = require('underscore');

var Request = require('./../models/Request');

var MakeRequestView = Backbone.View.extend({
    template: _.template( require( './../templates/make-request-template' ) ),
    events: {
        'keyup .problem-input': 'problemChanged',
        'keyup .location-input': 'locationChanged',
        'click .get-help-button': 'submit'
    },

    initialize: function( options ) {
        this.course = options.course;
    },
    checkForSubmit: function( e ) {
        if ( e.keyCode == 13 ) {
            this.submit();
        }
    },
    problemChanged: function( e ) {
        if ( this.problemInputRow.hasClass( 'error' ) && e.keyCode != 13 ) {
            this.problemInputRow.removeClass( 'error' );
        }
        this.problemCharCount.text( this.problemInput.val().length );
        this.checkForSubmit( e );
    },
    locationChanged: function( e ) {
        if ( this.locationInputRow.hasClass( 'error' ) && e.keyCode != 13 ) {
            this.locationInputRow.removeClass( 'error' );
        }
        this.locationCharCount.text( this.locationInput.val().length );
        this.checkForSubmit( e );
    },
    enableSubmit: function() {
        this.helpButton.each( function( _, btn ) {
            btn.removeAttribute( 'disabled' );
        } );
    },
    disableSubmit: function() {
        this.helpButton.each( function( _, btn ) {
            btn.setAttribute( 'disabled', 'disabled' );
        } );
    },
    submit: function() {
        var problem = this.problemInput.val();
        var loc = this.locationInput.val();

        this.disableSubmit();

        var request = new Request({'question': problem, 'where_located': loc}, 
                                  { 'course': this.course } );
        request.save({}, {
            'success': _.bind( function( model, response, options ) {
                this.enableSubmit();
                this.trigger( 'newRequest', model );
                this.render();
            }, this ),
            'error': _.bind( function( model, response, options ) {
                this.enableSubmit();
                var errorData = response.responseJSON;

                if( 'question' in errorData ) {
                    this.problemInputRow.addClass( 'error' );
                    this.$el.find( '.problem-error' ).text( errorData.question );
                }

                if( 'where_located' in errorData ) {
                    this.locationInputRow.addClass( 'error' );
                    this.$el.find( '.location-error' ).text( errorData.where_located );
                }

            }, this )
        } );
    },
    render: function() {
        this.$el.html( this.template( this.course.attributes ) );

        this.problemInput = this.$el.find( '.problem-input' );
        this.problemInputRow = this.$el.find( '.problem-input-row' );
        this.problemCharCount = this.$el.find( '.problem-char-count' );

        this.locationInput = this.$el.find( '.location-input' );
        this.locationInputRow = this.$el.find( '.location-input-row' );
        this.locationCharCount = this.$el.find( '.location-char-count' );

        this.helpButton = this.$el.find( '.get-help-button' );

        this.delegateEvents();

        return this;
    }
});

module.exports = MakeRequestView;

