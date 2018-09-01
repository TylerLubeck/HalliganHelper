var CourseDependentCollection = require( './CourseDependentCollection' );
var Request = require('./../models/Request');

var Requests = CourseDependentCollection.extend({
    model: Request,

    url: function() {
        return '/api/v3/school/courses/' + this.course.get( 'id' ) + '/requests/';
    },
    comparator: function ( request ) {
        return request.get( 'when_asked' );
    }
});

module.exports = Requests;
