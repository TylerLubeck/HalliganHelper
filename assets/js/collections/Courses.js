var Backbone = require('backbone');
var Course = require('./../models/Course');

var CourseCollection = Backbone.Collection.extend({
    url: '/api/v3/school/courses',
    model: Course,
});

module.exports = CourseCollection;
