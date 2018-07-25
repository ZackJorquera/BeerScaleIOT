import time
import sys
import logging
import os
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


def printAndLog(msg, loglevel):
    print msg
    logger.log(loglevel, msg)


def createLogger():
    logDir = "../Log"
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    logPath = "../Log/Log.txt"
    file_handler = logging.FileHandler(logPath)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s\t%(asctime)s \t%(message)s')
    file_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    return logger


ScaleDataDB = LoadDB()
logger = createLogger()
scaleInfoList = None
loopOn = 0
secsPerPersist = int(CfgRW.cfgVars["aggregatorSecsPerPersist"],10) # try catch
loopsOfPersists = int(CfgRW.cfgVars["aggregatorLoopsOfPersists"],10)
timeOfLastUpdate = None

printAndLog("Starting Aggregation every " + str(secsPerPersist) + " Second.", logging.INFO)
if ScaleDataDB.Client != None:
    printAndLog("Outputting to " + CfgRW.cfgVars["dbToUse"] + " database " + ScaleDataDB.DBName + " at: " + str(ScaleDataDB.Client.address), logging.INFO)

while True:
    if CfgRW.cfgVars["uselatestFromMongoAsCurrent"].upper() == "TRUE":
        break

    timeOfLastUpdate = time.time()

    if scaleInfoList is None or loopOn > loopsOfPersists or len(scaleInfoList) != ScaleIRW.GetNumOfScales():
        try:
            scaleInfoList = ScaleIRW.GetListOfScaleInfos()
        except Exception as error:
            printAndLog(str(error), logging.ERROR)
            break

    if ScaleDataDB.Connected:
        successfulPushes = 0
        failedPushes = 0

        for si in scaleInfoList:
            try:
                if si.Failed:
                    raise Exception()
                ScaleDataDB.Write(si, (si.GetValue() * 100)) # There is a Write Function for both the MySQLRW and MongoRW classes
                successfulPushes += 1
            except:
                failedPushes += 1

        if CfgRW.cfgVars["aggregatorPrintPushes"].upper() == "TRUE":
            printAndLog(str(successfulPushes) + " documents successfully added to database" \
                  " with " + str(failedPushes) + " fails. " \
                  "Waiting " + str(secsPerPersist) + " seconds before next update.", logging.INFO)
        else:
            if failedPushes > 0:
                printAndLog(str(failedPushes) + " documents failed to push to database.", logging.ERROR)

        if successfulPushes == 0 and len(scaleInfoList) != 0:
            printAndLog("DB failed to push, attempting Reconnect.", logging.ERROR)
            if ScaleDataDB.Reconnect():
                    printAndLog("Successfully reconnected to " + CfgRW.cfgVars["dbToUse"] + " database " + ScaleDataDB.DBName + " at: " + str(ScaleDataDB.Client.address), logging.INFO)

    else:
        printAndLog("DB failed to connect, attempting Reconnect.", logging.ERROR)
        ScaleDataDB.Reconnect()
        if ScaleDataDB.Client != None:
            printAndLog("Outputting to " + CfgRW.cfgVars["dbToUse"] + " database " + ScaleDataDB.DBName + " at: " + str(ScaleDataDB.Client.address), logging.INFO)

    while time.time() - timeOfLastUpdate < secsPerPersist:
        time.sleep(1)

    loopOn += 1