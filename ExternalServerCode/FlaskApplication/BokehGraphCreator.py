import math

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import Range1d, Plot, Label, HoverTool
from bokeh.models.glyphs import AnnularWedge
from bokeh.layouts import column, row

gaugeColors = ["#ffa500", "#00ff00", "#fbfbf1"]
lineColors = ["#ffa500", "#00ff00", "#fbfbf1"]
dotColors = ["#cc8400", "#00e500", "#e1e1d8"]

def GetStaticResources():
    return (INLINE.render_js(), INLINE.render_css())


def CreateGauge(percentage, scaleInfo):
    gaugeFig = Plot(x_range=Range1d(start=-1.25, end=1.25), y_range=Range1d(start=-1.25, end=1.25), plot_width=250, plot_height=250)
    gaugeFig.title.text = "Scale " + str(scaleInfo.Num) + ": " + scaleInfo.Name
    gaugeFig.title.align = 'center'
    gaugeFig.toolbar_location = None

    gaugeFig.border_fill_color = "#101010"
    gaugeFig.background_fill_color = "#101010"
    gaugeFig.title.text_color = "white"
    gaugeFig.outline_line_color = None

    glyph = AnnularWedge(x=0, y=0, inner_radius=.7, outer_radius=1, start_angle=math.pi / 2 - (2 * math.pi),
                         end_angle=math.pi / 2, fill_color="#444444", name="back")
    glyph2 = AnnularWedge(x=0, y=0, inner_radius=.7, outer_radius=1, start_angle=math.pi / 2 - (2 * math.pi * percentage),
                          end_angle=math.pi / 2, fill_color=gaugeColors[(scaleInfo.Num - 1) % len(gaugeColors)], name="front")
    PercentageText = Label(text_align='center', text=str(round((percentage * scaleInfo.MaxCapacity), 1)),text_color = 'white',
                           text_font_size="35px")
    lowerText = Label(text_align='center', y=-0.25, text=scaleInfo.Units, text_color='white')
    lowerText2 = Label(text_align='center', y=-0.48, text="Of " + str(scaleInfo.MaxCapacity), text_color='white')
    gaugeFig.add_glyph(glyph)
    gaugeFig.add_glyph(glyph2)
    gaugeFig.add_layout(PercentageText)
    gaugeFig.add_layout(lowerText)
    gaugeFig.add_layout(lowerText2)

    return gaugeFig


def CombineFigs(alignment='h', *args, **kwargs):
    if alignment == 'h':  # h is horizontal
        allFigs = row(*args)
    else:
        allFigs = column(*args)

    return allFigs


def GetComponentsFromFig(fig):
    return components(fig)


def CreatePlot(x, y, scaleInfo, dbNotWorking = False, minTimeSecs = 60 * 60, withDots = True):
    if x != list():
        time = x[len(x) - 1]
    else:
        time = 0
    if time < minTimeSecs: time = minTimeSecs

    if time > 3 * (60 * 60 * 24 * 30.41):  # 3 months
        timeScale = "Months"
        for i in range(len(x)):
            x[i] = x[i] / (60 * 60 * 24 * 30.41)
        time = time / (60 * 60 * 24 * 30.41)
    elif time > 4 * (60 * 60 * 24):  # 4 days
        timeScale = "Days"
        for i in range(len(x)):
            x[i] = x[i] / (60 * 60 * 24)
        time = time / (60 * 60 * 24)
    elif time > 5 * (60 * 60):  # 5 hours
        timeScale = "Hours"
        for i in range(len(x)):
            x[i] = x[i] / (60 * 60)
        time = time / (60 * 60)
    else:
        timeScale = "Minutes"
        for i in range(len(x)):
            x[i] = x[i] / (60)
        time = time / 60

    hover = HoverTool(names=['line'], tooltips=
    [
        (timeScale + " Ago", "@x"),
        ("Value", "@y")
    ], mode='vline')

    graphFig = figure(title="History Graph for Scale " + str(scaleInfo.Num) + ": " + scaleInfo.Name,
                      plot_width=600, plot_height=600, tools=[hover])
    graphFig.yaxis[0].axis_label = 'Percent Full'
    graphFig.xaxis[0].axis_label = timeScale + ' Ago'
    graphFig.toolbar_location = None

    graphFig.x_range = Range1d(time, -1 * (time/20.0))
    graphFig.y_range = Range1d(0, 103)

    graphFig.border_fill_color = "#101010"
    graphFig.background_fill_color = "#333333"
    graphFig.xgrid.grid_line_color = "#545454"
    graphFig.ygrid.grid_line_color = "#545454"
    graphFig.title.text_color = "white"
    graphFig.yaxis.axis_label_text_color = "white"
    graphFig.xaxis.axis_label_text_color = "white"

    graphFig.line(x, y, line_width=3, line_color=lineColors[(scaleInfo.Num - 1) % len(lineColors)], name='line')
    if withDots:
        graphFig.circle(x, y, size=10, color=dotColors[(scaleInfo.Num - 1) % len(dotColors)], alpha=0.7)

    if dbNotWorking:
        PercentageText = Label(x=time - time/4, y=60, text="DB Not Working",
                           text_color='white',
                           text_font_size="35px")
        graphFig.add_layout(PercentageText)

    return graphFig


def encodeToUTF8(html):
    return encode_utf8(html)
