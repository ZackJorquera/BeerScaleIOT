import uuid


infoFilePath = "../ScaleInfoFile.SIF"


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

        self.Failed = False

        try:
            if num <= GetNumOfScales():
                self.__GetDataForScale()
            else:
                raise IndexError()
        except:
            self.Failed = True
            self.MaxCapacity = 0.0
            self.DataPin = 0
            self.ClockPin = 0
            self.EmptyValue = 0
            self.FullValue = 100


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


def SetAsInfoFile(text):
    f = open(infoFilePath, "w+")
    f.write(text)
    f.close()
    return open(infoFilePath, "r")
