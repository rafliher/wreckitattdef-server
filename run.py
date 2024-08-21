# run.py
import logging
from app import app, socketio

# Disable Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == '__main__':
    socketio.run(app, debug=False, host="0.0.0.0", use_reloader=False, allow_unsafe_werkzeug=True)
    # app.run(debug=False, host="0.0.0.0", use_reloader=False)
    # app.run(debug=True, host="0.0.0.0", use_reloader=False)
