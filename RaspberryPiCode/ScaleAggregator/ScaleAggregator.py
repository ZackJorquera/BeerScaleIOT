import time
import sys
sys.path.append('../Tools/')
import ScaleInfoReaderWriter as ScaleIRW
import MongoReaderWriter as MongoRW
import MySQLReaderWriter as MySQLRW


dbToUse = "mongo" # TODO: From Config


def LoadDB():
    if dbToUse == "mongo": # use a switch
        db = MongoRW.MongoDBProfile()
    else:
        db = MySQLRW.MySQLDBProfile()
    return db


ScaleDataDB = LoadDB()

scaleInfoList = None
loopOn = 0
secsPerParsist = 10 # TODO: From Config
timeOfLastUpdate = None
while True:
    timeOfLastUpdate = time.time()

    if scaleInfoList == None or loopOn > 20 or len(scaleInfoList) != ScaleIRW.GetNumOfScales(): # TODO: get the 20 from Config
        scaleInfoList = ScaleIRW.GetListOfScaleInfos()

    if ScaleDataDB.Connected == True:
        successfulPushes = 0
        failedPushes = 0

        for si in scaleInfoList:
            try:
                ScaleDataDB.Write(si, (si.GetValue() * 100)) # There is a Write Function for both the MySQLRW and MongoRW classes
                successfulPushes += 1
            except:
                failedPushes += 1

        print str(successfulPushes) + " documents successfully added to database" \
              " with " + str(failedPushes) + " fails. " \
              "Waiting " + str(secsPerParsist) + " seconds before next update."

        if successfulPushes == 0 and len(scaleInfoList) != 0:
            print "DB failed to push, attempting Reconnect."
            ScaleDataDB.Reconnect()

    else:
        print "DB failed to connect, attempting Reconnect."
        ScaleDataDB.Reconnect()

    while time.time() - timeOfLastUpdate < secsPerParsist:
        time.sleep(1)

    loopOn += 1