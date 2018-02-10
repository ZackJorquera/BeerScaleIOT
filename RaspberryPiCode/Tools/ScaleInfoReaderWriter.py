import uuid
import time
import math


simulateData = True
infoFilePath = "../ScaleInfoFile" # the file directory is still where FlaskMain is and not at this programs file location

class ScaleInfo:
    # scaleInfo is a class used to store the information for each scale.
    # Because of the way Flask works, there is no update function, so, the only way to get new information is to create a new ScaleInfo.
    # This is done each time in the getScale method in FlaskMain
    def __init__(self, num):
        self.Type = "Not Programmed"
        self.Name = "Not Programmed"
        self.UUID = uuid.uuid1() # this is so each scale have a unique id for the database
        self.MaxCapacity = 0.0
        self.Units = ""
        self.DataPin = 0
        self.ClockPin = 0
        self.Num = num

        if num <= GetNumOfScales():
            self.__GetDataForScale()


    def __GetDataForScale(self):
        # This private method is used to get all of the information for a programmed scale.
        # The information for each programmed scale is stored in the file scaleInfoFile.
        try:
            scaleInfoFile = open(infoFilePath, "r")
        except:
            scaleInfoFile = self.__CreateNewInfoFile(infoFilePath)

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

        scaleInfoFile.close()


    def GetValue(self):
        if self.Name != "Not Programmed":
            pv = self.__ReadFromPin(self.DataPin, self.ClockPin)
            v = pv/100.0
        else:
            v = -1
        return v

    def __ReadFromPin(self, dataPin, clockPin):
        if simulateData:
            return (math.sin(3 * math.pi * (time.time() - 1516000000) / 88000 + self.Num) * (50 / 2) +
                    math.sin(2 * math.pi * (time.time() - 1516000000) / 88000 + self.Num) * (50 / 2) + 50)
        else:
            return 43.24 #will read from the pins using GPIO


    def __CreateNewInfoFile(self, filePath):
        # Create a new InfoFile with no scales programmed into it
        # The reason that this file is reopened after it is created is because we only want to return the readonly mode of the file.
        f = open(filePath, "w+")
        f.write("Total scales:0")
        f.close()
        return open(filePath, "r")


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
            fw.writelines(data[line:line + 7])
            fw.write("\n")

        fw.close()


def GetNumOfScales():
    # In the file, the first line is always the line that shows how many scales are programmed in the file.
    try:
        scaleInfoFile = open(infoFilePath, "r")
    except:
        return 0

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
        fw.writelines(data[line:line+8])
        fw.write("\n")

    fw.write("Scale " + str(numScales + 1) + "\n")
    fw.write("Type:" + type + "\n")
    fw.write("Name:" + name + "\n")
    fw.write("UUID:" + str(uuid.uuid1()) + "\n")
    fw.write("Max Capacity:" + max + "\n")
    fw.write("Units:" + units + "\n")
    fw.write("Data Pin:" + dataPin + "\n")
    fw.write("Clock Pin:" + clockPin + "\n")

    fw.close()

    return (numScales + 1)


def GetListOfScaleInfos():
    scaleInfoList = list()

    for i in range(GetNumOfScales()):
        scaleInfoList.append(ScaleInfo(i + 1))

    return scaleInfoList
