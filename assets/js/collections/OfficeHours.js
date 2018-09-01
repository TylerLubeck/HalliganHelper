var CourseDependentCollection = require( './CourseDependentCollection' );
var OfficeHour = require( './../models/OfficeHour' );

var OfficeHours = CourseDependentCollection.extend({
    model: OfficeHour,
    url: function() {
        return '/api/v3/school/courses/' + this.course.get( 'id' ) + '/officehours/';
    },
});

module.exports = OfficeHours;
