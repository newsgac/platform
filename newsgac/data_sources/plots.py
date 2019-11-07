from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from pandas import DataFrame
from bokeh.palettes import Category20


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

    # p.min_border_left = 100
    # p.min_border_top = 20
    # p.min_border_bottom = 50

    return p