from pymongo import MongoClient, IndexModel, DESCENDING
import time

class MongoDBProfile:

    class MongoDataSample:
        def __init__(self, scaleID, value):
            self.id = scaleID
            self.Value = value
            self.TimeStamp = time.time()


        def asBSON(self):
            return {"c": self.id, "v": self.Value, "t": self.TimeStamp}

    def __init__(self, hostServer='localhost', hostPort=27017, dbName='ScaleLiquidRemainingIOT', collectionName='ScaleData'):
        self.HostServer = hostServer
        self.HostPort = hostPort
        self.DBName = dbName
        self.CollectionName = collectionName

        self.Connected = self.__Connect()


    def __Connect(self):
        try:
            self.Client = MongoClient(self.HostServer, self.HostPort)
            self.DB = self.Client[self.DBName]
            self.Collection = self.DB[self.CollectionName]
            index = IndexModel([("t", DESCENDING)]) # This makes the data pre-sorted so when you all find it returns sorted data by descending "t" values
            self.Collection.create_indexes([index])
            return True
        except:
            self.Client = None
            self.DB = None
            self.Collection = None
            return False


    def Reconnect(self):
        if self.Connected != True:
            self.Connected = self.__Connect()


    def Write(self, scaleInfo, value):
        dataSample = self.MongoDataSample(scaleInfo.UUID, value)
        result = self.Collection.insert_one(dataSample.asBSON())
        return result


    def DropDB(self):
        self.Client.drop_database(self.DBName)
        return


    def GetTimeFrameFor(self, scaleInfo, timeSpanMins):
        scaleUUID = scaleInfo.UUID

        endTime = time.time()
        startTime = endTime - timeSpanMins * 60

        cursor = self.Collection.find({"t":{"$gte": startTime, "$lte": endTime},"c":scaleUUID}) # Finds all documents with values of 't' less than endTime and greater
                                                                                                # than startTime and having the value of "c" equal to scaleInfo.UUID
        timeStampList = list()
        valueList = list()

        for item in cursor:
            timeStampList.append(-1 * (item['t'] - time.time())/60)
            valueList.append(item['v'])

        timeFrameData = {'valueList': valueList, 'timeStampList': timeStampList}
        return timeFrameData