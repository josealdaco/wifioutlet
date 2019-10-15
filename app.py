from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/', methods=['GET'])
def log_page():
    render_template('login_page.html')


if __name__ == '__main__':
    app.run(debug=True, port=6060)
