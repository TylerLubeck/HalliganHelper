var Backbone = require('backbone');
var _ = require('underscore');
var $ = require('jquery');

var TA = require ( './../models/TA' );

var TAView = Backbone.View.extend({
    className: 'ta-card',
    template: _.template( require( './../templates/ta-template' ) ),

    initialize: function( options ) {
        this.listenTo( this.model, 'change', this.render ); 
    },

    render: function() {
        this.$el.html( this.template( this.model.attributes ) );
        return this;
    }
});

module.exports = TAView;



