#!/usr/bin/python

import math

from flask import Flask, render_template, redirect, url_for, request

import sys
sys.path.append('../Tools/')
import ScaleInfoReaderWriter as ScaleIRW
import MongoReaderWriter as MongoRW
import MySQLReaderWriter as MySQLRW
import BokehGraphCreater as GraphCreater


dbToUse = "mongo" # TODO: From Config

if dbToUse == "mongo": # use a switch
    ScaleDataDB = MongoRW.MongoDBProfile()
else:
    ScaleDataDB = MySQLRW.MySQLDBProfile()

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
    value = ki.GetValue()

    # Get the data
    timeFrameData = ScaleDataDB.GetTimeFrameFor(ki, 31)

    y = timeFrameData['valueList']
    x = timeFrameData['timeStampList']

    js_resources,css_resources = GraphCreater.GetStaticResources()

    # render template
    gfig = GraphCreater.CreateGauge(value, ki)
    pfig = GraphCreater.CreatePlot(x,y, ki, time = 30, withDots = False)
    script, div = GraphCreater.ConvertFigsToComponents('c', gfig, pfig)

    html = render_template("ScaleInfo.html", num=num, type=ki.Type, name=ki.Name,
                           unit=ki.Units,
                           totalNum=totalScales, plot_script=script, plot_div=div,
                           js_resources=js_resources, css_resources=css_resources)

    return GraphCreater.encodeTOUTF8(html)


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


if __name__ == "__main__":
    app.run(threaded=True,host='0.0.0.0')