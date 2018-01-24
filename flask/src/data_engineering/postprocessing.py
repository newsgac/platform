from __future__ import division
from collections import OrderedDict
import numpy as np
from sklearn.metrics import confusion_matrix
import data_engineering.utils as DataUtils
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar,
    FixedTicker, FuncTickFormatter)
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.core.properties import value

from sklearn import metrics

__author__ = 'abilgin'

class Result(object):

    def __init__(self, y_test, y_pred):

        self.y_test = y_test
        self.y_pred = y_pred

        self.genre_names = []
        for number, name in DataUtils.genres.items():
            self.genre_names.append(''.join(name))

        self.confusion_matrix = confusion_matrix(self.y_test, self.y_pred)

        self.precision_weighted = format(metrics.precision_score(self.y_test, self.y_pred, average='weighted'), '.2f')
        self.precision_micro = format(metrics.precision_score(self.y_test, self.y_pred, average='micro'), '.2f')
        self.precision_macro = format(metrics.precision_score(self.y_test, self.y_pred, average='macro'), '.2f')

        self.recall_weighted =format(metrics.recall_score(self.y_test, self.y_pred, average='weighted'), '.2f')
        self.recall_micro =format(metrics.recall_score(self.y_test, self.y_pred, average='micro'), '.2f')
        self.recall_macro =format(metrics.recall_score(self.y_test, self.y_pred, average='macro'), '.2f')

        self.fmeasure_weighted = format(metrics.f1_score(self.y_test, self.y_pred, average='weighted'), '.2f')
        self.fmeasure_micro = format(metrics.f1_score(self.y_test, self.y_pred, average='micro'), '.2f')
        self.fmeasure_macro = format(metrics.f1_score(self.y_test, self.y_pred, average='macro'), '.2f')

        self.cohens_kappa = format(metrics.cohen_kappa_score(self.y_test, self.y_pred), '.2f')

        self.accuracy = 0

        np.set_printoptions(precision=2)

    def get_confusion_matrix(self):
        return self.confusion_matrix

    def get_normalised_confusion_matrix(self):
        cm = self.confusion_matrix
        return cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    def visualise_confusion_matrix(self, normalisation_flag):

        cm_normalised = self.get_normalised_confusion_matrix()

        colors = ["#283747", "#1B4F72", "#21618C", "#2874A6", "#2E86C1", "#3498DB", "#5DADE2", "#85C1E9", "#AED6F1", "#D6EAF8", "#EBF5FB", ]
        if normalisation_flag:
            mapper = LinearColorMapper(palette=list(reversed(colors)), low=0, high=1)
        else:
            mapper = LinearColorMapper(palette=list(reversed(colors)), low=self.confusion_matrix.min(), high=self.confusion_matrix.max())

        actual = []
        predicted = []
        weight = []
        value = []
        for node1 in range(0, len(self.genre_names)):
            for node2 in range(0, len(self.genre_names)):
                actual.append(self.genre_names[node2])
                predicted.append(self.genre_names[node1])
                value.append(self.confusion_matrix[node1][node2])
                weight.append(format(cm_normalised[node1][node2], '.2f'))

        source = ColumnDataSource(
            data=dict(
                actual=actual,
                predicted=predicted,
                weight=weight,
                value=value,
            )
        )

        TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

        p = figure(title="",
                   y_range=list(reversed(self.genre_names)), x_range=list(self.genre_names),
                   x_axis_location="below", plot_width=850, plot_height=800,
                   tools=TOOLS, toolbar_location='right')

        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size = "12pt"
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = np.math.pi / 3

        p.rect(x="actual", y="predicted", width=1, height=1,
               source=source,
               fill_color={'field': 'weight', 'transform': mapper},
               line_color='white')

        color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="10pt",
                             ticker=BasicTicker(desired_num_ticks=len(colors)),
                             # ticker=FixedTicker(ticks=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]),
                             formatter=PrintfTickFormatter(format="%.1f"),
                             label_standoff=7, border_line_color='white', location=(0, 0))
        p.add_layout(color_bar, 'right')

        p.select_one(HoverTool).tooltips = [
            ('Class', ' @actual predicted as @predicted'),
            ('Value', ' @value'),
            ('Normalized', ' @weight'),
        ]

        script, div = components(p)

        return script, div


