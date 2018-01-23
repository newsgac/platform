from __future__ import division

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


