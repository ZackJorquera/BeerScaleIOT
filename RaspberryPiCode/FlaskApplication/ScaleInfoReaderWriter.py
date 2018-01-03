#import RPi.GPIO as GPIO

infoFilePath = "ScaleInfoFile"

class ScaleInfo:
    # scaleInfo is a class used to store the information for each scale.
    # Because of the way Flask works, there is no update function, so, the only way to get new information is to create a new ScaleInfo.
    # This is done each time in the getScale method in FlaskMain
    def __init__(self, num):
        self.Type = "Not Programmed"
        self.Name = "Not Programmed"
        self.MaxCapacity = 0.0
        self.Units = ""
        self.Value = 0.0

        if num <= GetNumOfScales():
            self.__GetDataForScale(num)


    def __GetDataForScale(self, scaleNum):
        # This private method is used to get all of the information for a programmed scale.
        # The information for each programmed scale is stored in the file scaleInfoFile.
        try:
            scaleInfoFile = open(infoFilePath, "r")
        except:
            scaleInfoFile = self.__CreateNewInfoFile(infoFilePath)

        line = scaleInfoFile.readline()
        while line != "Scale " + str(scaleNum) + "\n":
            line = scaleInfoFile.readline()

        line = scaleInfoFile.readline()
        self.Type = line.split(":")[1].strip()
        line = scaleInfoFile.readline()
        self.Name = line.split(":")[1].strip()
        line = scaleInfoFile.readline()
        self.MaxCapacity = line.split(":")[1].strip()
        line = scaleInfoFile.readline()
        self.Units = line.split(":")[1].strip()
        line = scaleInfoFile.readline()
        dataPin = int(line.split(":")[1].strip())
        line = scaleInfoFile.readline()
        clockPin = int(line.split(":")[1].strip())

        self.__ReadFromPin(dataPin, clockPin)

        scaleInfoFile.close()


    def __ReadFromPin(self, dataPin, clockPin):
        self.Value = 43.24 #will read from the pins using GPIO


    def __CreateNewInfoFile(self, filePath):
        # Create a new InfoFile with not scales programmed in it
        # The reason that this file is reopened after it is created is because we only to return the readonly mode of the file.
        f = open(filePath, "w+")
        f.write("Total scales:0")
        f.close()
        return open(filePath, "r")


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
        fw.writelines(data[line:line+7])
        fw.write("\n")

    fw.write("Scale " + str(numScales + 1) + "\n")
    fw.write("Type:" + type + "\n")
    fw.write("Name:" + name + "\n")
    fw.write("Max Capacity:" + max + "\n")
    fw.write("Units:" + units + "\n")
    fw.write("Data Pin:" + dataPin + "\n")
    fw.write("Clock Pin:" + clockPin + "\n")

    fw.close()

    return (numScales + 1)


def DeleteScaleInfo(num):
    numScales = GetNumOfScales()

    fr = open(infoFilePath, "r")
    data = fr.readlines()
    fr.close()

    fw = open(infoFilePath, "w")
    fw.write("Total Scales:" + str(numScales - 1) + "\n\n")

    line = 0
    offset = 1
    for i in range(0, numScales):
        if i + 1 == num:
            offset -= 1
            continue
        while data[line] != "Scale " + str(i + 1) + "\n":
            line += 1
        line += 1
        fw.write("Scale " + str(i + offset) + "\n")
        fw.writelines(data[line:line + 6])
        fw.write("\n")

    fw.close()
