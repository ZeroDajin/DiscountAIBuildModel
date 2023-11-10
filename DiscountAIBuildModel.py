import pyodbc
import pandas as pd
from datetime import datetime as dt
from dataclasses import dataclass
#Creating Dataclasses
@dataclass
class RawData:
    def __init__(self,UserID,ProductType,DayCreated):
        self.UserID = UserID
        self.ProductType = ProductType
        self.DayCreated = DayCreated
    def __repr__(self):
        return f"{self.UserID},{self.ProductType},{self.DayCreated}"
@dataclass
class OutputData:
    def __init__(self,UserID,ProductType,Day):
        self.UserID = UserID
        self.ProductType = ProductType
        self.Day = Day
    def __repr__(self):
        return f"{self.UserID},{self.ProductType},{self.Day}"
    def to_dict(self):
        return {'UserID':self.UserID,'ProductType':self.ProductType,'Approximate Day':self.Day}
    
TheDBConnection= pyodbc.connect(connectionstring)
ReadDataResult = pd.read_sql("Select ApplicationUsers_Id as UserID, tb_ProductCategories.Tiltle as ProductType, tb_Order.CreatedDate as DayBuy FROM tb_OrderDetail LEFT JOIN tb_Product ON tb_OrderDetail.ProductId=tb_Product.Id RIGHT JOIN tb_Order ON tb_Order.Id=tb_OrderDetail.OrderId INNER JOIN tb_ProductCategories ON tb_ProductCategories.Id=tb_Product.ProductCategoryId",TheDBConnection)
#FULL QUERY:
#Select ApplicationUsers_Id as UserID,
#		tb_ProductCategories.Tiltle as ProductType,
#		tb_Order.CreatedDate as DayBuy
#FROM tb_OrderDetail
#LEFT JOIN tb_Product ON tb_OrderDetail.ProductId=tb_Product.Id
#RIGHT JOIN tb_Order ON tb_Order.Id=tb_OrderDetail.OrderId
#INNER JOIN tb_ProductCategories ON tb_ProductCategories.Id=tb_Product.ProductCategoryId
#why the hell do we have 3 productcategoryid in product table ?
df=pd.DataFrame(ReadDataResult)
#Functions:
def ApproximateTimeCalculation(ListOfData): #this return an OutputData object to be insert into the output list.
                                            #TODO: this is dumb.
    print("Processing Approximate Time...")
    Numerator = 0
    Denominator = len(ListOfData) - 1
    for i in range(len(ListOfData)-1,-1,-1):
        if(i == 0):
            ApproximateTime = Numerator/Denominator
            Output = (OutputData(ListOfData[1].UserID,ListOfData[1].ProductType,ApproximateTime))
            break
        else:
            CalDate = (dt.strptime(str(ListOfData[i].DayCreated),"%Y-%m-%d %H:%M:%S.%f") - dt.strptime(str(ListOfData[i-1].DayCreated),"%Y-%m-%d %H:%M:%S.%f")).days
            Numerator = Numerator + CalDate
    return Output
def CheckingForSimilarObjects(ObjectToBeCompare,ListOfComparableData):
    if(ObjectToBeCompare is None):
        raise Exception("CheckingForSimilarObjects: Invalid data input")
    elif(ListOfComparableData == []):
        return False
    else:
        for Variable in ListOfComparableData:
            if(ObjectToBeCompare.UserID==Variable.UserID and ObjectToBeCompare.ProductType == Variable.ProductType):
                return True
            else:
                return False
def RemoveOnlyOneInstanceOfUserOrder(ListOfComparableData): 
    #This will try to find only one existing UserID||ProductType 
    #and remove them from ListRawData. This need to be fix....
    if(ListOfComparableData!=[]):
        ListOutputData = ListOfComparableData
        for Variable in ListOfComparableData:
            countobject = 0
            for Object in ListOutputData:
                if(Variable is not Object):
                    if(Variable.UserID == Object.UserID and Variable.ProductType == Object.ProductType):
                        countobject = countobject + 1
            if(countobject == 0):
                ListOutputData.remove(Variable)
        return ListOutputData
    else:
        raise Exception("RemoveOnlyOneInstanceOfUserOrder: Invalid data input")
        
#Initializing Datas....
ListRawData = []
#Input dataset
for index,row in df.iterrows():
    ListRawData.append(RawData(*row))
#initializing Lists to Calculate...
ListRawData = RemoveOnlyOneInstanceOfUserOrder(ListRawData)
ListProcessingData = []
ListOutputData = []
#Main program
while ListRawData != []:
    for object in ListRawData:
        if(ListOutputData == [] or ListProcessingData == []):
            ListProcessingData.append(RawData(object.UserID,object.ProductType,object.DayCreated))
            ListRawData.remove(object)
        elif(ListProcessingData!=[] and 
             CheckingForSimilarObjects(object,ListProcessingData) and 
             CheckingForSimilarObjects(object,ListOutputData)==False):
            ListProcessingData.append(RawData(object.UserID,object.ProductType,object.DayCreated))
            ListRawData.remove(object)
    if(len(ListProcessingData)>1):
        ListOutputData.append(ApproximateTimeCalculation(ListProcessingData))
        ListProcessingData.clear()
print(ListOutputData)
dfout = pd.DataFrame([x.to_dict() for x in ListOutputData])
dfout = dfout.set_index('UserID')
dfout.to_excel("DiscountModel.xlsx",sheet_name='FinalModel') #final result