class ExperimentComparator:

    def __init__(self, experiments):
        self.experiments = experiments
        self.experiment_titles = []
        for experiment in self.experiments:
            self.experiment_titles.append(experiment.display_title)

    def resultsComparisonUsingMetrics(self):
        # construct data x axis experiment names, y axis result
        fmeasure = {}
        precision = {}
        recall = {}
        other = {}

        fmeasure['weighted'] = []
        fmeasure['micro'] = []
        fmeasure['macro'] = []

        precision['weighted'] = []
        precision['micro'] = []
        precision['macro'] = []

        recall['weighted'] = []
        recall['micro'] = []
        recall['macro'] = []

        other['cross_validation_accuracies'] = []
        other['kappas'] = []

        for exp in self.experiments:
            results = exp.get_results()
            fmeasure['weighted'].append(results.fmeasure_weighted)
            fmeasure['micro'].append(results.fmeasure_micro)
            fmeasure['macro'].append(results.fmeasure_macro)

            precision['weighted'].append(results.precision_weighted)
            precision['micro'].append(results.precision_micro)
            precision['macro'].append(results.precision_macro)

            recall['weighted'].append(results.recall_weighted)
            recall['micro'].append(results.recall_micro)
            recall['macro'].append(results.recall_macro)

            other['cross_validation_accuracies'].append(results.accuracy)
            other['kappas'].append(results.cohens_kappa)

        p_fmeasure = self.generate_plot_for_metric(fmeasure, "F1 Scores Per Experiment")
        p_precision= self.generate_plot_for_metric(precision, "Precision Per Experiment")
        p_recall = self.generate_plot_for_metric(recall, "Recall Per Experiment")
        p_other = self.generate_plot_for_other(other, "Other metrics Per Experiment")

        plots = []
        plots.append(p_fmeasure)
        plots.append(p_precision)
        plots.append(p_recall)
        plots.append(p_other)

        return list(plots)

    def generate_plot_for_metric(self, metric, title):
        metric_data = {'experiments': self.experiment_titles,
                         'weighted': metric['weighted'],
                         'micro': metric['micro'],
                         'macro': metric['macro']}
        metric_source = ColumnDataSource(data=metric_data)

        p = figure(x_range=self.experiment_titles, y_range=(0, 1), plot_height=300, title=title,
                   toolbar_location='above', tools="hover,save,pan,box_zoom,reset,wheel_zoom")
        p.vbar(x=dodge('experiments', -0.25, range=p.x_range), top='weighted', width=0.2, source=metric_source,
               color="#c9d9d3", legend=value("Weighted"))
        p.vbar(x=dodge('experiments', 0.0, range=p.x_range), top='micro', width=0.2, source=metric_source,
               color="#718dbf", legend=value("Micro"))
        p.vbar(x=dodge('experiments', 0.25, range=p.x_range), top='macro', width=0.2, source=metric_source,
               color="#e84d60", legend=value("Macro"))

        p.x_range.range_padding = 0.4
        p.xgrid.grid_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = "vertical"

        return p

    def generate_plot_for_other(self, metric, title):
        metric_data = {'experiments': self.experiment_titles,
                       'accuracies': metric['cross_validation_accuracies'],
                       'kappas': metric['kappas']}
        metric_source = ColumnDataSource(data=metric_data)

        p = figure(x_range=self.experiment_titles, y_range=(0, 1), plot_height=300, title=title,
                   toolbar_location='above', tools="hover,save,pan,box_zoom,reset,wheel_zoom")

        p.vbar(x=dodge('experiments', 0.0, range=p.x_range), top='accuracies', width=0.2, source=metric_source,
               color="#718dbf", legend=value("Accuracy"))
        p.vbar(x=dodge('experiments', 0.25, range=p.x_range), top='kappas', width=0.2, source=metric_source,
               color="#e84d60", legend=value("Cohen's kappa"))

        p.x_range.range_padding = 0.4
        p.xgrid.grid_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = "vertical"

        return p

    def performComparison(self):

        plots = []
        plots.extend(self.resultsComparisonUsingMetrics())
        overview_layout = gridplot(plots, ncols=2)
        script, div = components(overview_layout)
        return script, div


