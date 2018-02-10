import time
import sys
sys.path.append('../Tools/')
import ScaleInfoReaderWriter as ScaleIRW
import MongoReaderWriter as MongoRW
#import MySQLReaderWriter as MySQLRW


dbToUse = "mongo" # TODO: From Config
printPushes = False


def LoadDB():
    if dbToUse == "mongo": # use a switch
        db = MongoRW.MongoDBProfile()
    else:
        db = MongoRW.MongoDBProfile()
        # db = MySQLRW.MySQLDBProfile()
    return db


ScaleDataDB = LoadDB()

scaleInfoList = None
loopOn = 0
secsPerParsist = 60 # TODO: From Config
timeOfLastUpdate = None
while True:
    timeOfLastUpdate = time.time()

    if scaleInfoList is None or loopOn > 20 or len(scaleInfoList) != ScaleIRW.GetNumOfScales(): # TODO: get the 20 from Config
        scaleInfoList = ScaleIRW.GetListOfScaleInfos()

    if ScaleDataDB.Connected:
        successfulPushes = 0
        failedPushes = 0

        for si in scaleInfoList:
            try:
                ScaleDataDB.Write(si, (si.GetValue() * 100)) # There is a Write Function for both the MySQLRW and MongoRW classes
                successfulPushes += 1
            except:
                failedPushes += 1

        if printPushes:
            print str(successfulPushes) + " documents successfully added to database" \
                  " with " + str(failedPushes) + " fails. " \
                  "Waiting " + str(secsPerParsist) + " seconds before next update."
        else:
            if failedPushes > 0:
                print str(failedPushes) + " documents failed to push to database."

        if successfulPushes == 0 and len(scaleInfoList) != 0:
            print "DB failed to push, attempting Reconnect."
            ScaleDataDB.Reconnect()

    else:
        print "DB failed to connect, attempting Reconnect."
        ScaleDataDB.Reconnect()

    while time.time() - timeOfLastUpdate < secsPerParsist:
        time.sleep(1)

    loopOn += 1