from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.core.properties import value
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource, LabelSet)
import math
import itertools

from collections import defaultdict
from src.common.utils import Utils
from src.models.experiments.experiment import ExperimentSVC
from src.visualisation.resultvisualiser import ResultVisualiser
from src.models.data_sources.data_source import DataSource

UT = Utils()

__author__ = 'abilgin'


class ExperimentComparator:

    def __init__(self, experiments):
        self.experiments = experiments
        self.experiment_titles = []
        for experiment in self.experiments:
            self.experiment_titles.append(experiment.display_title)

        # construct data_sources x axis experiment names, y axis result
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

        for exp in self.experiments:
            results = exp.get_results()
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

    def resultsComparisonUsingExperiments(self):

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

    def resultsComparisonUsingMetric(self):

        # TODO: Label location tuning for figures
        p_fmeasure = self.generate_plot_for_experiment(self.fmeasure, "Overview F1 Scores")
        p_precision= self.generate_plot_for_experiment(self.precision, "Overview Precision")
        p_recall = self.generate_plot_for_experiment(self.recall, "Overview Recall")
        p_other = self.generate_plot_for_other(self.other, "Overview Other metrics")

        plots = []
        plots.append(p_fmeasure)
        plots.append(p_precision)
        plots.append(p_recall)
        plots.append(p_other)

        return list(plots)

    def generate_plots_for_metric(self, metric, title, color='navy'):

        figures = []
        types = ['weighted', 'micro', 'macro']

        metric_data = {'experiments': self.experiment_titles,
                       'weighted': metric['weighted'],
                       'micro': metric['micro'],
                       'macro': metric['macro']}
        metric_source = ColumnDataSource(data=metric_data)

        if len(self.experiment_titles) < 7:
            height = 300
        else:
            height = 50*len(self.experiment_titles)

        for type in types:
            p = figure(y_range=self.experiment_titles, plot_height=height, title=title + ' (' + type + ')',
                       plot_width = 400, x_range=[0,1], toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

            p.hbar(y=self.experiment_titles, height=0.5, left=0, right=metric[type], color=color)

            labels = LabelSet(x=type, y='experiments', text=type, level='glyph', text_font_size="7pt",
                              x_offset=2, y_offset= -1, source=metric_source, render_mode='canvas')

            p.y_range.range_padding = 0.4
            p.xgrid.grid_line_color = None
            p.legend.location = "top_left"
            p.legend.orientation = "horizontal"
            p.xaxis.major_label_orientation = "horizontal"

            p.add_layout(labels)

            figures.append(p)

        return figures

    def generate_plots_for_other_metric(self, metric, title, color='navy'):

        figures = []
        types = ['cross_validation_accuracies', 'kappas']
        subtitles = ['Accuracy', 'Cohen\'s kappa']

        metric_data = {'experiments': self.experiment_titles,
                       'cross_validation_accuracies': metric['cross_validation_accuracies'],
                       'kappas': metric['kappas']}
        metric_source = ColumnDataSource(data=metric_data)

        if len(self.experiment_titles) < 7:
            height = 300
        else:
            height = 50*len(self.experiment_titles)

        i = 0
        for type in types:
            p = figure(y_range=self.experiment_titles, plot_height=height, title=title + ' (' + subtitles[i] + ')',
                       plot_width = 400, x_range=[0,1], toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

            p.hbar(y=self.experiment_titles, height=0.5, left=0, right=metric[type], color=color)

            labels = LabelSet(x=type, y='experiments', text=type, level='glyph', text_font_size="7pt",
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

    def generate_plot_for_other(self, metric, title):
        crowd = len(self.experiments)
        metric_data = {'experiments': self.experiment_titles,
                       'accuracies': metric['cross_validation_accuracies'],
                       'kappas': metric['kappas']}
        metric_source = ColumnDataSource(data=metric_data)

        p = figure(x_range=self.experiment_titles, y_range=(0, 1), plot_height=400, title=title,
                   toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

        p.vbar(x=dodge('experiments', 0.0, range=p.x_range), top='accuracies', width=0.2, source=metric_source,
               color="#718dbf", legend=value("10-fold cross validation accuracy"))
        p.vbar(x=dodge('experiments', 0.25, range=p.x_range), top='kappas', width=0.2, source=metric_source,
               color="#e84d60", legend=value("Cohen's kappa"))

        labels_acc = LabelSet(x='experiments', y='accuracies', text='accuracies', level='glyph', text_font_size="7pt",
                          y_offset=2, x_offset=-(100/(crowd*crowd)), source=metric_source, render_mode='canvas')

        labels_kap = LabelSet(x='experiments', y='kappas', text='kappas', level='glyph', text_font_size="7pt",
                              y_offset=2, x_offset=(100/(crowd*crowd))*5-3*crowd, source=metric_source, render_mode='canvas')

        p.add_layout(labels_acc)
        p.add_layout(labels_kap)

        p.x_range.range_padding = 0.4
        p.xgrid.grid_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = "vertical"

        return p

    def generate_plot_for_experiment(self, metric, title):
        crowd = len(self.experiments)
        metric_data = {'experiments': self.experiment_titles,
                         'weighted': metric['weighted'],
                         'micro': metric['micro'],
                         'macro': metric['macro']}
        metric_source = ColumnDataSource(data=metric_data)

        p = figure(x_range=self.experiment_titles, y_range=(0, 1), plot_height=400, title=title,
                   toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

        p.vbar(x=dodge('experiments', -0.30, range=p.x_range), top='weighted', width=0.2, source=metric_source,
           color="#c9d9d3", legend=value('Weighted'))
        p.vbar(x=dodge('experiments', 0.0, range=p.x_range), top='micro', width=0.2, source=metric_source,
           color="#718dbf", legend=value('Micro'))
        p.vbar(x=dodge('experiments', 0.30, range=p.x_range), top='macro', width=0.2, source=metric_source,
           color="#e84d60", legend=value("Macro"))

        labels_wei = LabelSet(x='experiments', y='weighted', text='weighted', level='glyph', text_font_size="7pt",
                              y_offset=2, x_offset=-((100/(crowd*crowd))*7+crowd), source=metric_source, render_mode='canvas')

        labels_mic = LabelSet(x='experiments', y='micro', text='micro', level='glyph', text_font_size="7pt",
                              y_offset=2, x_offset=-(100/(crowd*crowd))*2, source=metric_source, render_mode='canvas')

        labels_mac = LabelSet(x='experiments', y='macro', text='macro', level='glyph', text_font_size="7pt",
                              y_offset=2, x_offset=(100/(crowd*crowd))*7-3*crowd, source=metric_source, render_mode='canvas')

        p.add_layout(labels_wei)
        p.add_layout(labels_mic)
        p.add_layout(labels_mac)

        p.x_range.range_padding = 0.3
        p.xgrid.grid_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = "vertical"

        return p

    def combineHeatMapPlotsForAllExperiments(self):

        plots = []

        if len(self.experiments) > 2:
            ds_param = 0.55
        else:
            ds_param = 1/math.sqrt(len(self.experiments))

        for experiment in self.experiments:

            results = experiment.get_results()
            plot, script, div = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results,
                                                                           title=experiment.display_title,
                                                                           ds_param = ds_param)
            plots.append(plot)

        overview_layout = gridplot(list(plots), ncols=3)
        script, div = components(overview_layout)

        return script, div

    def visualise_prediction_comparison(self, raw_text):

        plots = []

        if len(self.experiments) > 2:
            ds_param = 0.55
        else:
            ds_param = 1/math.sqrt(len(self.experiments))

        for experiment in self.experiments:
            prediction_results = experiment.predict(raw_text)
            plot, script, div = ResultVisualiser.visualise_sorted_probabilities_for_raw_text_prediction(prediction_results, experiment.display_title, ds_param)
            plots.append(plot)

        overview_layout = gridplot(list(plots), ncols=3)
        script, div = components(overview_layout)

        return script, div


    def performComparison(self):

        scripts = []
        divs = []

        plots = []
        plots.extend(self.resultsComparisonUsingExperiments())
        overview_layout = gridplot(plots, ncols=3)
        script, div = components(overview_layout)
        scripts.append(script)
        divs.append(div)

        # Plots shows all metrics grouped by experiment in the same graph
        # plots = []
        # plots.extend(self.resultsComparisonUsingMetric())
        # overview_layout = gridplot(plots, ncols=2)
        # script, div = components(overview_layout)
        # scripts.append(script)
        # divs.append(div)

        return scripts, divs

    def retrieveTestArticles(self):
        test_articles = []
        unique_data_sources = []
        unique_exp = []
        for exp in self.experiments:
            if exp.data_source_id not in unique_data_sources:
                unique_data_sources.append(exp.data_source_id)
                unique_exp.append(exp)

        print unique_data_sources
        print unique_exp

        for exp in unique_exp:
            if exp.type == "SVC":
                test_articles.extend(ExperimentSVC.get_by_id(exp._id).get_test_instances())
            elif exp.type == "DT":
                pass


        return test_articles


    def generateAgreementOverview(self, test_articles):
        # generate a dictionary to be displayed in the format of article_text, mutually agreeing experiments,
        # quantity for the chosen genre
        # test_articles is a list of documents from DB.collection("processed_data")
        tabular_data_all = []   # list of dictionaries
        count = 1

        dicts_to_merge = {}
        for article in test_articles:
            tabular_data_row = {}
            tabular_data_row["article_number"] = count
            tabular_data_row["article_text"] = article["article_raw_text"]
            tabular_data_row["article_id"] = article["_id"]

            # get prediction from each experiment
            predictions_dict = {}

            for exp in self.experiments:
                predictions_dict[exp] = (exp.predict_from_db(article)).keys()[0]

            # print "Predictions dictionary"
            # print predictions_dict

            # count the predictions in the dictionary and find the largest agreement
            genre_counts = defaultdict(int)
            for genre in predictions_dict.values():
                genre_counts[genre] += 1

            # print "Genre counts"
            # print genre_counts

            # get the prevailing genre
            prevailing_genre = max(genre_counts, key=lambda key: genre_counts[key])

            # get the experiments that agree on the prevailing genre
            agreement_dict = {}
            for k, v in predictions_dict.iteritems():
                agreement_dict.setdefault(v, []).append(k)

            # print "Agreement dictionary"
            # print agreement_dict
            dicts_to_merge[article["_id"]] = agreement_dict

            tabular_data_row["mutual_agreement_exp"] = agreement_dict[prevailing_genre]
            tabular_data_row["gold_agreement_exp"] = []
            tabular_data_row["agreed_genre_prediction"] = prevailing_genre
            tabular_data_row["true_genre"] = article["genre_friendly"] if article["genre_friendly"] is not None else "N/A"

            count += 1
            tabular_data_all.append(tabular_data_row)

        # quantity_genre = defaultdict(set)
        # for d in dicts_to_merge:
        #     for k, v in d.iteritems():
        #         quantity_genre[k].add(v)

        combinations = {}
        # create combinations of the experiments
        # set based overview - venn diagram information
        for i, combo in enumerate(UT.powerset(iterable=self.experiments), 1):
            if i != 1:
                combinations[combo] = {}

        # for each article find the combination that agrees on the prediction
        for art_id, d in dicts_to_merge.items():
            for pred, exp_list in d.items():
                for key in combinations.keys():
                    if set(key) == set(exp_list):
                        if pred not in combinations[key].keys():
                            combinations[key][pred] = []
                        # combinations[key][pred].append(DataSource.get_processed_article_by_id(art_id))
                        combinations[key][pred].append(art_id)
                        break



        return tabular_data_all, combinations


