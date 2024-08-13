# run.py

from app import app, socketio

if __name__ == '__main__':
    socketio.run(app, debug=False, host="0.0.0.0", use_reloader=False)
    # app.run(debug=False, host="0.0.0.0", use_reloader=False)
    # app.run(debug=True, host="0.0.0.0", use_reloader=False)
