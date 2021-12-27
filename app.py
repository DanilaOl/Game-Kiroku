from flask import Flask, render_template, request, redirect, url_for, session, abort


app = Flask(__name__)
app.secret_key = 'kirokupass'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
