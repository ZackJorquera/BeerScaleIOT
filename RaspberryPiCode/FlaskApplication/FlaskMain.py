#!/usr/bin/python

import math
import threading
import os
import time
import datetime
import sys

from flask import Flask, render_template, redirect, url_for, request, send_from_directory, session

import BokehGraphCreator as GraphCreater
sys.path.append('../Tools/')
import ScaleInfoReaderWriter as ScaleIRW
import DatabaseReaderWriter as DBRW
import ConfigReaderWriter as CfgRW


exportDir = "../Exports"

ScaleDataDB = None
reconnecting = False
lock = threading.Lock()


def LoadDB():
    if CfgRW.cfgVars["dbToUse"] == "mongo":
        db = DBRW.MongoDBProfile()
    else:
        db = DBRW.MongoDBProfile()
        # db = DBRW.MySQLDBProfile()
    db.Connect()
    return db


def Reconnect():
    lock.acquire()
    ScaleDataDB.Reconnect()
    lock.release()


ScaleDataDB = LoadDB()

app = Flask(__name__)
app.secret_key = "Not Random. Oh Noes"
# It doesn't matter becuase im not storing passwords or anything

@app.route('/')
def start():
    return redirect(url_for('home'))


@app.route('/Home', methods=['GET'])
def home():
    numOfScales = ScaleIRW.GetNumOfScales()

    js_resources, css_resources = GraphCreater.GetStaticResources()

    horizontalAlignments = list()
    for i in range(int(math.ceil(numOfScales/2.0))):
        scale1 = ScaleIRW.ScaleInfo(i*2+1)
        scale1.startGPIO()
        if i*2+1 < numOfScales:
            scale2 = ScaleIRW.ScaleInfo(i*2+2)
            scale2.startGPIO()
            horizontalAlignments.append(GraphCreater.CombineFigs('h', GraphCreater.CreateGauge(scale1.GetValue(), scale1),
                                                                      GraphCreater.CreateGauge(scale2.GetValue(), scale2)))
        else:
            horizontalAlignments.append(GraphCreater.CreateGauge(scale1.GetValue(), scale1))

    script, div = GraphCreater.GetComponentsFromFig(GraphCreater.CombineFigs('v', horizontalAlignments))

    return render_template("HomePage.html", num=numOfScales, plot_script=script, plot_div=div, js_resources=js_resources, css_resources=css_resources)

@app.route('/Home', methods=['POST'])
def homePost():
    if request.form["submit"] == "Restart Pi":
        os.system('sudo reboot')
    if request.form["submit"] == "Start ScaleAggregator":
        os.system("(cd ../ScaleAggregator/; python ScaleAggregator.py &)")
    return redirect(url_for('home'))


def CreateScaleGraphFromTimeFrame(num, hours=730):
    ki = ScaleIRW.ScaleInfo(num)

    didFail = "False"
    failMsg = "None"

    if 'failMsg' in session:
        failMsg = session.pop('failMsg', None)
        didFail = "True"

    if not ki.Failed:
        ki.startGPIO()
        value = ki.GetValue()
    else:
        if failMsg == "None":
            failMsg = "An error occurred while loading scale info."
        value = 0
        didFail = "True"

    totalScales = ScaleIRW.GetNumOfScales()

    # Get the data
    dbNotWorking = False
    try:
        if ScaleDataDB.Connected == True:
            timeFrameData = ScaleDataDB.GetTimeFrameFor(ki, hours)
        else:
            raise Exception('GetTimeFrameFor failed')
    except:
        dbNotWorking = True
        ScaleDataDB.Connected = False
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
                           unit=ki.Units, didFail=didFail, failMsg=failMsg,
                           totalNum=totalScales, plot_script=script, plot_div=div,
                           js_resources=js_resources, css_resources=css_resources)

    return GraphCreater.encodeToUTF8(html)


def ExportScaleGraphFromTimeFrame(num, hours=730):
    ki = ScaleIRW.ScaleInfo(num)
    if ki.Failed:
        session['failMsg'] = "An error occurred while loading scale info."
        if hours == 730:
            return redirect(url_for('getScale', num))
        else:
            return redirect(url_for('getScaleWithTimeFrame', num, hours))

    dbNotWorking = False
    try:
        if ScaleDataDB.Connected == True:
            timeFrameData = ScaleDataDB.GetTimeFrameFor(ki, hours)
        else:
            raise Exception('GetTimeFrameFor failed')
    except:
        dbNotWorking = True
        ScaleDataDB.Connected = False
        session['failMsg'] = "An error occurred while exporting historical data."
        if hours == 730:
            return redirect(url_for('getScale', num))
        else:
            return redirect(url_for('getScaleWithTimeFrame', num, hours))

    y = timeFrameData['valueList']
    x = timeFrameData['timeStampList']

    if not os.path.isdir(exportDir):
        os.makedirs(exportDir)
    timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
    exportPath = exportDir + "/" + timeStamp + ".csv"

    FW = open(exportPath, "w")

    FW.write("Secs Ago,Value\n")
    for i in range(len(x)):
        FW.write(str(x[i]) + "," + str(y[i]))
        FW.write("\n")
    FW.close()

    return send_from_directory(exportDir, timeStamp + ".csv", as_attachment=True)


