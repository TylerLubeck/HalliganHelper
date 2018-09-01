var Backbone = require('backbone');
var CourseCollection = require('../collections/Courses');

var School = Backbone.Model.extend({
    url: '/api/v3/school/',
    
    initialize: function() {
        this.listenTo( this, 'change', this.convertCourses );
    },
    convertCourses: function() {
        this.courses = new CourseCollection( this.get( 'courses' ) );
    },
    save: function() {
       /* noop for schools, since they can't be changed. */ 
    },
});

module.exports = School;
