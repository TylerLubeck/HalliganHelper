var DRFModel = require( './DRFModel' );

var Course = DRFModel.extend( {
    urlRoot: '/api/v3/school/courses/',
} );

module.exports = Course;
