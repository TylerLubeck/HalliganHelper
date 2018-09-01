var CourseDependentModel = require( './CourseDependentModel' );

var TA = CourseDependentModel.extend( { 
    endRoute: 'tas/',

    defaults : {
        'blurb': 'hello  hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello',
    },
} );

module.exports = TA;
