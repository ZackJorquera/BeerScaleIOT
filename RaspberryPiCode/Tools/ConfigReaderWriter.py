import re
import os.path


configFilePath = "../config.cfg"

cfgVars = \
{
    'dbToUse': "mongo",
    'simulateData': "false",
    'useCQuickPulse': "true",
    'useMedianOfData': "true",

    'aggregatorSecsPerParsist': "60",
    'aggregatorLoopsOfParsists': "20",
    'aggregatorPrintPushes': "false",

    'dbHostServer': "localhost",
    'dbHostPort': "27017",
    'dbName': "ScaleLiquidRemainingIOT",
    'dbCollectionName': "ScaleData"
}


def CreateNewCFGFile():
    f = open(configFilePath, "w+")

    for key, value in cfgVars.iteritems():
        f.write("<" + key + ">" + str(value) + "<\\" + key + ">\n")
    f.close()
    return


def ReadInVals():
    f = open(configFilePath, "r")

    lines = f.readlines()

    for key, value in cfgVars.iteritems():
        for line in lines:
            parts = re.findall(r"[\w\.']+", line)
            if parts[0] == key:
                cfgVars[key] = parts[1]
    f.close()
    return


if not os.path.isfile(configFilePath):
    CreateNewCFGFile()
else:
    ReadInVals()


