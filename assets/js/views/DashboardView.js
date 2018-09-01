var Backbone = require('backbone');
var _ = require('underscore');
var $ = require('jquery');

var DashboardChartView = require('./DashboardChartView');

var DashboardView = Backbone.View.extend({
    className: 'dashboard-view',
    template: _.template( require( './../templates/dashboard-template' ) ),
    initialize: function( options ) {
        this.webSocketHandler = options.webSocketHandler;
    },
    renderChart: function( course ) {
        var chartView = new DashboardChartView( { 'model': course, 
                                                  'webSocketHandler': this.webSocketHandler 
                                                } );
        this.grid.append( chartView.$el );
        chartView.render();
    },
    render: function() {
        this.$el.html( this.template( this.model.attributes ) );
        this.grid = this.$el.find( '.dashboard-grid' );
        this.model.courses.forEach( this.renderChart, this );
        return this;
    }
});

module.exports = DashboardView;
