import time
import sys
sys.path.append('../Tools/')
import ScaleInfoReaderWriter as ScaleIRW
import DatabaseReaderWriter as DBRW
import ConfigReaderWriter as CfgRW



def LoadDB():
    if CfgRW.cfgVars["dbToUse"] == "Mongo":
        db = DBRW.MongoDBProfile()
    else:
        db = DBRW.MongoDBProfile()
        # db = DBRW.MySQLDBProfile()
    db.Connect()
    return db


ScaleDataDB = LoadDB()

scaleInfoList = None
loopOn = 0
secsPerParsist = int(CfgRW.cfgVars["aggregatorSecsPerParsist"],10) # try catch
loopsOfParsists = int(CfgRW.cfgVars["aggregatorLoopsOfParsists"],10)
timeOfLastUpdate = None

print "Starting Aggregation every " + str(secsPerParsist) + " Second."
if ScaleDataDB.Client != None:
    print "Outputting to " + CfgRW.cfgVars["dbToUse"] + " database " + ScaleDataDB.DBName + " at: " + str(ScaleDataDB.Client.address)

while True:
    timeOfLastUpdate = time.time()

    if scaleInfoList is None or loopOn > loopsOfParsists or len(scaleInfoList) != ScaleIRW.GetNumOfScales():
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

        if CfgRW.cfgVars["aggregatorPrintPushes"].upper() == "TRUE":
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
        if ScaleDataDB.Client != None:
            print "Outputting to " + CfgRW.cfgVars["dbToUse"] + " database " + ScaleDataDB.DBName + " at: " + str(ScaleDataDB.Client.address)

    while time.time() - timeOfLastUpdate < secsPerParsist:
        time.sleep(1)

    loopOn += 1