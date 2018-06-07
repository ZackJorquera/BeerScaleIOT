import uuid
import time
import math
import statistics
import ConfigReaderWriter as CfgRW
from QuickPulse import *
import RPi.GPIO as GPIO


GPIO.setwarnings(False)  # find a better way

infoFilePath = "../ScaleInfoFile.SIF"  # the file directory is still where FlaskMain is and not at this programs file location
#simulateData = CfgRW.cfgVars["simulateData"]
#useCQuickPulse = CfgRW.cfgVars["useCQuickPulse"]
#useMedian = CfgRW.cfgVars["useMedianOfData"]

GPIO.setmode(GPIO.BCM)


class ScaleInfo:
    # scaleInfo is a class used to store the information for each scale.
    # Because of the way Flask works, there is no update function, so, the only way to get new information is to create a new ScaleInfo.
    # This is done each time in the getScale method in FlaskMain
    def __init__(self, num):
        self.Type = "Not Programmed"
        self.Name = "Not Programmed"
        self.UUID = uuid.uuid1()  # this is so each scale have a unique id for the database
        self.MaxCapacity = 0.0
        self.Units = ""
        self.DataPin = 0
        self.ClockPin = 0
        self.EmptyValue = 0
        self.FullValue = 100
        self.Num = num

        if num <= GetNumOfScales():
            self.__GetDataForScale()


    def startGPIO(self):
        if CfgRW.cfgVars["simulateData"].upper() != "TRUE":
            GPIO.setup(self.ClockPin, GPIO.OUT)
            GPIO.setup(self.DataPin, GPIO.IN)

            GPIO.output(self.ClockPin, GPIO.HIGH) # go to sleep
            time.sleep(0.00007)
            #GPIO.output(self.ClockPin, GPIO.LOW)


    def __GetDataForScale(self):
        # This private method is used to get all of the information for a programmed scale.
        # The information for each programmed scale is stored in the file scaleInfoFile.
        try:
            scaleInfoFile = open(infoFilePath, "r")
        except:
            scaleInfoFile = CreateNewInfoFile(infoFilePath)

        line = scaleInfoFile.readline()
        while line != "Scale " + str(self.Num) + "\n":
            line = scaleInfoFile.readline()

        line = scaleInfoFile.readline()
        self.Type = line.split(":")[1].strip()
        line = scaleInfoFile.readline()
        self.Name = line.split(":")[1].strip()
        line = scaleInfoFile.readline()
        self.UUID = line.split(":")[1].strip()
        line = scaleInfoFile.readline()
        self.MaxCapacity = float(line.split(":")[1].strip())
        line = scaleInfoFile.readline()
        self.Units = line.split(":")[1].strip()
        line = scaleInfoFile.readline()
        self.DataPin = int(line.split(":")[1].strip())
        line = scaleInfoFile.readline()
        self.ClockPin = int(line.split(":")[1].strip())
        line = scaleInfoFile.readline()
        self.EmptyValue = float(line.split(":")[1].strip())
        line = scaleInfoFile.readline()
        self.FullValue = float(line.split(":")[1].strip())

        scaleInfoFile.close()


    def GetLowerRange(self):
        self.EmptyValue = self.__ReadFromPin()
        return self.EmptyValue


    def GetUpperRange(self):
        self.FullValue = self.__ReadFromPin()
        return self.FullValue


    def SetRange(self, emptyValue, fullValue):
        self.EmptyValue = emptyValue
        self.FullValue = fullValue

        fr = open(infoFilePath, "r")
        data = fr.readlines()
        fr.close()

        fw = open(infoFilePath, "w")

        i = 0;
        while data[i] != "Scale " + str(self.Num) + "\n":
            line = data[i]
            fw.write(data[i])
            i += 1

        for i in range(i, i + 8):
            line = data[i]
            fw.write(line)
        i += 1

        fw.write("Empty Value:" + str(emptyValue) + "\n")
        fw.write("Full Value:" + str(fullValue) + "\n")
        i += 2

        for i in range(i, len(data)):
            line = data[i]
            fw.write(line)

        fw.close()


    def GetValue(self):
        if self.Name != "Not Programmed":
            m = 100.0/(self.FullValue - self. EmptyValue)
            b = -1.0 * m * self.EmptyValue
            v = self.__ReadFromPin() * m + b

            if v < -100 or v > 200:  # sometimes the HX711 fails and returns a bad value
                time.sleep(0.1)
                v = self.__ReadFromPin() * m + b

            if v > 100.0: v = 100.0
            if v < 0.0: v = 0.0

            return v/100.0
        else:
            return -1

    def __ReadFromPin(self):
        if CfgRW.cfgVars["simulateData"].upper() == "TRUE":
            return (math.sin(3 * math.pi * (time.time() - 1516000000) / 88000 + self.Num) * (50 / 2) +
                    math.sin(2 * math.pi * (time.time() - 1516000000) / 88000 + self.Num) * (50 / 2) + 50)
        else:
            GPIO.output(self.ClockPin, GPIO.LOW)  # power on
            #time.sleep(0.000001)

            repeats = 10
            totalVals = list()
            for repeat in range(repeats):
                dataBits = [0,0,0]

                while GPIO.input(self.DataPin) != 0:
                    pass

                for j in range(2, -1, -1):
                    for i in range(7, -1, -1):
                        if CfgRW.cfgVars["useCQuickPulse"].upper() == "TRUE":
                            dataBits[j] = bitWrite(dataBits[j], i, DoQuickPulse(self.ClockPin, self.DataPin))
                        else:
                            GPIO.output(self.ClockPin, GPIO.HIGH)
                            GPIO.output(self.ClockPin, GPIO.LOW)
                            dataBits[j] = bitWrite(dataBits[j], i, GPIO.input(self.DataPin))

                if CfgRW.cfgVars["useCQuickPulse"].upper() == "TRUE":
                    DoQuickPulse(self.ClockPin, self.DataPin)
                else:
                    GPIO.output(self.ClockPin, GPIO.HIGH)
                    GPIO.output(self.ClockPin, GPIO.LOW)

                val = (dataBits[2] << 16 | dataBits[1] << 8) | dataBits[0]

                if dataBits[2] & 128:
                    val = val - (1 << 24)

                totalVals.append(val)

                time.sleep(0.00001)

            GPIO.output(self.ClockPin, GPIO.HIGH)  # power off
            time.sleep(0.00007)

            if CfgRW.cfgVars["useMedianOfData"].upper() == "TRUE":
                return statistics.median(totalVals)
            else:
                return statistics.mean(totalVals)


    def Delete(self):
        numScales = GetNumOfScales()

        fr = open(infoFilePath, "r")
        data = fr.readlines()
        fr.close()

        fw = open(infoFilePath, "w")
        fw.write("Total Scales:" + str(numScales - 1) + "\n\n")

        line = 0
        offset = 1
        for i in range(0, numScales):
            if i + 1 == self.Num:
                offset -= 1
                continue
            while data[line] != "Scale " + str(i + 1) + "\n":
                line += 1
            line += 1
            fw.write("Scale " + str(i + offset) + "\n")
            fw.writelines(data[line:line + 9])
            fw.write("\n")

        fw.close()


