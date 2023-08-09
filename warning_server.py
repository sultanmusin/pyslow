import threading
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

app = Flask(__name__)
socketio = SocketIO(app, async_mode=None)

@app.route('/warning', methods=['GET', 'POST'])
def warn():
    msg = request.args.get('MSG')
    print(msg)
    socketio.emit('my_response', {'data': f'{msg}'})
    return ''


@app.route('/')
def index():
    return render_template('warning_server.html', async_mode=socketio.async_mode)


def run_server():
    app.run(debug=True, use_reloader=False, port=9009)


def main():
    web_thread = threading.Thread(target=run_server)
    web_thread.start()


if __name__ == '__main__':
    main()
