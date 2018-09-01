var CourseDependentModel = require( './CourseDependentModel' );

var OfficeHour = CourseDependentModel.extend( {
    endRoute: 'officehours/',
} );

module.exports = OfficeHour;
