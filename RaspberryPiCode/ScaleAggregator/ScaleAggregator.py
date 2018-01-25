import time
import sys
sys.path.append('../Tools/')
import ScaleInfoReaderWriter as ScaleIRW
import MongoReaderWriter as MongoRW


ScaleDataDB = MongoRW.MongoDBProfile()


def GetListOfScaleInfos():
    scaleInfoList = list()

    for i in range(ScaleIRW.GetNumOfScales()):
        scaleInfoList.append(ScaleIRW.ScaleInfo(i + 1))

    return scaleInfoList

scaleInfoList = None
loopOn = 0
secsPerParsist = 20
timeOfLastUpdate = None
while True:
    timeOfLastUpdate = time.time()

    if scaleInfoList == None or loopOn > 20:
        scaleInfoList = GetListOfScaleInfos()

    for si in scaleInfoList:
        ScaleDataDB.Write(si, si.GetValue())

    print str(len(scaleInfoList)) + " Documents added to database. Waiting " + str(secsPerParsist) + " seconds before next update"

    while time.time() - timeOfLastUpdate < secsPerParsist:
        time.sleep(1)

    loopOn += 1