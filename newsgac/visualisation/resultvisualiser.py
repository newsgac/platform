from collections import OrderedDict

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
from scipy.sparse import csr_matrix

from newsgac import genres as DataUtils
from newsgac.genres import genre_labels

__author__ = 'abilgin'


def normalise_confusion_matrix(cm):
    sum = cm.sum(axis=1)[:, np.newaxis]
    temp = cm.astype('float')
    # return cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    return np.divide(temp, sum, out=np.zeros_like(temp), where=sum!=0)


def heatMapFromResult(pipeline, title="Evaluation", normalisation_flag=True, ds_param = 1):
    result = pipeline.result
    confusion_matrix = result.confusion_matrix.get()
    cm_normalised = normalise_confusion_matrix(confusion_matrix)
    genre_names = pipeline.data_source.labels

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

    return p


def get_coef_map(indices: []):
    """maps coef index to (class 1, class 2) tuple,
    e.g. get_coef_map([1,4,7,8]) == {
    0: (1, 4),
    1: (1, 7),
    2: (1, 8),
    3: (4, 7),
    4: (4, 8),
    5: (7, 8)}
    """
    coef_map = {}
    index = 0
    for i in range(0, len(indices) - 1):
        for j in range(i+1, len(indices)):
            coef_map[index] = (indices[i], indices[j])
            index += 1
    return coef_map


def svc_feature_weights(pipeline, top_features=10):
    sk_pipeline = pipeline.sk_pipeline.get()
    classifier = sk_pipeline.named_steps['Classifier']
    if classifier.kernel != 'linear':
        raise TypeError("SVC features: Can only plot feature weights for linear kernel.")

    coefficients = classifier.coef_
    labels = pipeline.data_source.labels
    feature_names = sk_pipeline.named_steps['FeatureExtraction'].get_feature_names()
    # get vectorizer for bow
    if isinstance(coefficients, csr_matrix):
        coefficients = coefficients.toarray()

    coef_map = get_coef_map(labels)
    # coef_map inversed, so that you can lookup the coef index for class pair
    # e.g. coef_map_inverse[(1,7)] == 1
    coef_map_inverse = {v: k for k, v in coef_map.items()}

    plots = []
    for label_pair, idx in coef_map_inverse.items():
        sub_classifier = coefficients[idx]
        # For classifiers using vectorizer

        # if hasattr(classifier, 'todense'):
        #     classifier = np.asarray(classifier.todense()).reshape(-1)

        title = str(label_pair[0]) + " vs " + str(label_pair[1])
        top_coeff_pos = np.argsort(sub_classifier)[-top_features:]
        top_coeff_neg = np.argsort(sub_classifier)[:top_features]

        pos_features_names = []
        pos_features_weights = []
        for index in top_coeff_pos:
            if sub_classifier[index] > 0:
                # print classifier[index]
                pos_features_weights.append(format(sub_classifier[index], '.3f'))
                pos_features_names.append(feature_names[index])

        neg_features_names = []
        neg_features_weights = []
        for index in top_coeff_neg:
            if sub_classifier[index] < 0:
                # print classifier[index]
                neg_features_weights.append(format(sub_classifier[index], '.3f'))
                neg_features_names.append(feature_names[index])


        all_feats = np.hstack([neg_features_names, pos_features_names])
        weight_data_pos = {'names': pos_features_names,
                           'weights': pos_features_weights}
        pred_source_pos = ColumnDataSource(data=weight_data_pos)

        weight_data_neg = {'names': neg_features_names,
                           'weights': neg_features_weights}
        pred_source_neg = ColumnDataSource(data=weight_data_neg)

        p = figure(y_range=all_feats, plot_height=int(30 * len(all_feats)),
                   # title='Feature importance weights for ' + main_title + ": " + title,
                   title=title,
                   plot_width=int(300), x_range=[-3, 3], toolbar_location='right',
                   tools="save,pan,box_zoom,reset,wheel_zoom")

        p.hbar(y=pos_features_names, height=0.5, left=0, right=pos_features_weights, color='navy')
        p.hbar(y=neg_features_names, height=0.5, left=neg_features_weights, right=0, color='red')

        labels_pos = LabelSet(x='weights', y='names', text='weights', text_font_size='8pt',
                              x_offset=2, y_offset=-1, source=pred_source_pos, render_mode='canvas')
        labels_neg = LabelSet(x='weights', y='names', text='weights', text_font_size='8pt',
                              x_offset=-35, y_offset=-1, source=pred_source_neg, render_mode='canvas')

        # p.y_range.range_padding = 0.4
        # p.axis.major_label_text_font_size = '8pt'
        # p.xgrid.grid_line_color = None
        # p.legend.location = "top_left"
        # p.legend.orientation = "horizontal"
        # p.xaxis.major_label_orientation = "horizontal"

        p.add_layout(labels_pos)
        p.add_layout(labels_neg)
        p.min_border_left = 100
        p.min_border_top = 20
        p.min_border_bottom = 20
        plots.append(p)

    # return plots[0]
    return gridplot(plots, ncols=3)


