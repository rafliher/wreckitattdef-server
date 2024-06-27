# run.py

from app import app

if __name__ == '__main__':
    # app.run(debug=False, host="0.0.0.0", use_reloader=False)
    app.run(debug=True, host="0.0.0.0", use_reloader=False)