def GetNumOfScales():
    # In the file, the first line is always the line that shows how many scales are programmed in the file.
    try:
        scaleInfoFile = open(infoFilePath, "r")
    except:
        scaleInfoFile = CreateNewInfoFile(infoFilePath)

    fl = scaleInfoFile.readline()
    scaleInfoFile.close()

    if fl.split(":")[0] == "Total Scales":
        return int((fl.split(":")[1]).strip())
    else:
        return 0


def AddScaleInfoToFile(type, name, max, units, dataPin, clockPin):
    numScales = GetNumOfScales()

    try:
        int(dataPin)
        int(clockPin)
        float(max)
    except:
        return numScales

    fr = open(infoFilePath, "r")
    data = fr.readlines()
    fr.close()

    fw = open(infoFilePath, "w")
    fw.write("Total Scales:" + str(numScales + 1) + "\n\n")

    line = 0
    for i in range(0, numScales):
        while data[line] != "Scale " + str(i + 1) + "\n":
            line += 1
        fw.writelines(data[line:line+10])
        fw.write("\n")

    fw.write("Scale " + str(numScales + 1) + "\n")
    fw.write("Type:" + type + "\n")
    fw.write("Name:" + name + "\n")
    fw.write("UUID:" + str(uuid.uuid1()) + "\n")
    fw.write("Max Capacity:" + max + "\n")
    fw.write("Units:" + units + "\n")
    fw.write("Data Pin:" + dataPin + "\n")
    fw.write("Clock Pin:" + clockPin + "\n")
    fw.write("Empty Value:" + "0.0" + "\n")
    fw.write("Full Value:" + "100.0" + "\n")

    fw.close()

    return (numScales + 1)


def GetListOfScaleInfos():
    scaleInfoList = list()

    for i in range(GetNumOfScales()):
        ki = ScaleInfo(i + 1)
        ki.startGPIO()
        scaleInfoList.append(ki)

    return scaleInfoList


def CreateNewInfoFile(filePath):
    # Create a new InfoFile with no scales programmed into it
    # The reason that this file is reopened after it is created is because we only want to return the readonly mode of the file.
    f = open(filePath, "w+")
    f.write("Total scales:0")
    f.close()
    return open(filePath, "r")


def bitWrite(x, n, b):
    if n <= 7 and n >= 0:
        if b == 1:
            x |= (1 << n)
        else:
            x &= ~(1 << n)
    return x
