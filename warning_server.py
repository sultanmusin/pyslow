import threading
from flask import Flask, request

app = Flask(__name__)


@app.route('/warning', methods=['GET', 'POST'])
def warn():
    msg = request.args.get('MSG')
    print(msg)
    return ''


@app.route('/')
def webpage():
    return ''


def run_server():
    app.run(debug=True, use_reloader=False, port=9009)


def main():
    web_thread = threading.Thread(target=run_server)
    web_thread.start()


if __name__ == '__main__':
    main()
