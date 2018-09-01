var DRFModel = require( './DRFModel' );

var CourseDependentModel = DRFModel.extend( {
    initialize: function( attrs, options ) {
        this.course = options.course;
    },
    endRoute: '',
    urlRoot: function() {
        if( this.collection ) {
            return this.collection.url();
        }

        var courseID = this.course.get('id');
        return '/api/v3/school/courses/' + courseID + '/' + this.endRoute;
    },

} );

module.exports = CourseDependentModel;
