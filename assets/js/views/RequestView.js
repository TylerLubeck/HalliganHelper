var Backbone = require('backbone');
var _ = require('underscore');
var $ = require('jquery');

var RequestView = Backbone.View.extend({
    className: 'request-listing',
    template: _.template( require( './../templates/request-template' ) ),
    editTemplate: _.template( require( './../templates/edit-request-template' ) ),
    events: {
        'keyup .problem-input': 'editedRequest',
        'keyup .location-input': 'editedRequest',
        'click .primary.button': 'primaryClick',
        'click .secondary.button': 'secondaryClick',
    },

    initialize: function() {
        this.listenTo( this.model, 'change', this.handleChange );
        this.listenTo( this.model, 'destroy', this.remove );
    },

    removeView: function() {
        var transitionFinishedEvents = 'transitionend webkitTransitionEnd oTransitionEnd otransitionend MSTransitionEnd';
        this.model.trigger( 'destroy' );
        /*
        this.$el.addClass( 'cancelled' )
            .on( transitionFinishedEvents, function() {
                $(this).height($(this).height());
                $(this).height(0).css({'margin':'0'}).on( transitionFinishedEvents, _.bind( function() {
                    this.remove();
                }, this ) );
            } );
            */
    },
    editedRequest: function( e ) {
        if ( e.keyCode == 13 ) {
            this.$el.find( '.primary.button' ).click();
        }
        var problem = this.$el.find( '.problem-input' ).val();
        var loc = this.$el.find( '.location-input' ).val();
        var primaryButton = this.$el.find( '.primary.button' );
        
        if ( problem != this.model.get( 'question' ) ||
             loc != this.model.get( 'where_located' ) ) {
            primaryButton.removeAttr( 'disabled' );
        } else {
            primaryButton.attr( 'disabled', 'disabled' );
        }
    },
    primaryClick: function( e ) {
        if( $( e.currentTarget ).data( 'save-edit' ) ) {
            var question = this.$el.find( '.problem-input' ).val();
            var loc = this.$el.find( '.location-input' ).val();
            this.model.save( { 'question': question, 'where_located': loc } );
        }
        else if ( this.model.get( 'owned_by_me' ) ) {
            this.model.save( { 'cancelled': true },
                             {
                                'success': _.bind( this.removeView, this ),
                                'error': _.bind( function( model, response ) {
                                    if ( response.status === 404 ) {
                                        this.removeView();
                                    }
                                }, this ),
                             } 
                           );
            
        } else if ( this.model.get( 'can_ta_for' ) ) {
            this.model.save( { 'solved': true },
                             {
                                'success': _.bind( this.removeView, this ),
                                'error': _.bind( function( model, response ) {
                                    if ( response.status === 404 ) {
                                        this.removeView();
                                    }
                                }, this ),
                             } 
                           );
        }

    },
    secondaryClick: function( e ) {
        if ( $( e.currentTarget ).data( 'cancel-edit' )) {
            this.render();
        }
        else if ( this.model.get( 'owned_by_me' ) ) {
            this.renderEdit();
        } else if ( this.model.get( 'can_ta_for' ) ) {
            this.model.save( { 'checked_out': true } );
        }
    },
    handleChange: function( model ) {

        if ( model.hasChanged( 'checked_out' ) ) {
            /* If we've checked it out, we just want to toggle the class
             * so we get the nice animation
             */
            this.$el.find( '.request-information' )
                .toggleClass( 'checked-out', model.get( 'checked_out' ) );

            if ( this.model.get( 'can_ta_for' ) ) {
                this.$el.find( '.secondary.button' ).remove(); 
            }
        } else {
            /* Otherwise, re-render the whole thing */
            this.render();
        }
    },
    renderEdit: function() {
        this.$el.html( this.editTemplate( this.model.attributes ) );
        return this;
    },
    render: function() {
        this.$el.html( this.template( this.model.attributes ) ); 
        return this;
    }
});

module.exports = RequestView;
