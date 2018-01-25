#!/usr/bin/python

from flask import Flask, render_template, redirect, url_for, request

import sys
sys.path.append('../Tools/')
import ScaleInfoReaderWriter as ScaleIRW

app = Flask(__name__)


@app.route('/')
def start():
    return redirect(url_for('home'))


@app.route('/Home')
def home():
    numOfScales = ScaleIRW.GetNumOfScales()
    return render_template("HomePage.html", num=numOfScales)


@app.route('/ScaleInfo=<int:num>')
def getScale(num):
    ki = ScaleIRW.ScaleInfo(num)
    totalScales = ScaleIRW.GetNumOfScales()
    return render_template("ScaleInfo.html", num=num, type=ki.Type, name=ki.Name, capacity=ki.MaxCapacity, unit=ki.Units, value=ki.GetValue(), totalNum=totalScales)


@app.route('/ScaleInfo=<int:num>', methods=['POST'])
def getScalePost(num):
    ki = ScaleIRW.ScaleInfo(num)
    ki.Delete()
    return redirect(url_for('home'))


@app.route('/AddScale')
def addScale():
    num = ScaleIRW.GetNumOfScales()
    return render_template("AddScale.html", num=num)


@app.route('/AddScale', methods=['POST'])
def addScalePost():
    Type = request.form['Type']
    Name = request.form['Name']
    MaxCapacity = request.form['MaxCapacity']
    Units = request.form['Units']
    DataPin = request.form['DataPin']
    ClockPin = request.form['ClockPin']

    num = ScaleIRW.AddScaleInfoToFile(Type, Name, MaxCapacity, Units, DataPin, ClockPin)
    return redirect(url_for('getScale', num=num))


@app.route('/ProgramInfo')
def InfoPage():
    return render_template("InfoPage.html")


if __name__ == "__main__":
    app.run(threaded=True,host='0.0.0.0')