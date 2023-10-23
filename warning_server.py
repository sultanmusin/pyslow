import threading
import os
from threading import Timer

from flask import Flask, render_template, request
from flask_socketio import SocketIO


LOG_FILE = os.path.join('logs', 'warn_server.log')


app = Flask(__name__)
socketio = SocketIO(app, async_mode=None)


def save_cache(msg: str):
    with open(LOG_FILE, 'a') as f:
        f.write(msg)


def load_cache():
    def read_cache():
        with open(LOG_FILE, 'r') as f:
            for l in f.readlines():
                socketio.emit('my_response', {'data': f'{l}'})
    thr = Timer(1, read_cache)
    thr.start()
    return thr


@app.route('/warning', methods=['GET', 'POST'])
def warn():
    msg = request.args.get('MSG')
    print(msg)
    if msg is None or msg == '':
        return ''
    socketio.emit('my_response', {'data': f'{msg}'})
    save_cache(msg)
    return ''


@app.route('/')
def index():
    load_cache()
    return render_template('warning_server.html', async_mode=socketio.async_mode)


def run_server():
    app.run(debug=True, use_reloader=False, port=9009)


def main():
    web_thread = threading.Thread(target=run_server)
    web_thread.start()


if __name__ == '__main__':
    main()
