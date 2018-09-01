var Backbone = require('backbone');
var _ = require('underscore');
var $ = require('jquery');

var RequestView = require( './RequestView' );

var RequestsView = Backbone.View.extend({
    template: _.template( require( './../templates/requests-view-template' ) ),
    loadingTemplate: _.template( require( './../templates/loading-template' ) ),
    initialize: function( options ) {
        this.listenTo( this.collection, 'reset', this.render );
        this.listenTo( this.collection, 'add', this.renderRequest );
        this.listenTo( this.collection, 'request', this.renderLoading );
    },
    renderLoading: function( collection ) {
        /* If this event is propagated from an inner model, ignore it */
        if ( collection !== this ) return;
        this.$el.html( this.loadingTemplate() );
    },
    renderRequest: function( request ) {
        var requestView = new RequestView( { model: request } ); 
        this.$el.append( requestView.render().$el );
    },
    render: function() {
        this.$el.html( this.template() );
        this.collection.each( this.renderRequest, this ); 
        return this;
    }
});

module.exports = RequestsView;
