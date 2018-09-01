var Backbone = require('backbone');

var AppRouter = Backbone.Router.extend({
    routes: {
        'course/:id': 'course',
        'dashboard': 'dashboard',
        'profile': 'profile',
        'logout': 'logout',
    },
});

module.exports = AppRouter;
