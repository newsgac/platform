from data_engineering.postprocessing import Result
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar,
    FixedTicker, FuncTickFormatter)
from bokeh.embed import components
from bokeh.plotting import figure
import numpy as np


__author__ = 'abilgin'


class ResultVisualiser(object):

    def __init__(self):
        pass

    @staticmethod
    def retrieveHeatMapfromResult(normalisation_flag, result, title="", downsize=False):
        confusion_matrix = result.get_confusion_matrix()
        cm_normalised = Result.normalise_confusion_matrix(confusion_matrix)

        genre_names = result.genre_names

        colors = [ "#1B4F72", "#21618C", "#2874A6", "#2E86C1", "#3498DB", "#5DADE2", "#85C1E9", "#AED6F1",
                  "#D6EAF8", "#EBF5FB", "#FBFCFC"]
        if normalisation_flag:
            mapper = LinearColorMapper(palette=list(reversed(colors)), low=0, high=1)
        else:
            mapper = LinearColorMapper(palette=list(reversed(colors)), low=confusion_matrix.min(),
                                       high=confusion_matrix.max())

        actual = []
        predicted = []
        weight = []
        value = []
        class_sizes = []
        for x in range(0, len(genre_names)):
            for y in range(0, len(genre_names)):
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

        if downsize:
            ds_param = 0.5
            tool_loc = 'right'
        else:
            ds_param = 1
            tool_loc = 'above'

        p = figure(title=title,
                   y_range=list(reversed(genre_names)), x_range=list(genre_names),
                   x_axis_location="below", plot_width=int(850*ds_param), plot_height=int(800*ds_param),
                   tools=TOOLS, toolbar_location=tool_loc)

        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        if downsize:
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
                             ticker=BasicTicker(desired_num_ticks=len(colors)),
                             # ticker=FixedTicker(ticks=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]),
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
