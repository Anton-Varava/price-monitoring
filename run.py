from app import app, routes, scheduler
import os


if __name__ == '__main__':
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("loaded scheduler")
        scheduler.start()
    app.run()
