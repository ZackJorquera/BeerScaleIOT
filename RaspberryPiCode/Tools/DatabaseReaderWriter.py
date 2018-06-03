from pymongo import MongoClient, IndexModel, DESCENDING
from abc import abstractmethod
import time
import ConfigReaderWriter as CfgRW


class DBProfileBase:
    def __init__(self):
        self.HostServer = CfgRW.cfgVars["dbHostServer"]
        self.HostPort = int(CfgRW.cfgVars["dbHostPort"], 10)
        self.DBName = CfgRW.cfgVars["dbName"]
        self.CollectionName = CfgRW.cfgVars["dbCollectionName"]
        self.Client = None
        self.DB = None
        self.Collection = None
        self.Connected = False;

    @abstractmethod
    def Connect(self):
        pass

    @abstractmethod
    def Reconnect(self):
        pass

    @abstractmethod
    def Write (self, scaleInfo, value):
        pass

    @abstractmethod
    def DropDB (self):
        pass

    @abstractmethod
    def GetTimeFrameFor (self, scaleInfo, timeSpanHours):
        pass


class DataSampleBase():
    def __init__(self, scaleID, value):
        self.id = scaleID
        self.Value = value
        self.TimeStamp = time.time()


class MongoDBProfile(DBProfileBase):
    class MongoDataSample(DataSampleBase):
        def asBSON(self):
            return {"c": self.id, "v": self.Value, "t": self.TimeStamp}

    def Connect(self):
        try:
            self.Client = MongoClient(self.HostServer, self.HostPort)
            self.DB = self.Client[self.DBName]
            self.Collection = self.DB[self.CollectionName]
            index = IndexModel([("t", DESCENDING)]) # This makes the data pre-sorted so when you all find it returns sorted data by descending "t" values
            self.Collection.create_indexes([index])
            self.Connected = True
        except:
            self.Client = None
            self.DB = None
            self.Collection = None
            self.Connected = False
        return self.Connected

    def Reconnect(self):
        if self.Connected != True:
            self.Connected = self.Connect()

    def Write(self, scaleInfo, value):
        dataSample = self.MongoDataSample(scaleInfo.UUID, value)
        result = self.Collection.insert_one(dataSample.asBSON())
        return result

    def DropDB(self):
        self.Client.drop_database(self.DBName)
        return

    def GetTimeFrameFor(self, scaleInfo, timeSpanHours):
        scaleUUID = scaleInfo.UUID

        endTime = time.time()
        startTime = endTime - (timeSpanHours * 60 * 60)

        cursor = self.Collection.find({"t":{"$gte": startTime, "$lte": endTime},"c":scaleUUID}) # Finds all documents with values of 't' less than endTime and greater
                                                                                                # than startTime and having the value of "c" equal to scaleInfo.UUID
        timeStampList = list()
        valueList = list()

        for item in cursor:
            timeStampList.append(-1 * (item['t'] - time.time()))
            valueList.append(item['v'])

        timeFrameData = {'valueList': valueList, 'timeStampList': timeStampList}
        return timeFrameData