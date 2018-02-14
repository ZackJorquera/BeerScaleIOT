#!/usr/bin/python

import math
import threading

from flask import Flask, render_template, redirect, url_for, request

import sys
import BokehGraphCreater as GraphCreater
sys.path.append('../Tools/')
import ScaleInfoReaderWriter as ScaleIRW
import MongoReaderWriter as MongoRW
#import MySQLReaderWriter as MySQLRW


dbToUse = "mongo" # TODO: From Config


ScaleDataDB = None
reconnecting = False
lock = threading.Lock()


def LoadDB():
    if dbToUse == "mongo": # use a switch
        db = MongoRW.MongoDBProfile()
    else:
        db = MongoRW.MongoDBProfile()
        #db = MySQLRW.MySQLDBProfile()
    return db


def Reconnect():
    lock.acquire()
    ScaleDataDB.Reconnect()
    lock.release()


ScaleDataDB = LoadDB()

app = Flask(__name__)


@app.route('/')
def start():
    return redirect(url_for('home'))


@app.route('/Home')
def home():
    numOfScales = ScaleIRW.GetNumOfScales()

    js_resources, css_resources = GraphCreater.GetStaticResources()

    horizontalAlignments = list()
    for i in range(int(math.ceil(numOfScales/2.0))):
        scale1 = ScaleIRW.ScaleInfo(i*2+1)
        if i*2+1 < numOfScales:
            scale2 = ScaleIRW.ScaleInfo(i*2+2)
            horizontalAlignments.append(GraphCreater.CombineFigs('h', GraphCreater.CreateGauge(scale1.GetValue(), scale1),
                                                                      GraphCreater.CreateGauge(scale2.GetValue(), scale2)))
        else:
            horizontalAlignments.append(GraphCreater.CreateGauge(scale1.GetValue(), scale1))

    script, div = GraphCreater.GetComponentsFromFig(GraphCreater.CombineFigs('v', horizontalAlignments))

    return render_template("HomePage.html", num=numOfScales, plot_script=script, plot_div=div, js_resources=js_resources, css_resources=css_resources)


def CreateScaleGraphFromTimeFrame(num, hours = 150):
    ki = ScaleIRW.ScaleInfo(num)
    totalScales = ScaleIRW.GetNumOfScales()
    value = ki.GetValue()

    # Get the data
    dbNotWorking = False
    try:
        if ScaleDataDB.Connected == True:
            timeFrameData = ScaleDataDB.GetTimeFrameFor(ki, hours)
        else:
            raise Exception('GetTimeFrameFor failed')
    except:
        dbNotWorking = True
        timeFrameData = {'valueList': list(), 'timeStampList': list()}
        t = threading.Thread(target=Reconnect)
        t.start()

    y = timeFrameData['valueList']
    x = timeFrameData['timeStampList']

    js_resources, css_resources = GraphCreater.GetStaticResources()

    # render template
    gfig = GraphCreater.CreateGauge(value, ki)
    pfig = GraphCreater.CreatePlot(x, y, ki, dbNotWorking, withDots=False)
    script, div = GraphCreater.GetComponentsFromFig(GraphCreater.CombineFigs('v', gfig, pfig))

    html = render_template("ScaleInfo.html", num=num, type=ki.Type, name=ki.Name,
                           unit=ki.Units,
                           totalNum=totalScales, plot_script=script, plot_div=div,
                           js_resources=js_resources, css_resources=css_resources)

    return GraphCreater.encodeTOUTF8(html)


@app.route('/ScaleInfo=<int:num>', methods=['GET', 'POST'])
def getScale(num):
    if request.method == 'GET':
        return CreateScaleGraphFromTimeFrame(num)
    elif request.method == 'POST':
        if request.form['_action'] == 'DELETE':
            ki = ScaleIRW.ScaleInfo(num)
            ki.Delete()
            return redirect(url_for('home'))
        elif request.form['_action'] == 'ShowLastDay':
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=24))
        elif request.form['_action'] == 'ShowLastWeek':
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=(24*7)))
        elif request.form['_action'] == 'ShowHoursAgo':
            h = request.form['HoursAgo']
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=h))
        elif request.form['_action'] == 'ShowDefault':
            return redirect(url_for('getScale', num=num))


@app.route('/ScaleInfo=<int:num>t=<int:hours>', methods=['GET', 'POST'])
def getScaleWithTimeFrame(num, hours):
    if request.method == 'GET':
        return CreateScaleGraphFromTimeFrame(num, hours)
    elif request.method == 'POST':
        if request.form['_action'] == 'DELETE':
            ki = ScaleIRW.ScaleInfo(num)
            ki.Delete()
            return redirect(url_for('home'))
        elif request.form['_action'] == 'ShowLastDay':
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=24))
        elif request.form['_action'] == 'ShowLastWeek':
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=(24*7)))
        elif request.form['_action'] == 'ShowHoursAgo':
            h = request.form['HoursAgo']
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=h))
        elif request.form['_action'] == 'ShowDefault':
            return redirect(url_for('getScale', num=num))


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