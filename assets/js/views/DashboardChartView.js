var Backbone = require('backbone');
var _ = require('underscore');
var $ = require('jquery');
var Chart = require('chart.js');

var DashboardChartView = Backbone.View.extend({
    className: 'dashboard-card',
    template: _.template( require( './../templates/dashboard-chart-template' ) ),
    initialize: function( options ) {
        var changes = 'change:active_ta_count change:current_request_count';
        //this.listenTo( this.model, changes, this.addDataPoint );
        this.listenTo( this.model, changes, this.render );
    },
    addDataPoint: function() {
        
    },
    renderChart: function() {
        canvasContext = this.$el.find( '.course-dashboard-canvas' )
            .get( 0 ).getContext( "2d" );

        var initialData = {
            labels: ['requests', 'tas'],
            datasets: [
                {
                    label: 'Requests',
                    fillColor: "rgba(220,220,220,0.2)",
                    strokeColor: "rgba(220,220,220,1)",
                    pointColor: "rgba(220,220,220,1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(220,220,220,1)",
                    data: [ this.model.current_request_count, this.model.current_request_count ]
                },
                {
                    label: 'TAs',
                    fillColor: "rgba(220,220,220,0.2)",
                    strokeColor: "rgba(220,220,220,1)",
                    pointColor: "rgba(220,220,220,1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(220,220,220,1)",
                    data: [ this.model.active_ta_count, this.model.active_ta_count ]
                },
            ]
        };

        this.chart = new Chart( canvasContext ).Line( initialData, { 'responsive': true } );
    },
    render: function() {
        this.$el.html( this.template( this.model.attributes ) );
        //this.renderChart();
        return this;
    }
    
});

module.exports = DashboardChartView;
