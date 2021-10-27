from app import app, routes, scheduler
import os


if __name__ == '__main__':
    # this is necessary so that it does not run twice if debug - true
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler.start()
    app.run()
