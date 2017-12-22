#!/usr/bin/python

from flask import Flask, render_template, redirect, url_for

import KegInfoReaderWriter as KegIRW

app = Flask(__name__)


@app.route('/')
def start():
    return redirect(url_for('home'))


@app.route('/Home')
def home():
    numOfKegs = KegIRW.GetNumOfScales()
    return render_template("HomePage.html", num=numOfKegs)


@app.route('/KegInfo=<int:num>')
def getKeg(num):
    ki = KegIRW.KegInfo(num)
    return render_template("KegInfo.html", num=num, type=ki.Type, name=ki.Name, capacity=ki.MaxCapacity, unit=ki.Units, value=ki.Value)


@app.route('/ProgramInfo')
def InfoPage():
    return render_template("InfoPage.html")


if __name__ == "__main__":
    app.run(threaded=True,host='0.0.0.0')