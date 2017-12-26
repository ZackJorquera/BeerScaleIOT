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