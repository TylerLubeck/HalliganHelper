var CourseDependentCollection = require( './CourseDependentCollection' );
var TA = require('./../models/TA');

var TAs = CourseDependentCollection.extend({
    model: TA,

    url: function() {
        return '/api/v3/school/courses/' + this.course.get( 'id' ) + '/tas/';
    }
});

module.exports = TAs;
