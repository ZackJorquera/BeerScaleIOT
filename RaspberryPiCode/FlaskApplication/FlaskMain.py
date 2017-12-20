from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def start():
    return redirect(url_for('home'))


@app.route('/Home')
def home():
    return 'This is the homepage'


@app.route('/KegInfo=<int:num>')
def getKeg(num):
    return render_template("KegInfo.html",num=num)


@app.route('/ProgramInfo')
def InfoPage():
    return render_template("InfoPage.html")


if __name__ == "__main__":
    app.run(threaded=True,host='0.0.0.0')