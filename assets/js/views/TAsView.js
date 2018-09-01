var Backbone = require( 'backbone' );
var _ = require( 'underscore' );
var TAView = require( './TAView' );

var TAsView = Backbone.View.extend({
    className: 'ta-grid',
    loadingTemplate: _.template( require( './../templates/loading-template' ) ),

    initialize: function( options ) {
        this.listenTo( this.collection, 'reset', this.render );
        this.listenTo( this.collection, 'add', this.renderTA );
        this.listenTo( this.collection, 'request', this.renderLoading );
    },
    renderLoading: function( collection ) {
        /* If this event is propagated from an inner model, ignore it */
        if ( collection !== this ) return;
        this.$el.html( this.loadingTemplate() );
    },
    renderTA: function( ta ) {
        var taView = new TAView( { model: ta } );
        this.$el.append( taView.render().$el );
    },
    render: function() {
        this.$el.empty();
        this.collection.each( this.renderTA, this );
        return this;
    }
});

module.exports = TAsView;
