import time
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

scaleInfoList = None
loopOn = 0
secsPerParsist = 10 # TODO: From Config
timeOfLastUpdate = None
while True:
    timeOfLastUpdate = time.time()

    if scaleInfoList == None or loopOn > 20 or len(scaleInfoList) != ScaleIRW.GetNumOfScales(): # TODO: get the 20 from Config
        scaleInfoList = ScaleIRW.GetListOfScaleInfos()

    if ScaleDataDB != None:
        for si in scaleInfoList:
            ScaleDataDB.Write(si, (si.GetValue() * 100)) # There is a Write Function for both the MySQLRW and MongoRW classes

    print str(len(scaleInfoList)) + " Documents added to database. Waiting " + str(secsPerParsist) + " seconds before next update"

    while time.time() - timeOfLastUpdate < secsPerParsist:
        time.sleep(1)

    loopOn += 1