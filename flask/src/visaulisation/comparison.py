from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.core.properties import value
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource)

__author__ = 'abilgin'


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


