var CourseDependentModel = require( './CourseDependentModel' );

var Request = CourseDependentModel.extend( {
    endRoute: 'requests/'
} );

module.exports = Request;

