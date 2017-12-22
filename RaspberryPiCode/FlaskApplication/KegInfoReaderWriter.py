#import RPi.GPIO as GPIO


class KegInfo:
    def __init__(self, num):
        self.Type = "Not Programmed"
        self.Name = "Not Programmed"
        self.MaxCapacity = 0.0
        self.Units = ""
        self.Value = 0.0

        if num <= GetNumOfKegs():
            self.GetDataForKeg(num)


    def GetDataForKeg(self, kegNum):
        kegInfoFile = open("KegInfoFile", "r")

        line = kegInfoFile.readline()
        while line != "Keg " + str(kegNum) + "\n":
            line = kegInfoFile.readline()

        line = kegInfoFile.readline()
        self.Type = line.split(":")[1]
        line = kegInfoFile.readline()
        self.Name = line.split(":")[1]
        line = kegInfoFile.readline()
        self.MaxCapacity = line.split(":")[1]
        line = kegInfoFile.readline()
        self.Units = line.split(":")[1]
        line = kegInfoFile.readline()
        dataPin = line.split(":")[1]
        line = kegInfoFile.readline()
        clockPin = line.split(":")[1]

        self.ReadFromPin(dataPin, clockPin)

        kegInfoFile.close()
        return self


    def ReadFromPin(self, dataPin, clockPin):
        self.Value = 43.24 #will read from the pins using GPIO


def GetNumOfKegs():
    kegInfoFile = open("KegInfoFile", "r")
    fl = kegInfoFile.readline()
    kegInfoFile.close()
    return int((fl.split(":")[1]).strip())