@app.route('/ScaleInfo=<int:num>', methods=['GET', 'POST'])
def getScale(num):
    if request.method == 'GET':
        return CreateScaleGraphFromTimeFrame(num)
    elif request.method == 'POST':
        if request.form['_action'] == "Export":
            return ExportScaleGraphFromTimeFrame(num)
        elif request.form['_action'] == 'DELETE':
            ki = ScaleIRW.ScaleInfo(num)
            ki.Delete()
            return redirect(url_for('home'))
        elif request.form['_action'] == 'ShowLastDay':
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=24))
        elif request.form['_action'] == 'ShowLastWeek':
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=(24*7)))
        elif request.form['_action'] == 'ShowHoursAgo':
            h = request.form['HoursAgo']
            try:
                int(h)
            except:
                session['failMsg'] = "An error occurred while processing your input."
                return redirect(url_for('getScale', num=num))
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=h))
        elif request.form['_action'] == 'ShowDefault':
            return redirect(url_for('getScale', num=num))


@app.route('/ScaleInfo=<int:num>t=<int:hours>', methods=['GET', 'POST'])
def getScaleWithTimeFrame(num, hours):
    if request.method == 'GET':
        return CreateScaleGraphFromTimeFrame(num, hours)
    elif request.method == 'POST':
        if request.form['_action'] == "Export":
            return ExportScaleGraphFromTimeFrame(num, hours)
        elif request.form['_action'] == 'DELETE':
            ki = ScaleIRW.ScaleInfo(num)
            ki.Delete()
            return redirect(url_for('home'))
        elif request.form['_action'] == 'ShowLastDay':
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=24))
        elif request.form['_action'] == 'ShowLastWeek':
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=(24*7)))
        elif request.form['_action'] == 'ShowHoursAgo':
            h = request.form['HoursAgo']
            try:
                int(h)
            except:
                session['failMsg'] = "An error occurred while processing your input."
                return redirect(url_for('getScaleWithTimeFrame', num=num, hours=hours))
            return redirect(url_for('getScaleWithTimeFrame', num=num, hours=h))
        elif request.form['_action'] == 'ShowDefault':
            return redirect(url_for('getScale', num=num))


@app.route('/AddScale')
def addScale():
    if 'failMsg' not in session:
        didFail = "False"
        failMsg = "None"
    else:
        didFail = "True"
        failMsg = session.pop('failMsg', None)
    num = ScaleIRW.GetNumOfScales()
    return render_template("AddScale.html", num=num, didFail=didFail, failMsg=failMsg)


@app.route('/AddScale<int:num>/Range', methods=['GET', 'POST'])
def setScaleRange(num):
    totalNum = ScaleIRW.GetNumOfScales()
    s = ScaleIRW.ScaleInfo(num)
    if request.method == 'GET':
        return render_template("SetRange.html", totalNum=totalNum, num=num, lr=s.EmptyValue, ur=s.FullValue)
    elif request.method == 'POST':
        s.startGPIO()
        if request.form['submit'] == 'Get Empty Value':
            s.GetLowerRange()
            s.SetRange(s.EmptyValue, request.form['FullValue'])
            return redirect(url_for('setScaleRange', num=num))
        elif request.form['submit'] == 'Get Full Value':
            s.GetUpperRange()
            s.SetRange(request.form['EmptyValue'], s.FullValue)
            return redirect(url_for('setScaleRange', num=num))
        elif request.form['submit'] == 'Set':
            s.SetRange(request.form['EmptyValue'], request.form['FullValue'])
            return redirect(url_for('getScale', num=num))


