import numpy
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.core.properties import value
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource, LabelSet)
import math
import uuid

from collections import defaultdict, Counter
from newsgac import database
from newsgac.tasks.progress import report_progress
from newsgac.visualisation.resultvisualiser import ResultVisualiser
# from newsgac.models.data_sources.data_source_old import DataSource


__author__ = 'abilgin'


class PipelineComparator:

    def __init__(self, ace):
        self.ace = ace
        pipelines = ace.pipelines
        # self.pipelines = pipelines
        self.pipelines = sorted(pipelines, key=lambda x: x.display_title)
        self.pipeline_titles = []
        for pipeline in self.pipelines:
            self.pipeline_titles.append(pipeline.display_title)

        self.pipeline_titles = sorted(self.pipeline_titles)
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

        for pipeline in self.pipelines:
            results = pipeline.result
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


    def resultsComparisonUsingMetric(self):
        # TODO: Label location tuning for figures
        p_fmeasure = self.generate_plot_for_pipeline(self.fmeasure, "Overview F1 Scores")
        p_precision= self.generate_plot_for_pipeline(self.precision, "Overview Precision")
        p_recall = self.generate_plot_for_pipeline(self.recall, "Overview Recall")
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
                       plot_width = 400, x_range=[0,1], toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

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
                       plot_width = 400, x_range=[0,1], toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

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

    def generate_plot_for_other(self, metric, title):
        crowd = len(self.pipelines)
        metric_data = {'pipelines': self.pipeline_titles,
                       'accuracies': metric['cross_validation_accuracies'],
                       'kappas': metric['kappas']}
        metric_source = ColumnDataSource(data=metric_data)

        p = figure(x_range=self.pipeline_titles, y_range=(0, 1), plot_height=400, title=title,
                   toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

        p.vbar(x=dodge('pipelines', 0.0, range=p.x_range), top='accuracies', width=0.2, source=metric_source,
               color="#718dbf", legend=value("10-fold cross validation accuracy"))
        p.vbar(x=dodge('pipelines', 0.25, range=p.x_range), top='kappas', width=0.2, source=metric_source,
               color="#e84d60", legend=value("Cohen's kappa"))

        labels_acc = LabelSet(x='pipelines', y='accuracies', text='accuracies', level='glyph', text_font_size="7pt",
                          y_offset=2, x_offset=-(100/(crowd*crowd)), source=metric_source, render_mode='canvas')

        labels_kap = LabelSet(x='pipelines', y='kappas', text='kappas', level='glyph', text_font_size="7pt",
                              y_offset=2, x_offset=(100/(crowd*crowd))*5-3*crowd, source=metric_source, render_mode='canvas')

        p.add_layout(labels_acc)
        p.add_layout(labels_kap)

        p.x_range.range_padding = 0.4
        p.xgrid.grid_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = "vertical"

        return p

    def generate_plot_for_pipeline(self, metric, title):
        crowd = len(self.pipelines)
        metric_data = {'pipelines': self.pipeline_titles,
                         'weighted': metric['weighted'],
                         'micro': metric['micro'],
                         'macro': metric['macro']}
        metric_source = ColumnDataSource(data=metric_data)

        p = figure(x_range=self.pipeline_titles, y_range=(0, 1), plot_height=400, title=title,
                   toolbar_location='right', tools="save,pan,box_zoom,reset,wheel_zoom")

        p.vbar(x=dodge('pipelines', -0.30, range=p.x_range), top='weighted', width=0.2, source=metric_source,
           color="#c9d9d3", legend=value('Weighted'))
        p.vbar(x=dodge('pipelines', 0.0, range=p.x_range), top='micro', width=0.2, source=metric_source,
           color="#718dbf", legend=value('Micro'))
        p.vbar(x=dodge('pipelines', 0.30, range=p.x_range), top='macro', width=0.2, source=metric_source,
           color="#e84d60", legend=value("Macro"))

        labels_wei = LabelSet(x='pipelines', y='weighted', text='weighted', level='glyph', text_font_size="7pt",
                              y_offset=2, x_offset=-((100/(crowd*crowd))*7+crowd), source=metric_source, render_mode='canvas')

        labels_mic = LabelSet(x='pipelines', y='micro', text='micro', level='glyph', text_font_size="7pt",
                              y_offset=2, x_offset=-(100/(crowd*crowd))*2, source=metric_source, render_mode='canvas')

        labels_mac = LabelSet(x='pipelines', y='macro', text='macro', level='glyph', text_font_size="7pt",
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

    def combineHeatMapPlotsForAllPipelines(self):

        plots = []

        if len(self.pipelines) == 2:
            ds_param = 0.7
        elif len(self.pipelines) > 2:
            ds_param = 0.55
        else:
            ds_param = 1/math.sqrt(len(self.pipelines))

        for pipeline in self.pipelines:

            results = pipeline.get_results_model()
            plot, script, div = ResultVisualiser.retrieveHeatMapfromResult(normalisation_flag=True, result=results,
                                                                           title=pipeline.display_title,
                                                                           ds_param = ds_param)
            plots.append(plot)

        overview_layout = gridplot(list(plots), ncols=3)
        script, div = components(overview_layout)

        return script, div

    def visualise_prediction_comparison(self, raw_text):

        plots = []

        if len(self.pipelines) > 2:
            ds_param = 0.55
        else:
            ds_param = 1/math.sqrt(len(self.pipelines))

        for pipeline in self.pipelines:
            data_source = pipeline.data_source
            prediction_results = pipeline.predict([raw_text])[0]
            print (prediction_results)
            plot, script, div = ResultVisualiser.visualise_sorted_probabilities_for_raw_text_prediction(prediction_results, pipeline.display_title, ds_param)
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

        # Plots shows all metrics grouped by pipeline in the same graph
        # plots = []
        # plots.extend(self.resultsComparisonUsingMetric())
        # overview_layout = gridplot(plots, ncols=2)
        # script, div = components(overview_layout)
        # scripts.append(script)
        # divs.append(div)

        return scripts, divs

    # def retrieveUniqueTestArticleGenreTuplesBasedOnRawText(self):
    #     processed_data_source_list = DataSource.get_processed_datasets()
    #     test_articles_genres = []
    #     used_raw_text = []
    #     for ds in processed_data_source_list:
    #         # ds = DataSource.get_by_id(ds_id)
    #         for art in ds.get_test_instances():
    #             if (art['article_raw_text'],art["genre_friendly"]) not in used_raw_text:
    #                 used_raw_text.append((art['article_raw_text'],art["genre_friendly"]))
    #                 test_articles_genres.append((art['_id'],art['article_raw_text'],art["genre_friendly"]))
    #
    #     print "Total unique articles : ", len(test_articles_genres)
    #     return test_articles_genres

    @staticmethod
    def get_predictions(articles, pipelines):
        # todo: parallelize
        # pipeline predictions are (hopefully) already parallelized for multiple articles at the same time
        # we could still paralellize multiple pipelines
        predictions = []
        for idx, pipeline in enumerate(pipelines):
            predictions.append(
                pipeline.sk_pipeline.predict([article.raw_text for article in articles]))
            report_progress('ace', (idx + 1) / float(len(pipelines)))
        # transpose so first axis is now article e.g. predictions[0][1] is article 0, pipeline 1
        return numpy.array(predictions).transpose()

    def generateAgreementOverview(self):
        tabular_data_all = []   # list of dictionaries

        predictions = self.get_predictions(self.ace.date_source.articles, self.ace.pipelines)


        articles = [{
            'raw_text': article.raw_text,
            'label': article.label,
            'predictions': predictions[idx]

        } for idx, article in enumerate(self.ace.data_source.articles)]

        for key, article in enumerate(self.ace.data_source.articles):
            tabular_data_row = {}
            tabular_data_row["article_text"] = article.raw_text
            tabular_data_row["predictions"] = predictions[key]
            # tabular_data_row["article_key"] = key
            tabular_data_row["true_genre"] = article.label if article.label is not "UNL" else "N/A"
            tabular_data_row["agreed_genre_prediction"] = Counter(predictions[key]).most_common(1)[0][0]

            # contains a dict with key = prediction label, value = list of pipeline ids with this prediction
            predicted_genres = {}
            for idx, prediction in enumerate(predictions[key]):
                predicted_genres[prediction] = predicted_genres.get(prediction, []) + [idx]
            tabular_data_row["mutual_agreement_pipelines"] = predicted_genres

            tabular_data_all.append(tabular_data_row)

        return tabular_data_all


    @staticmethod
    def visualize_hypotheses_using_DF(df, data_title, exp_title):

        df = df.reset_index().rename(columns={'index': 'genre'})
        print (df)
        data = df.to_dict(orient='list')
        idx = df['genre'].tolist()
        print (data)
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


