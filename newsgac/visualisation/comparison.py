from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource, LabelSet)
import math

from newsgac.pipelines.models import Result
from newsgac.visualisation.resultvisualiser import heatMapFromResult


__author__ = 'abilgin'


class PipelineComparator:

    def __init__(self, ace):
        self.ace = ace
        self.pipelines = pipelines = ace.pipelines
        self.pipeline_titles = []
        for pipeline in self.pipelines:
            self.pipeline_titles.append(pipeline.display_title)

        # construct data_sources x axis pipeline names, y axis result
        self.fmeasure = {}
        self.precision = {}
        self.recall = {}
        self.other = {}

        self.fmeasure['weighted'] = []
        self.fmeasure['micro'] = []
        self.fmeasure['macro'] = []

        self.precision['weighted'] = []
        self.precision['micro'] = []
        self.precision['macro'] = []

        self.recall['weighted'] = []
        self.recall['micro'] = []
        self.recall['macro'] = []

        self.other['cross_validation_accuracies'] = []
        self.other['kappas'] = []

        predictions = ace.predictions.get().transpose()

        for key, pipeline in enumerate(self.pipelines):
            true_labels = [article.label for article in ace.data_source.articles]
            predicted_labels = predictions[key]
            results = Result.from_prediction(true_labels, predicted_labels)
            # results = pipeline.result
            self.fmeasure['weighted'].append(results.fmeasure_weighted)
            self.fmeasure['micro'].append(results.fmeasure_micro)
            self.fmeasure['macro'].append(results.fmeasure_macro)

            self.precision['weighted'].append(results.precision_weighted)
            self.precision['micro'].append(results.precision_micro)
            self.precision['macro'].append(results.precision_macro)

            self.recall['weighted'].append(results.recall_weighted)
            self.recall['micro'].append(results.recall_micro)
            self.recall['macro'].append(results.recall_macro)

            self.other['cross_validation_accuracies'].append(results.accuracy)
            self.other['kappas'].append(results.cohens_kappa)


    def resultsComparisonUsingPipelines(self):
        colors = ["#E74C3C", "#9B59B6", "#1ABC9C", "#F39C12", "#2980B9"]
        p_fmeasure = self.generate_plots_for_metric(self.fmeasure, "F1 Scores", colors[0])
        p_precision= self.generate_plots_for_metric(self.precision, "Precision", colors[1])
        p_recall = self.generate_plots_for_metric(self.recall, "Recall", colors[2])
        p_other = self.generate_plots_for_other_metric(self.other, "Other", colors[3])

        plots = []
        plots.extend(p_fmeasure)
        plots.extend(p_precision)
        plots.extend(p_recall)
        plots.extend(p_other)

        return list(plots)


    def generate_plots_for_metric(self, metric, title, color='navy'):
        figures = []
        types = ['weighted', 'micro', 'macro']

        metric_data = {'pipelines': self.pipeline_titles,
                       'weighted': metric['weighted'],
                       'micro': metric['micro'],
                       'macro': metric['macro']}
        metric_source = ColumnDataSource(data=metric_data)

        if len(self.pipeline_titles) < 7:
            height = 300
        else:
            height = 50*len(self.pipeline_titles)

        for type in types:
            p = figure(y_range=self.pipeline_titles, plot_height=height, title=title + ' (' + type + ')',
                       plot_width = 400, x_range=[0,1.05], toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

            p.hbar(y=self.pipeline_titles, height=0.5, left=0, right=metric[type], color=color)

            labels = LabelSet(x=type, y='pipelines', text=type, level='glyph', text_font_size="7pt",
                              x_offset=2, y_offset= -1, source=metric_source, render_mode='canvas')

            p.y_range.range_padding = 0.4
            p.xgrid.grid_line_color = None
            p.legend.location = "top_left"
            p.legend.orientation = "horizontal"
            p.xaxis.major_label_orientation = "horizontal"

            p.add_layout(labels)

            p.min_border_left = 100
            p.min_border_top = 20
            p.min_border_bottom = 20

            figures.append(p)

        return figures

    def generate_plots_for_other_metric(self, metric, title, color='navy'):

        figures = []
        types = ['cross_validation_accuracies', 'kappas']
        subtitles = ['Accuracy', 'Cohen\'s kappa']

        metric_data = {'pipelines': self.pipeline_titles,
                       'cross_validation_accuracies': metric['cross_validation_accuracies'],
                       'kappas': metric['kappas']}
        metric_source = ColumnDataSource(data=metric_data)

        if len(self.pipeline_titles) < 7:
            height = 300
        else:
            height = 50*len(self.pipeline_titles)

        i = 0
        for type in types:
            p = figure(y_range=self.pipeline_titles, plot_height=height, title=title + ' (' + subtitles[i] + ')',
                       plot_width = 400, x_range=[0,1.05], toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

            p.hbar(y=self.pipeline_titles, height=0.5, left=0, right=metric[type], color=color)

            labels = LabelSet(x=type, y='pipelines', text=type, level='glyph', text_font_size="7pt",
                              x_offset=2, y_offset= -1, source=metric_source, render_mode='canvas')

            p.y_range.range_padding = 0.4
            p.xgrid.grid_line_color = None
            p.legend.location = "top_left"
            p.legend.orientation = "horizontal"
            p.xaxis.major_label_orientation = "horizontal"

            p.add_layout(labels)

            figures.append(p)

            i += 1

        return figures


    def combineHeatMapPlotsForAllPipelines(self):

        plots = []

        if len(self.pipelines) == 2:
            ds_param = 0.7
        elif len(self.pipelines) > 2:
            ds_param = 0.55
        else:
            ds_param = 1/math.sqrt(len(self.pipelines))


        predictions = self.ace.predictions.get().transpose()

        for key, pipeline in enumerate(self.pipelines):
            true_labels = [article.label for article in self.ace.data_source.articles]
            predicted_labels = predictions[key]
            results = Result.from_prediction(true_labels, predicted_labels)

            # results = pipeline.result
            plot = heatMapFromResult(
                pipeline=pipeline,
                normalisation_flag=True,
                title=pipeline.display_title,
                ds_param = ds_param
            )

            # script, div = components(plot)
            plots.append(plot)

        overview_layout = gridplot(list(plots), ncols=3)
        script, div = components(overview_layout)

        return script, div


    def performComparison(self):
        scripts = []
        divs = []

        plots = []
        plots.extend(self.resultsComparisonUsingPipelines())
        overview_layout = gridplot(plots, ncols=3)
        script, div = components(overview_layout)
        scripts.append(script)
        divs.append(div)

        return scripts, divs