@app.route('/AddScale', methods=['POST'])
def addScalePost():
    Type = request.form['Type']
    Name = request.form['Name']
    MaxCapacity = request.form['MaxCapacity']
    Units = request.form['Units']
    DataPin = request.form['DataPin']
    ClockPin = request.form['ClockPin']

    oldNumOfScales = ScaleIRW.GetNumOfScales()

    num = ScaleIRW.AddScaleInfoToFile(Type, Name, MaxCapacity, Units, DataPin, ClockPin)
    if oldNumOfScales == ScaleIRW.GetNumOfScales():
        session['failMsg'] = "An error occurred while processing your input."
        return redirect(url_for('addScale'))
    return redirect(url_for('setScaleRange', num=num))


@app.route('/Settings', methods=['GET','POST'])
def changeSettings():
    totalNum = ScaleIRW.GetNumOfScales()

    if request.method == 'GET':
        currentDBToUse = CfgRW.cfgVars["dbToUse"]
        currentSimulateData = CfgRW.cfgVars["simulateData"]
        currentUseCQuickPulse = CfgRW.cfgVars["useCQuickPulse"]
        currentUseMedianOfData = CfgRW.cfgVars["useMedianOfData"]

        launchScaleAggregatorOnStart = CfgRW.cfgVars["launchScaleAggregatorOnStart"]

        currentAggregatorSecsPerPersist = CfgRW.cfgVars["aggregatorSecsPerPersist"]
        currentAggregatorLoopsOfPersists = CfgRW.cfgVars["aggregatorLoopsOfPersists"]
        currentAggregatorPrintPushes = CfgRW.cfgVars["aggregatorPrintPushes"]

        currentDBHostServer = CfgRW.cfgVars["dbHostServer"]
        currentDBHostPort = CfgRW.cfgVars["dbHostPort"]
        currentDBName = CfgRW.cfgVars["dbName"]
        currentDBCollectionName = CfgRW.cfgVars["dbCollectionName"]

        if 'failMsg' not in session:
            didFail = "False"
            failMsg = "None"
        else:
            didFail = "True"
            failMsg = session.pop('failMsg', None)

        return render_template("ChangeSettingPage.html", totalNum=totalNum, currentDBToUse=currentDBToUse, currentSimulateData=currentSimulateData, currentUseCQuickPulse=currentUseCQuickPulse,
                               currentUseMedianOfData=currentUseMedianOfData, currentAggregatorSecsPerPersist=currentAggregatorSecsPerPersist, currentAggregatorLoopsOfPersists=currentAggregatorLoopsOfPersists,
                               currentAggregatorPrintPushes=currentAggregatorPrintPushes, currentDBHostServer=currentDBHostServer, currentDBHostPort=currentDBHostPort, currentDBName=currentDBName,
                               currentDBCollectionName=currentDBCollectionName, num=ScaleIRW.GetNumOfScales(), didFail=didFail, failMsg=failMsg, currentLaunchScaleAggregatorOnStart=launchScaleAggregatorOnStart)
    elif request.method == 'POST':
        try:
            int(request.form['aggregatorSecsPerPersist'])
            int(request.form['aggregatorLoopsOfPersists'])
        except:
            session['failMsg'] = "An error occurred while processing your input."
            return redirect(url_for('changeSettings'))
        CfgRW.cfgVars["dbToUse"] = request.form['dbToUse']
        CfgRW.cfgVars["simulateData"] = request.form['simulateData']
        CfgRW.cfgVars["useCQuickPulse"] = request.form['useCQuickPulse']
        CfgRW.cfgVars["useMedianOfData"] = request.form['useMedianOfData']
        CfgRW.cfgVars["launchScaleAggregatorOnStart"] = request.form['launchScaleAggregatorOnStart']
        CfgRW.cfgVars["aggregatorSecsPerPersist"] = request.form['aggregatorSecsPerPersist']
        CfgRW.cfgVars["aggregatorLoopsOfPersists"] = request.form['aggregatorLoopsOfPersists']
        CfgRW.cfgVars["aggregatorPrintPushes"] = request.form['aggregatorPrintPushes']
        CfgRW.cfgVars["dbHostServer"] = request.form['dbHostServer']
        CfgRW.cfgVars["dbHostPort"] = request.form['dbHostPort']
        CfgRW.cfgVars["dbName"] = request.form['dbName']
        CfgRW.cfgVars["dbCollectionName"] = request.form['dbCollectionName']

        CfgRW.CreateNewCFGFile()

        if request.form["submit"] == "Set and Restart":
            os.system('sudo reboot')
        return redirect(url_for('home'))


if __name__ == "__main__":
    if CfgRW.cfgVars["launchScaleAggregatorOnStart"].upper() == "TRUE":
        os.system("(cd ../ScaleAggregator/; python ScaleAggregator.py &)")
    app.run(threaded=True, host='0.0.0.0')
