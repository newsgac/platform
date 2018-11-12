from newsgac import config
from newsgac.app import app
from werkzeug.contrib.profiler import ProfilerMiddleware

app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
app.run(debug = True,
        host='0.0.0.0',
        port=config.flask_port,
        )
