from pandas import DataFrame

import colorcet
import numpy as np

from bokeh.models import (
    ColumnDataSource,
    LabelSet,
    HoverTool,
    LinearColorMapper,
    PrintfTickFormatter,
    ColorBar,
    FixedTicker, FactorRange)
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.layouts import gridplot

from bokeh.transform import factor_cmap
from bokeh.palettes import Category20

from newsgac import genres as DataUtils
from newsgac.genres import genre_labels

__author__ = 'abilgin'


def normalise_confusion_matrix(cm):
    sum = cm.sum(axis=1)[:, np.newaxis]
    temp = cm.astype('float')
    # return cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    return np.divide(temp, sum, out=np.zeros_like(temp), where=sum!=0)

class ResultVisualiser(object):

    def __init__(self):
        pass

    @staticmethod
    def retrieveHeatMapfromResult(normalisation_flag, result, title="", ds_param = 1):
        confusion_matrix = result.confusion_matrix.get()
        cm_normalised = normalise_confusion_matrix(confusion_matrix)
        genre_names = DataUtils.genre_labels
        # print title
        # print confusion_matrix

        if normalisation_flag:
            mapper = LinearColorMapper(palette=colorcet.blues, low=0, high=1)
        else:
            mapper = LinearColorMapper(palette=colorcet.blues, low=confusion_matrix.min(),
                                       high=confusion_matrix.max())

        actual = []
        predicted = []
        weight = []
        value = []
        class_sizes = []
        for x in range(0, len(confusion_matrix)):
            for y in range(0, len(confusion_matrix)):
                actual.append(genre_names[y])
                predicted.append(genre_names[x])
                value.append(confusion_matrix[y][x])
                weight.append(format(cm_normalised[y][x], '.2f'))
                class_sizes.append(sum(confusion_matrix[0:][y]))


        source = ColumnDataSource(
            data=dict(
                actual=actual,
                predicted=predicted,
                weight=weight,
                pred_value=value,
                actual_value=class_sizes,
            )
        )

        TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

        p = figure(title=title,
                   y_range=list(reversed(genre_names)), x_range=list(genre_names),
                   x_axis_location="below", plot_width=int(850*ds_param), plot_height=int(800*ds_param),
                   tools=TOOLS, toolbar_location='above')

        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        if ds_param < 1:
            font_size = "7pt"
        else:
            font_size = "10pt"
        p.axis.major_label_text_font_size = font_size
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = np.math.pi / 3

        p.rect(x="predicted", y="actual", width=1, height=1,
               source=source,
               fill_color={'field': 'weight', 'transform': mapper},
               line_color='white')

        color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size=font_size,
                             ticker=FixedTicker(ticks=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]),
                             formatter=PrintfTickFormatter(format="%.1f"),
                             label_standoff=7, border_line_color='white', location=(0, 0))
        p.add_layout(color_bar, 'right')

        p.select_one(HoverTool).tooltips = [
            ('Class', ' @actual predicted as @predicted'),
            ('Predicted # instances', ' @pred_value'),
            ('Total # instances', ' @actual_value'),
            ('Normalized', ' @weight'),
        ]

        script, div = components(p)

        return p, script, div

    @staticmethod
    def visualise_sorted_probabilities_for_raw_text_prediction(sorted_probabilities, title_suffix, ds_param = 1):

        if ds_param < 1:
            font_size = "7pt"
        else:
            font_size = "10pt"

        prediction_data = {'genres': sorted_probabilities.keys(),
                       'probs': sorted_probabilities.values()}
        pred_source = ColumnDataSource(data=prediction_data)

        p = figure(y_range=sorted_probabilities.keys(), plot_height=int(600*ds_param), title='Genre Probabilities for '+ title_suffix,
                   plot_width=int(800*ds_param), x_range=[0, 1], toolbar_location='right',
                   tools="save,pan,box_zoom,reset,wheel_zoom")

        p.hbar(y=sorted_probabilities.keys(), height=0.5, left=0, right=sorted_probabilities.values(), color='navy')

        labels = LabelSet(x='probs', y='genres', text='probs', level='glyph', text_font_size=font_size,
                          x_offset=2, y_offset=-1, source=pred_source, render_mode='canvas')

        p.y_range.range_padding = 0.4
        p.axis.major_label_text_font_size = font_size
        p.xgrid.grid_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = "horizontal"

        p.add_layout(labels)

        script, div = components(p)

        return p, script, div

    @staticmethod
    def retrievePlotForFeatureWeights(coefficients, names, vectorized_pipeline=False):
        top_features = 10

        i = 1
        j = i + 1
        plots = []
        for classifier in coefficients:

            if vectorized_pipeline:
                # For classifiers using vectorizer
                classifier = np.asarray(classifier.todense()).reshape(-1)

            title = str(DataUtils.genres_full[i]) + " vs " + str(DataUtils.genres_full[j])
            top_coeff_pos = np.argsort(classifier)[-top_features:]
            top_coeff_neg = np.argsort(classifier)[:top_features]

            pos_features_names = []
            pos_features_weights = []
            for index in top_coeff_pos:
                if classifier[index] > 0:
                    # print classifier[index]
                    pos_features_weights.append(format(classifier[index], '.3f'))
                    pos_features_names.append(names[index])

            neg_features_names = []
            neg_features_weights = []
            for index in top_coeff_neg:
                if classifier[index] < 0:
                    # print classifier[index]
                    neg_features_weights.append(format(classifier[index], '.3f'))
                    neg_features_names.append(names[index])


            if j == len(DataUtils.genres_full)-1:
                i += 1
                j = i + 1
            else:
                j += 1

            all_feats = np.hstack([neg_features_names, pos_features_names])
            weight_data_pos = {'names': pos_features_names,
                            'weights': pos_features_weights}
            pred_source_pos = ColumnDataSource(data=weight_data_pos)

            weight_data_neg = {'names': neg_features_names,
                            'weights': neg_features_weights}
            pred_source_neg = ColumnDataSource(data=weight_data_neg)

            p = figure(y_range=all_feats, plot_height=int(30*len(all_feats)),
                       # title='Feature importance weights for ' + main_title + ": " + title,
                       title = title,
                       plot_width=int(500), x_range=[-3, 3], toolbar_location='right',
                       tools="save,pan,box_zoom,reset,wheel_zoom")

            p.hbar(y=pos_features_names, height=0.5, left=0, right=pos_features_weights, color='navy')
            p.hbar(y=neg_features_names, height=0.5, left=neg_features_weights, right=0, color='red')

            labels_pos = LabelSet(x='weights', y='names', text='weights', level='glyph', text_font_size='8pt',
                              x_offset=2, y_offset=-1, source=pred_source_pos, render_mode='canvas')
            labels_neg = LabelSet(x='weights', y='names', text='weights', level='glyph', text_font_size='8pt',
                              x_offset=-35, y_offset=-1, source=pred_source_neg, render_mode='canvas')

            p.y_range.range_padding = 0.4
            p.axis.major_label_text_font_size = '8pt'
            p.xgrid.grid_line_color = None
            p.legend.location = "top_left"
            p.legend.orientation = "horizontal"
            p.xaxis.major_label_orientation = "horizontal"

            p.add_layout(labels_pos)
            p.add_layout(labels_neg)

            plots.append(p)

        overview_layout = gridplot(list(plots), ncols=3)
        script, div = components(overview_layout)

        return plots, script, div

    @staticmethod
    def visualize_df_feature_importance(data_frame, title_suffix):

        pred_source = ColumnDataSource(data=data_frame)

        p = figure(y_range=data_frame['Feature'].tolist(), plot_height=1000, title='Feature Importance for '+ title_suffix,
                   plot_width=800, x_range=[0, 0.4], toolbar_location='right',
                   tools="save,pan,box_zoom,reset,wheel_zoom")

        p.hbar(y=data_frame['Feature'].tolist(), height=0.5, left=0, right=data_frame['Importance'].tolist(), color='navy')

        labels = LabelSet(x='Importance', y='Feature', text='Importance', level='glyph', text_font_size="8pt",
                          x_offset=2, y_offset=-1, source=pred_source, render_mode='canvas')

        p.y_range.range_padding = 0.4
        p.axis.major_label_text_font_size = "10pt"
        p.xgrid.grid_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = "horizontal"

        p.add_layout(labels)

        script, div = components(p)

        return p, script, div

    @staticmethod
    def visualize_data_source_stats(data_source):
        # https://bokeh.pydata.org/en/latest/docs/user_guide/categorical.html#nested-categories
        title = data_source.display_title
        articles = [{
            'year': str(article.year),
            'label': genre_labels[article.label]
        } for article in data_source.articles]

        df = DataFrame(articles)

        group_sizes = df.groupby(['year', 'label']).size().to_frame('size')

        counts = list(group_sizes['size'])
        x = list(group_sizes.index)  # year,label tuples

        source = ColumnDataSource(data=dict(
            x=x,
            counts=counts
        ))

        p = figure(x_range=FactorRange(*x),
                   plot_height=400,
                   plot_width=1200,
                   title="Distribution of genres over time in " + title,
                   toolbar_location='right',
                   tools="save,pan,box_zoom,reset,wheel_zoom"
                   )

        p.vbar(source=source,
               x='x',
               top='counts',
               width=1,
               line_color="white",
               fill_color=factor_cmap('x',
                                      palette=Category20[20],
                                      factors=sorted(list(df.label.unique())),
                                      start=1,
                                      end=2
                                      )
               )

        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        p.yaxis.axis_label = "Total number of instances"
        p.yaxis.major_label_text_font_size = '10pt'
        p.xaxis.major_label_text_font_size = '10pt'
        p.xaxis.major_label_orientation = "vertical"
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        script, div = components(p)

        return script, div
