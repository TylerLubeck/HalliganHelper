var Backbone = require('backbone');

var CourseDependentCollection = Backbone.Collection.extend( {
    initialize: function( models, options ) {
        this.course = options.course;
        
        /**
         * Why can't we bind this directly to `this.fetch`?
         * Good question, but when we do we get blow the call stack so...
         */
        this.listenTo( this.course, 'change:id', this.changed );
    },
    changed: function()  {
        this.fetch( { 'reset': true } );
    },
} );

module.exports = CourseDependentCollection;
