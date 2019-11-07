from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

from newsgac.ace import ACE

__author__ = 'abilgin'


def metric_plot(pipelines, field, title='', color='#000000'):
    data_source = ColumnDataSource({
        'pipeline_title': [pipeline.display_title for pipeline in pipelines],
        'value': [getattr(pipeline.result, field) for pipeline in pipelines]
    })

    plot = figure(
        plot_height=max(300, 50 * len(pipelines)),
        title=title,
        plot_width=400,
        x_range=[0, 1.05],
        y_range=[pipeline.display_title for pipeline in pipelines],
        toolbar_location='right',
        tools="save,pan,box_zoom,reset,wheel_zoom"
    )

    plot.hbar(
        source=data_source,
        # x='value',
        y='pipeline_title',
        color=color,
        height=0.5,
        right='value',
    )

    return plot


def metrics_plots(ace: ACE):
    metrics = [
        {
            'title': 'F1 Score (weighted)',
            'field': 'fmeasure_weighted',
            'color': '#ff0000',
        },
        {
            'title': 'F1 Score (micro)',
            'field': 'fmeasure_micro',
            'color': '#ff0000',
        },
        {
            'title': 'F1 Score (macro)',
            'field': 'fmeasure_macro',
            'color': '#ff0000',
        },
        {
            'title': 'Precision (weighted)',
            'field': 'precision_weighted',
            'color': '#00ff00',
        },
        {
            'title': 'Precision (micro)',
            'field': 'precision_micro',
            'color': '#00ff00',
        },
        {
            'title': 'Precision (macro)',
            'field': 'precision_macro',
            'color': '#00ff00',
        },
        {
            'title': 'Recall (weighted)',
            'field': 'recall_weighted',
            'color': '#0000ff',
        },
        {
            'title': 'Recall (micro)',
            'field': 'recall_micro',
            'color': '#0000ff',
        },
        {
            'title': 'Recall (macro)',
            'field': 'recall_macro',
            'color': '#0000ff',
        },
        {
            'title': 'Accuracy',
            'field': 'accuracy',
            'color': '#000000',
        },
        {
            'title': 'Cohen\'s Kappa',
            'field': 'cohens_kappa',
            'color': '#000000',
        }
    ]

    return [metric_plot(
        ace.pipelines,
        metric['field'],
        metric['title'],
        metric['color']
    ) for metric in metrics]



