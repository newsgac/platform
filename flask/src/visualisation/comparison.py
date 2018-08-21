from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.core.properties import value
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource, LabelSet)
import math
import uuid

from collections import defaultdict
from src.common.utils import Utils
from src.database import DATABASE
from src.visualisation.resultvisualiser import ResultVisualiser
from src.models.data_sources.data_source import DataSource

UT = Utils()

__author__ = 'abilgin'


class ExperimentComparator:

    def __init__(self, experiments):
        # self.experiments = experiments
        self.experiments = sorted(experiments, key=lambda x: x.display_title)
        self.experiment_titles = []
        for experiment in self.experiments:
            self.experiment_titles.append(experiment.display_title)

        self.experiment_titles = sorted(self.experiment_titles)
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
            results = exp.get_results_eval()
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

    @staticmethod
    def get_existing_article_predictions(article_text):
        return DATABASE.find_one('predictions', {"article_text": article_text})

    @staticmethod
    def save_article_comparison(id, article_text, ds_id):
        DATABASE.insert('predictions', {"_id":id, "article_text":article_text, "data_source_id":ds_id, "exp_predictions":{}})

    @staticmethod
    def update_article_comparison_by_experiment(article_text, exp_id, prediction):
        DATABASE.update('predictions', {"article_text": article_text},
                        {"$set": {"exp_predictions." +exp_id: prediction}})

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

        if len(self.experiments) == 2:
            ds_param = 0.7
        elif len(self.experiments) > 2:
            ds_param = 0.55
        else:
            ds_param = 1/math.sqrt(len(self.experiments))

        for experiment in self.experiments:

            results = experiment.get_results_model()
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
            data_source = DataSource.get_by_id(experiment.data_source_id)
            prediction_results = experiment.predict(raw_text, data_source)
            print prediction_results
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

    def retrieveUniqueTestArticleGenreTuplesBasedOnRawText(self):
        processed_data_source_list = DataSource.get_processed_datasets()
        test_articles_genres = []
        used_raw_text = []
        for ds in processed_data_source_list:
            # ds = DataSource.get_by_id(ds_id)
            for art in ds.get_test_instances():
                if (art['article_raw_text'],art["genre_friendly"]) not in used_raw_text:
                    used_raw_text.append((art['article_raw_text'],art["genre_friendly"]))
                    test_articles_genres.append((art['_id'],art['article_raw_text'],art["genre_friendly"]))

        print "Total unique articles : ", len(test_articles_genres)
        return test_articles_genres


    def generateAgreementOverview(self, test_articles_genres):
        # generate a dictionary to be displayed in the format of article_text, mutually agreeing experiments,
        # quantity for the chosen genre
        # test_articles is a list of documents from DB.collection("processed_data")
        tabular_data_all = []   # list of dictionaries
        count = 1

        dicts_to_merge = {}
        for article_id, article_text, article_genre in test_articles_genres:
            tabular_data_row = {}
            tabular_data_row["article_number"] = count
            tabular_data_row["article_text"] = article_text
            tabular_data_row["article_id"] = article_id

            # get prediction from each experiment
            predictions_dict = {}
            existing_pred = ExperimentComparator.get_existing_article_predictions(article_text=article_text)
            for exp in self.experiments:
                ds = DataSource.get_by_id(exp.data_source_id)

                if existing_pred is None:
                    ExperimentComparator.save_article_comparison(id=uuid.uuid4().hex, article_text=article_text, ds_id=ds._id)
                    predictions_dict[exp] = (exp.predict(article_text, ds)).keys()[0]
                    ExperimentComparator.update_article_comparison_by_experiment(article_text=article_text,
                                                                 exp_id=exp._id, prediction=predictions_dict[exp])
                elif exp._id not in existing_pred["exp_predictions"].keys():
                    predictions_dict[exp] = (exp.predict(article_text, ds)).keys()[0]
                    ExperimentComparator.update_article_comparison_by_experiment(article_text=article_text,
                                                               exp_id=exp._id, prediction=predictions_dict[exp])
                else:
                    predictions_dict[exp] = existing_pred["exp_predictions"][exp._id]

            # print "Predictions dictionary"
            # print predictions_dict

            # count the predictions in the dictionary and find the largest agreement
            genre_counts = defaultdict(int)
            for genre in predictions_dict.values():
                genre_counts[genre] += 1

            # get the prevailing genre
            prevailing_genre = max(genre_counts, key=lambda key: genre_counts[key])

            # get the experiments that agree on the prevailing genre
            agreement_dict = {}
            for k, v in predictions_dict.iteritems():
                agreement_dict.setdefault(v, []).append(k)

            dicts_to_merge[count] = agreement_dict

            tabular_data_row["mutual_agreement_exp"] = agreement_dict[prevailing_genre]
            tabular_data_row["agreed_genre_prediction"] = prevailing_genre
            tabular_data_row["true_genre"] = article_genre if (article_genre is not None or article_genre is not "UNL") else "N/A"
            # TODO:Test for unlabelled data here

            count += 1
            tabular_data_all.append(tabular_data_row)


        combinations = {}

        # for each article find the combination that agrees on the prediction
        # TODO: optimize this triple loop: fix applied down to double loop
        for art_num, d in dicts_to_merge.items():
            for pred, exp_list in d.items():
                key = tuple((sorted(exp_list)))
                try:
                    combinations[key].setdefault(pred, []).append(art_num)
                except KeyError:
                    combinations[key] = {pred: [art_num]}

        return tabular_data_all, combinations


    @staticmethod
    def visualize_hypotheses_using_DF(df, data_title, exp_title):

        df = df.reset_index().rename(columns={'index': 'genre'})
        print df
        data = df.to_dict(orient='list')
        idx = df['genre'].tolist()
        print data
        source = ColumnDataSource(data=data)

        p = figure(x_range=idx, y_range=(0, df[["1965", "1985"]].values.max() + 5),
                   plot_height=500, plot_width=1200, title="Relative distribution of genres over time using "+ exp_title+" on "+data_title,
                   toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

        p.vbar(x=dodge('genre', -0.1, range=p.x_range), top=df.columns[1], width=0.2, source=source,
               color="#c9d9d3", legend=value("1965"))
        labels = LabelSet(x='genre', y='1965', text='1965', level='glyph', text_font_size="7pt",
                          x_offset=-25, y_offset=1, source=source, render_mode='canvas')
        p.add_layout(labels)
        p.vbar(x=dodge('genre', 0.1, range=p.x_range), top=df.columns[2], width=0.2, source=source,
               color="#718dbf", legend=value("1985"))
        labels = LabelSet(x='genre', y='1985', text='1985', level='glyph', text_font_size="7pt",
                          x_offset=6, y_offset=1, source=source, render_mode='canvas')
        p.add_layout(labels)

        # p.vbar(x=dodge('freq', 0.1, range=p.x_range), top='C', width=0.2, source=source,
        #        color="#e84d60", legend=value("C"))
        #
        # p.vbar(x=dodge('freq',  0.3,  range=p.x_range), top='D', width=0.2, source=source,
        #        color="#ddb7b1", legend=value("D"))

        # labels = LabelSet(x='genre', text='macro', level='glyph', text_font_size="7pt",
        #                       y_offset=2, source=source,
        #                       render_mode='canvas')
        #
        # p.add_layout(labels)

        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        p.yaxis.axis_label = "Percentage (%)"
        p.yaxis.major_label_text_font_size = '10pt'
        p.xaxis.major_label_text_font_size = '10pt'
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        script, div = components(p)

        return script, div


