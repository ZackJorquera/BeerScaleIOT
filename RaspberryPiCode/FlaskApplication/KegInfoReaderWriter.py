#import RPi.GPIO as GPIO


class KegInfo:
    def __init__(self, num):
        self.Type = "Not Programmed"
        self.Name = "Not Programmed"
        self.MaxCapacity = 0.0
        self.Units = ""
        self.Value = 0.0

        if num <= GetNumOfScales():
            self.GetDataForScale(num)


    def GetDataForScale(self, kegNum):
        kegInfoFile = open("KegInfoFile", "r")

        line = kegInfoFile.readline()
        while line != "Keg " + str(kegNum) + "\n":
            line = kegInfoFile.readline()

        line = kegInfoFile.readline()
        self.Type = line.split(":")[1].strip()
        line = kegInfoFile.readline()
        self.Name = line.split(":")[1].strip()
        line = kegInfoFile.readline()
        self.MaxCapacity = line.split(":")[1].strip()
        line = kegInfoFile.readline()
        self.Units = line.split(":")[1].strip()
        line = kegInfoFile.readline()
        dataPin = int(line.split(":")[1].strip())
        line = kegInfoFile.readline()
        clockPin = int(line.split(":")[1].strip())

        self.ReadFromPin(dataPin, clockPin)

        kegInfoFile.close()
        return self


    def ReadFromPin(self, dataPin, clockPin):
        self.Value = 43.24 #will read from the pins using GPIO


def GetNumOfScales():
    kegInfoFile = open("KegInfoFile", "r")
    fl = kegInfoFile.readline()
    kegInfoFile.close()
    return int((fl.split(":")[1]).strip())