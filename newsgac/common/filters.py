from newsgac.genres import genre_labels


def load_filters(app):
    @app.context_processor
    def inject_bokeh_js_css():
        from bokeh.resources import CDN
        return dict(bokeh_js_css=CDN)

    @app.context_processor
    def inject_pymodm_fields():
        from pymodm import fields
        return dict(pymodm_fields=fields)

    @app.template_filter('datetime')
    def _format_datetime(date):
        return date.strftime('%d-%m-%Y %H:%M')

    @app.template_filter('dict_string')
    def _format_dict_string(dict_val):
        return ', '.join("%s=%s" % (key, val) for (key, val) in dict_val.iteritems() if key != '_cls')

    @app.template_filter('code_to_label')
    def _code_to_label(code):
        return genre_labels[code]