def feature_weights(pipeline, top_features = 10):
    if pipeline.learner._tag in ['svc']:
        return svc_feature_weights(pipeline, top_features)

    sk_pipeline = pipeline.sk_pipeline.get()
    classifier = sk_pipeline.named_steps['Classifier']

    if pipeline.learner.tag in ['xgb']:
        feature_weights = classifier.get_booster().get_fscore()

        sorted_fw = OrderedDict(sorted(list(feature_weights.items()), key=lambda t: t[0]))
        sorted_keys = sorted(sk_pipeline.named_steps['FeatureExtraction'].get_feature_names())
        print(sorted_fw)

        feat_importances = []
        for (ft, score) in list(sorted_fw.items()):
            index = int(ft.split("f")[1])
            feat_importances.append({'Feature': sorted_keys[index], 'Importance': score})
        feat_importances = DataFrame(feat_importances)
        feat_importances = feat_importances.sort_values(
            by='Importance', ascending=True).reset_index(drop=True)
        # Divide the importances by the sum of all importances
        # to get relative importances. By using relative importances
        # the sum of all importances will equal to 1, i.e.,
        # np.sum(feat_importances['importance']) == 1
        feat_importances['Importance'] /= feat_importances['Importance'].sum()
        feat_importances = feat_importances.round(3)

    elif pipeline.learner.tag in ['rf']:
        feature_weights = classifier.feature_importances_
        sorted_keys = sorted(sk_pipeline.named_steps['FeatureExtraction'].get_feature_names())
        feat_importances = []
        for (ft, key) in zip(feature_weights, sorted_keys):
            feat_importances.append({'Feature': key, 'Importance': ft})
        feat_importances = DataFrame(feat_importances)
        feat_importances = feat_importances.sort_values(
            by='Importance', ascending=True).reset_index(drop=True)

        # Divide the importances by the sum of all importances
        # to get relative importances. By using relative importances
        # the sum of all importances will equal to 1, i.e.,
        # np.sum(feat_importances['importance']) == 1
        feat_importances['Importance'] /= feat_importances['Importance'].sum()
        feat_importances = feat_importances.round(3)

    else:
        return None

    return visualize_df_feature_importance(
        feat_importances,
        pipeline.display_title
    )


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

    p.min_border_left = 100
    p.min_border_top = 20
    p.min_border_bottom = 50

    return p


def data_source_stats(data_source):
    # https://bokeh.pydata.org/en/latest/docs/user_guide/categorical.html#nested-categories
    title = data_source.display_title
    articles = [{
        'year': str(article.year),
        'label': data_source.labels[article.label]
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

    p.min_border_left = 100
    p.min_border_top = 20
    p.min_border_bottom = 50

    return p


