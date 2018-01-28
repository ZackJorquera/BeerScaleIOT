#!/usr/bin/python

from flask import Flask, render_template, redirect, url_for, request

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import Range1d, HoverTool, WheelZoomTool, SaveTool, PanTool, ResetTool

import sys
sys.path.append('../Tools/')
import ScaleInfoReaderWriter as ScaleIRW
import MongoReaderWriter as MongoRW
import MySQLReaderWriter as MySQLRW


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

    # Graph Colors
    lineColors = ["#ffa500", "#00ff00", "#fbfbf1"]
    dotColors = ["#cc8400", "#00e500", "#e1e1d8"]

    # Get the data
    timeFrameData = ScaleDataDB.GetTimeFrameFor(ki, 1000)

    y = timeFrameData['valueList']
    x = timeFrameData['timeStampList']

    # Create the tools
    hover = HoverTool(tooltips=
    [
        ("Secs Ago", "@x"),
        ("Value", "@y")
    ])
    save = SaveTool()
    wheel_zoom = WheelZoomTool()
    pan = PanTool()
    reset = ResetTool()

    fig = figure(title="History Graph", plot_width=600, plot_height=600, tools=[wheel_zoom, save, hover, pan, reset])
    fig.yaxis[0].axis_label = 'Present Full'
    fig.xaxis[0].axis_label = 'Seconds Ago'

    #Set Range
    fig.x_range = Range1d(-1050, 25)
    fig.y_range = Range1d(-5, 110)

    # Set Colors
    fig.border_fill_color = "#101010"
    fig.background_fill_color = "#333333"
    fig.xgrid.grid_line_color = "#545454"
    fig.ygrid.grid_line_color = "#545454"
    fig.title.text_color = "#A8A8A8"
    fig.yaxis.axis_label_text_color = "#A8A8A8"
    fig.xaxis.axis_label_text_color = "#A8A8A8"

    # Pot the Graph
    fig.line(x, y, line_width=3, line_color=lineColors[(num - 1) % len(lineColors)])
    fig.circle(x, y, size=10, color=dotColors[(num - 1) % len(dotColors)], alpha=0.7)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)

    html = render_template("ScaleInfo.html", num=num, type=ki.Type, name=ki.Name,
                           capacity=ki.MaxCapacity, unit=ki.Units, value=ki.GetValue(),
                           totalNum=totalScales, plot_script=script, plot_div=div,
                           js_resources=js_resources, css_resources=css_resources)

    return encode_utf8(html)


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