import uuid
import time
import math
import RPi.GPIO as GPIO


simulateData = True
infoFilePath = "../ScaleInfoFile.SIF" # the file directory is still where FlaskMain is and not at this programs file location
GPIO.setmode(GPIO.BCM)
# GPIO.setwarning(False)


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
        if not simulateData:
            GPIO.setup(self.ClockPin, GPIO.OUT)
            GPIO.setup(self.DataPin, GPIO.IN)

            GPIO.output(self.ClockPin, GPIO.HIGH)
            time.sleep(0.0001)
            GPIO.output(self.ClockPin, GPIO.LOW)


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

        for line in range(len(data)-2):
            fw.write(data[line])

        fw.write("Empty Value:" + str(emptyValue) + "\n")
        fw.write("Full Value:" + str(fullValue) + "\n")

        fw.close()


    def GetValue(self):
        if self.Name != "Not Programmed":
            m = 100.0/(self.FullValue - self. EmptyValue)
            b = -1.0 * m * self.EmptyValue
            v = self.__ReadFromPin() * m + b

            if(v > 100.0): v = 100.0
            if(v < 0.0): v = 0.0

            return v/100.0
        else:
            return -1

    def __ReadFromPin(self):
        if simulateData:
            return (math.sin(3 * math.pi * (time.time() - 1516000000) / 88000 + self.Num) * (50 / 2) +
                    math.sin(2 * math.pi * (time.time() - 1516000000) / 88000 + self.Num) * (50 / 2) + 50)
        else:
            sum = 0
            repeats = 5.0
            for repeat in range(repeats):
                b1 = []
                b2 = []
                b3 = []
                for i in range(8):
                    b1.append(False)
                    b2.append(False)
                    b3.append(False)
                dataBits = [b1,b2,b3]

                while GPIO.input(self.DataPin) != 0:
                    pass

                for j in range(2, -1, -1):
                    for i in range(7, -1, -1):
                        GPIO.output(self.ClockPin, GPIO.HIGH)
                        dataBits[j][i] = GPIO.input(self.DataPin)
                        GPIO.output(self.ClockPin, GPIO.LOW)
                for i in range(1):
                    GPIO.output(self.ClockPin, GPIO.HIGH)
                    GPIO.output(self.ClockPin, GPIO.LOW)

                bits = []
                for j in range(2, -1, -1):
                    bits += dataBits[j]

                val = int(''.join(map(str, bits)), 2)
                sum += val

            return sum / repeats


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
