var Backbone = require('backbone');
var _ = require('underscore');

var OfficeHourView = Backbone.View.extend({
    className: 'oh-card',
    template: _.template( require( './../templates/office-hour-template' ) ),

    events: {
        'click .cancel-button': 'cancel',
    },

    initialize: function( options ) {
        this.listenTo( this.model, 'change', this.render );
        this.listenTo( this.model, 'destroy', this.remove );
    },
    
    cancel: function() {
        this.model.destroy();
    },

    render: function() {
        this.$el.html( this.template( this.model.attributes ) );
        return this;
    }
});

module.exports = OfficeHourView;



