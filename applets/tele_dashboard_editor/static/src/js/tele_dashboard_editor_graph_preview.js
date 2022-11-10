tele.define('tele_dashboard_editor_list.tele_dashboard_graph_preview', function(require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var utils = require('web.utils');
    var config = require('web.config');
    var field_utils = require('web.field_utils');
    var TeleGlobalFunction = require('tele_dashboard_editor.TeleGlobalFunction');

    var QWeb = core.qweb;

    var MAX_LEGEND_LENGTH = 25 * (Math.max(1, config.device.size_class));

    var TeleGraphPreview = AbstractField.extend({
        supportedFieldTypes: ['char'],

        resetOnAnyFieldChange: true,

        jsLibs: [
            '/tele_dashboard_editor/static/lib/js/Chart.bundle.min.js',
            '/tele_dashboard_editor/static/lib/js/chartjs-plugin-datalabels.js'
        ],
        cssLibs: [
            '/tele_dashboard_editor/static/lib/css/Chart.min.css'
        ],

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
        },

        start: function() {
            var self = this;
            self.tele_set_default_chart_view();
            core.bus.on("DOM_updated", this, function() {
                if (self.shouldRenderChart && $.find('#ksMyChart').length > 0) self.renderChart();
            });
            Chart.plugins.unregister(ChartDataLabels);
            return this._super();
        },

        tele_set_default_chart_view: function() {
            Chart.plugins.register({
                afterDraw: function(chart) {
                    if (chart.data.labels.length === 0) {
                        // No data is present
                        var ctx = chart.chart.ctx;
                        var width = chart.chart.width;
                        var height = chart.chart.height
                        chart.clear();

                        ctx.save();
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.font = "3rem 'Lucida Grande'";
                        ctx.fillText('No data available', width / 2, height / 2);
                        ctx.restore();
                    }
                }
            });

            Chart.Legend.prototype.afterFit = function() {
                var chart_type = this.chart.config.type;
                if (chart_type === "pie" || chart_type === "doughnut") {
                    this.height = this.height;
                } else {
                    this.height = this.height + 20;
                };
            }
        },

        _render: function() {
            this.$el.empty()
            if (this.recordData.tele_dashboard_item_type !== 'tele_tile' && this.recordData.tele_dashboard_item_type !== 'tele_kpi' && this.recordData.tele_dashboard_item_type !== 'tele_list_view' && this.recordData.tele_dashboard_item_type !== 'tele_to_do') {
                if (this.recordData.tele_model_id) {
                    if (this.recordData.tele_chart_groupby_type == 'date_type' && !this.recordData.tele_chart_date_groupby) {
                        return this.$el.append($('<div>').text("Select Group by date to create chart based on date groupby"));
                    } else if (this.recordData.tele_chart_data_count_type === "count" && !this.recordData.tele_chart_relation_groupby) {
                        this.$el.append($('<div>').text("Select Group By to create chart view"));
                    } else if (this.recordData.tele_chart_data_count_type !== "count" && (this.recordData.tele_chart_measure_field.count === 0 || !this.recordData.tele_chart_relation_groupby)) {
                        this.$el.append($('<div>').text("Select Measure and Group By to create chart view"));
                    } else if (!this.recordData.tele_chart_data_count_type) {
                        this.$el.append($('<div>').text("Select Chart Data Count Type"));
                    } else {
                        this._getChartData();
                    }
                } else {
                    this.$el.append($('<div>').text("Select a Model first."));
                }

            }

        },

        _getChartData: function() {
            var self = this;
            self.shouldRenderChart = true;
            var field = this.recordData;
            var tele_chart_name;
            if (field.name) tele_chart_name = field.name;
            else if (field.tele_model_name) tele_chart_name = field.tele_model_id.data.display_name;
            else tele_chart_name = "Name";

            this.chart_type = this.recordData.tele_dashboard_item_type.split('_')[1];
            this.chart_data = JSON.parse(this.recordData.tele_chart_data);

            if (field.tele_chart_cumulative_field){

                for (var i=0; i< this.chart_data.datasets.length; i++){
                    var tele_temp_com = 0
                    var datasets = {}
                    var data = []
                    if (this.chart_data.datasets[i].tele_chart_cumulative_field){
                        for (var j=0; j < this.chart_data.datasets[i].data.length; j++)
                            {
                                tele_temp_com = tele_temp_com + this.chart_data.datasets[i].data[j];
                                data.push(tele_temp_com);
                            }
                            datasets.label =  'Cumulative' + this.chart_data.datasets[i].label;
                            datasets.data = data;
                             if (field.tele_chart_cumulative){
                                datasets.type =  'line';
                            }
                            this.chart_data.datasets.push(datasets);
                    }
                }
            }
            if (field.tele_chart_is_cumulative && field.tele_chart_data_count_type == 'count' && field.tele_dashboard_item_type === 'tele_bar_chart'){


                    var tele_temp_com = 0
                    var data = []
                    var datasets = {}

                        for (var j=0; j < this.chart_data.datasets[0].data.length; j++)
                            {
                                tele_temp_com = tele_temp_com + this.chart_data.datasets[0].data[j];
                                data.push(tele_temp_com);
                            }
                            datasets.label =  'Cumulative' + this.chart_data.datasets[0].label;
                            datasets.data = data;
                            if (field.tele_chart_cumulative){
                                datasets.type =  'line';
                            }
                            this.chart_data.datasets.push(datasets);


            }

            var $chartContainer = $(QWeb.render('tele_chart_form_view_container', {
                tele_chart_name: tele_chart_name
            }));
            this.$el.append($chartContainer);

            switch (this.chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    this.chart_family = "circle";
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                case "area":
                    this.chart_family = "square"
                    break;
                default:
                    this.chart_family = "none";
                    break;
            }

            if (this.chart_family === "circle") {
                if (this.chart_data && this.chart_data['labels'].length > 30) {
                    this.$el.find(".card-body").empty().append($("<div style='font-size:20px;'>Too many records for selected Chart Type. Consider using <strong>Domain</strong> to filter records or <strong>Record Limit</strong> to limit the no of records under <strong>30.</strong>"));
                    return;
                }
            }
            if ($.find('#ksMyChart').length > 0) {
                this.renderChart();
            }
        },

        renderChart: function() {
            var self = this;
            if (this.recordData.tele_chart_measure_field_2.count && this.recordData.tele_dashboard_item_type === 'tele_bar_chart') {
                var self = this;
                var scales = {}
                scales.yAxes = [{
                        type: "linear",
                        display: true,
                        position: "left",
                        id: "y-axis-0",
                        gridLines: {
                            display: true
                        },
                        labels: {
                            show: true,
                        }
                    },
                    {
                        type: "linear",
                        display: true,
                        position: "right",
                        id: "y-axis-1",
                        labels: {
                            show: true,
                        },
                        ticks: {
                            beginAtZero: true,
                            callback: function(value, index, values) {
                                var tele_selection = self.chart_data.tele_selection;
                                if (tele_selection === 'monetary') {
                                    var tele_currency_id = self.chart_data.tele_currency;
                                    var tele_data = TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits);
                                        tele_data = TeleGlobalFunction.tele_monetary(tele_data, tele_currency_id);
                                    return tele_data;
                                } else if (tele_selection === 'custom') {
                                    var tele_field = self.chart_data.tele_field;
                                    return TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits) + ' ' + tele_field;
                                }else {
                                    return TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits);
                                }
                            },
                        }
                    }
                ]

            }
            var chart_plugin = [];
            if (this.recordData.tele_show_data_value) {
                chart_plugin.push(ChartDataLabels);
            }
            this.teleMyChart = new Chart($.find('#ksMyChart')[0], {
                type: this.chart_type === "area" ? "line" : this.chart_type,
                plugins: chart_plugin,
                data: {
                    labels: this.chart_data['labels'],
                    datasets: this.chart_data.datasets,
                },
                options: {
                    maintainAspectRatio: false,
                    animation: {
                        easing: 'easeInQuad',
                    },
                    legend: {
                            display: this.recordData.tele_hide_legend
                        },
                    layout: {
                        padding: {
                            bottom: 0,
                        }
                    },
                    scales: scales,
                    plugins: {
                        datalabels: {
                            backgroundColor: function(context) {
                                return context.dataset.backgroundColor;
                            },
                            borderRadius: 4,
                            color: 'white',
                            font: {
                                weight: 'bold'
                            },
                            anchor: 'center',
                            textAlign: 'center',
                            display: 'auto',
                            clamp: true,
                            formatter: function(value, ctx) {
                                let sum = 0;
                                let dataArr = ctx.dataset.data;
                                dataArr.map(data => {
                                    sum += data;
                                });
                                let percentage = sum === 0 ? 0 + "%" : (value * 100 / sum).toFixed(2) + "%";
                                if(self.recordData.tele_data_label_type == 'value'){
                                    percentage = value;
                                }
                                return percentage;
                            },
                        },
                    },

                }
            });
            if (this.chart_data && this.chart_data["datasets"].length > 0) {
                self.teleChartColors(this.recordData.tele_chart_item_color, this.teleMyChart, this.chart_type, this.chart_family, this.recordData.tele_show_data_value);
            }
        },

        teleHideFunction: function(options, recordData, teleChartFamily, chartType) {
            return options;
        },

        teleChartColors: function(palette, teleMyChart, teleChartType, teleChartFamily, tele_show_data_value) {
            var self = this;
            var currentPalette = "cool";
            if (!palette) palette = currentPalette;
            currentPalette = palette;

            /*Gradients
              The keys are percentage and the values are the color in a rgba format.
              You can have as many "color stops" (%) as you like.
              0% and 100% is not optional.*/
            var gradient;
            switch (palette) {
                case 'cool':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [220, 237, 200, 1],
                        45: [66, 179, 213, 1],
                        65: [26, 39, 62, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'warm':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [254, 235, 101, 1],
                        45: [228, 82, 27, 1],
                        65: [77, 52, 47, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'neon':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [255, 236, 179, 1],
                        45: [232, 82, 133, 1],
                        65: [106, 27, 154, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;

                case 'default':
                    var color_set = ['#F04F65', '#f69032', '#fdc233', '#53cfce', '#36a2ec', '#8a79fd', '#b1b5be', '#1c425c', '#8c2620', '#71ecef', '#0b4295', '#f2e6ce', '#1379e7']
            }



            //Find datasets and length
            var chartType = teleMyChart.config.type;

            switch (chartType) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var datasets = teleMyChart.config.data.datasets[0];
                    var setsCount = datasets.data.length;
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                    var datasets = teleMyChart.config.data.datasets;
                    var setsCount = datasets.length;
                    break;
            }

            //Calculate colors
            var chartColors = [];

            if (palette !== "default") {
                //Get a sorted array of the gradient keys
                var gradientKeys = Object.keys(gradient);
                gradientKeys.sort(function(a, b) {
                    return +a - +b;
                });
                for (var i = 0; i < setsCount; i++) {
                    var gradientIndex = (i + 1) * (100 / (setsCount + 1)); //Find where to get a color from the gradient
                    for (var j = 0; j < gradientKeys.length; j++) {
                        var gradientKey = gradientKeys[j];
                        if (gradientIndex === +gradientKey) { //Exact match with a gradient key - just get that color
                            chartColors[i] = 'rgba(' + gradient[gradientKey].toString() + ')';
                            break;
                        } else if (gradientIndex < +gradientKey) { //It's somewhere between this gradient key and the previous
                            var prevKey = gradientKeys[j - 1];
                            var gradientPartIndex = (gradientIndex - prevKey) / (gradientKey - prevKey); //Calculate where
                            var color = [];
                            for (var k = 0; k < 4; k++) { //Loop through Red, Green, Blue and Alpha and calculate the correct color and opacity
                                color[k] = gradient[prevKey][k] - ((gradient[prevKey][k] - gradient[gradientKey][k]) * gradientPartIndex);
                                if (k < 3) color[k] = Math.round(color[k]);
                            }
                            chartColors[i] = 'rgba(' + color.toString() + ')';
                            break;
                        }
                    }
                }
            } else {
                for (var i = 0, counter = 0; i < setsCount; i++, counter++) {
                    if (counter >= color_set.length) counter = 0; // reset back to the beginning

                    chartColors.push(color_set[counter]);
                }

            }

            var datasets = teleMyChart.config.data.datasets;
            var options = teleMyChart.config.options;

            options.legend.labels.usePointStyle = true;
            if (teleChartFamily == "circle") {
                if (tele_show_data_value) {
                    options.legend.position = 'top';
                    options.layout.padding.top = 10;
                    options.layout.padding.bottom = 20;
                } else {
                    options.legend.position = 'bottom';
                }

                options = this.teleHideFunction(options, this.recordData, teleChartFamily, chartType);
                options.plugins.datalabels.align = 'center';
                options.plugins.datalabels.anchor = 'end';
                options.plugins.datalabels.borderColor = 'white';
                options.plugins.datalabels.borderRadius = 25;
                options.plugins.datalabels.borderWidth = 2;
                options.plugins.datalabels.clamp = true;
                options.plugins.datalabels.clip = false;
                options.tooltips.callbacks = {
                    title: function(tooltipItem, data) {
                        var tele_self = self;
                        var k_amount = data.datasets[tooltipItem[0].datasetIndex]['data'][tooltipItem[0].index];
                        var tele_selection = tele_self.chart_data.tele_selection;
                        if (tele_selection === 'monetary') {
                            var tele_currency_id = tele_self.chart_data.tele_currency;
                            k_amount = TeleGlobalFunction.tele_monetary(k_amount, tele_currency_id);
                            return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount
                        } else if (tele_selection === 'custom') {
                            var tele_field = tele_self.chart_data.tele_field;
                            //                                                        tele_type = field_utils.format.char(tele_field);
                            k_amount = field_utils.format.float(k_amount, Float64Array, {digits: [0, self.recordData.tele_precision_digits]});
                            return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount + " " + tele_field;
                        } else {
                            k_amount = field_utils.format.float(k_amount, Float64Array, {digits: [0, self.recordData.tele_precision_digits]});
                            return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount
                        }
                    },
                    label: function(tooltipItem, data) {
                        return data.labels[tooltipItem.index];
                    },

                }
                for (var i = 0; i < datasets.length; i++) {
                    datasets[i].backgroundColor = chartColors;
                    datasets[i].borderColor = "rgba(255,255,255,1)";
                }
                if (this.recordData.tele_semi_circle_chart && (chartType === "pie" || chartType === "doughnut")) {
                    options.rotation = 1 * Math.PI;
                    options.circumference = 1 * Math.PI;
                }
            } else if (teleChartFamily == "square") {
                options = this.teleHideFunction(options, this.recordData, teleChartFamily, chartType);

                options.scales.xAxes[0].gridLines.display = false;
                options.scales.yAxes[0].ticks.beginAtZero = true;
                options.plugins.datalabels.align = 'end';

                options.plugins.datalabels.formatter = function(value, ctx) {
                    var tele_self = self;
                    var tele_selection = self.chart_data.tele_selection;
                    if (tele_selection === 'monetary') {
                        var tele_currency_id = self.chart_data.tele_currency;
                        var tele_data = TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits);
                            tele_data = TeleGlobalFunction.tele_monetary(tele_data, tele_currency_id);
                        return tele_data;
                    } else if (tele_selection === 'custom') {
                        var tele_field = self.chart_data.tele_field;
                        return TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits) + ' ' + tele_field;
                    }else {
                        return TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits);
                    }
                };

                if (chartType === "line") {
                    options.plugins.datalabels.backgroundColor = function(context) {
                        return context.dataset.borderColor;
                    };
                }


                if (chartType === "horizontalBar") {
                    options.scales.xAxes[0].ticks.callback = function(value, index, values) {
                        var tele_self = self;
                        var tele_selection = self.chart_data.tele_selection;
                        if (tele_selection === 'monetary') {
                            var tele_currency_id = self.chart_data.tele_currency;
                            var tele_data = TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits);
                                tele_data = TeleGlobalFunction.tele_monetary(tele_data, tele_currency_id);
                            return tele_data;
                        } else if (tele_selection === 'custom') {
                            var tele_field = self.chart_data.tele_field;
                            return TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits) + ' ' + tele_field;
                        }else {
                            return TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits);
                        }
                    }
                    options.scales.xAxes[0].ticks.beginAtZero = true;
                } else {
                    options.scales.yAxes[0].ticks.callback = function(value, index, values) {
                        var tele_self = self;
                        var tele_selection = tele_self.chart_data.tele_selection;
                        var tele_selection = self.chart_data.tele_selection;
                        if (tele_selection === 'monetary') {
                            var tele_currency_id = self.chart_data.tele_currency;
                            var tele_data = TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits);
                                tele_data = TeleGlobalFunction.tele_monetary(tele_data, tele_currency_id);
                            return tele_data;
                        } else if (tele_selection === 'custom') {
                            var tele_field = self.chart_data.tele_field;
                            return TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits) + ' ' + tele_field;
                        }else {
                            return TeleGlobalFunction._onTeleGlobalFormatter(value, self.recordData.tele_data_format, self.recordData.tele_precision_digits);
                        }
                    }
                }
                options.tooltips.callbacks = {
                    label: function(tooltipItem, data) {
                        var tele_self = self;
                        var k_amount = data.datasets[tooltipItem.datasetIndex]['data'][tooltipItem.index];
                        var tele_selection = tele_self.chart_data.tele_selection;
                        if (tele_selection === 'monetary') {
                            var tele_currency_id = tele_self.chart_data.tele_currency;
                            k_amount = TeleGlobalFunction.tele_monetary(k_amount, tele_currency_id);
                            return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount
                        } else if (tele_selection === 'custom') {
                            var tele_field = tele_self.chart_data.tele_field;
                            // tele_type = field_utils.format.char(tele_field);
                            k_amount = field_utils.format.float(k_amount, Float64Array, {digits: [0, self.recordData.tele_precision_digits]});
                            return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount + " " + tele_field;
                        } else {
                            k_amount = field_utils.format.float(k_amount, Float64Array, {digits:[0,self.recordData.tele_precision_digits]});
                            return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount
                        }
                    }
                }

                for (var i = 0; i < datasets.length; i++) {
                    switch (teleChartType) {
                        case "bar":
                        case "horizontalBar":
                            if (datasets[i].type && datasets[i].type == "line") {
                                datasets[i].borderColor = chartColors[i];
                                datasets[i].backgroundColor = "rgba(255,255,255,0)";
                                datasets[i]['datalabels'] = {
                                    backgroundColor: chartColors[i],
                                }

                            } else {
                                datasets[i].backgroundColor = chartColors[i];
                                datasets[i].borderColor = "rgba(255,255,255,0)";
                                options.scales.xAxes[0].stacked = this.recordData.tele_bar_chart_stacked;
                                options.scales.yAxes[0].stacked = this.recordData.tele_bar_chart_stacked;
                            }
                            break;
                        case "line":
                            datasets[i].borderColor = chartColors[i];
                            datasets[i].backgroundColor = "rgba(255,255,255,0)";
                            break;
                        case "area":
                            datasets[i].borderColor = chartColors[i];
                            break;
                    }
                }

            }
            teleMyChart.update();
            if (this.$el.find('canvas').height() < 250) {
                this.$el.find('canvas').height(250);
            }
        },


    });
    registry.add('tele_dashboard_graph_preview', TeleGraphPreview);

    return {
        TeleGraphPreview: TeleGraphPreview,
    };

});