#import pyodbc
#import numpy as np
#import pandas as pd
#from datetime import datetime as dt
#Creating Dataclasses
# @dataclass
# class RawData:
#     def __init__(self,UserID,ProductType,DayCreated):
#         self.UserID = UserID
#         self.ProductType = ProductType
#         self.DayCreated = DayCreated
#     def __repr__(self):
#         return f"{self.UserID},{self.ProductType},{self.DayCreated}"
# @dataclass
# class OutputData:
#     def __init__(self,UserID,ProductType,Day):
#         self.UserID = UserID
#         self.ProductType = ProductType
#         self.Day = Day
#     def __repr__(self):
#         return f"{self.UserID},{self.ProductType},{self.Day}"
#     def to_dict(self):
#         return {'UserID':self.UserID,'ProductType':self.ProductType,'Approximate Day':self.Day}
    
# connectionstring = r'Driver=ODBC Driver 17 for SQL Server;Server=DESKTOP-HJ7PLGE;Database=DICHO;Trusted_Connection=yes;' #connection strings, Driver is important.
# TheDBConnection= pyodbc.connect(connectionstring)
# ReadDataResult = pd.read_sql("Select ApplicationUsers_Id as UserID, tb_ProductCategories.Tiltle as ProductType, tb_Order.CreatedDate as DayBuy FROM tb_OrderDetail LEFT JOIN tb_Product ON tb_OrderDetail.ProductId=tb_Product.Id RIGHT JOIN tb_Order ON tb_Order.Id=tb_OrderDetail.OrderId INNER JOIN tb_ProductCategories ON tb_ProductCategories.Id=tb_Product.ProductCategoryId",TheDBConnection)
# #FULL QUERY:
# #Select ApplicationUsers_Id as UserID,
# #		tb_ProductCategories.Tiltle as ProductType,
# #		tb_Order.CreatedDate as DayBuy
# #FROM tb_OrderDetail
# #LEFT JOIN tb_Product ON tb_OrderDetail.ProductId=tb_Product.Id
# #RIGHT JOIN tb_Order ON tb_Order.Id=tb_OrderDetail.OrderId
# #INNER JOIN tb_ProductCategories ON tb_ProductCategories.Id=tb_Product.ProductCategoryId
# #why the hell do we have 3 productcategoryid in product table ?
# df=pd.DataFrame(ReadDataResult)
# #Functions:
# def ApproximateTimeCalculation(ListOfData): #this return an OutputData object to be insert into the output list.
#                                             #TODO: this is dumb.
#     print("Processing Approximate Time...")
#     Numerator = 0
#     Denominator = len(ListOfData) - 1
#     for i in range(len(ListOfData)-1,-1,-1):
#         if(i == 0):
#             ApproximateTime = Numerator/Denominator
#             Output = (OutputData(ListOfData[1].UserID,ListOfData[1].ProductType,ApproximateTime))
#             break
#         else:
#             CalDate = (dt.strptime(str(ListOfData[i].DayCreated),"%Y-%m-%d %H:%M:%S.%f") - dt.strptime(str(ListOfData[i-1].DayCreated),"%Y-%m-%d %H:%M:%S.%f")).days
#             Numerator = Numerator + CalDate
#     return Output
# def CheckingForSimilarObjects(ObjectToBeCompare,ListOfComparableData):
#     if(ObjectToBeCompare is None):
#         raise Exception("CheckingForSimilarObjects: Invalid data input")
#     elif(ListOfComparableData == []):
#         return False
#     else:
#         for Variable in ListOfComparableData:
#             if(ObjectToBeCompare.UserID==Variable.UserID and ObjectToBeCompare.ProductType == Variable.ProductType):
#                 return True
#             else:
#                 return False
# def RemoveOnlyOneInstanceOfUserOrder(ListOfComparableData): 
#     #This will try to find only one existing UserID||ProductType 
#     #and remove them from ListRawData. This need to be fix....
#     if(ListOfComparableData!=[]):
#         ListOutputData = ListOfComparableData
#         for Variable in ListOfComparableData:
#             countobject = 0
#             for Object in ListOutputData:
#                 if(Variable is not Object):
#                     if(Variable.UserID == Object.UserID and Variable.ProductType == Object.ProductType):
#                         countobject = countobject + 1
#             if(countobject == 0):
#                 ListOutputData.remove(Variable)
#         return ListOutputData
#     else:
#         raise Exception("RemoveOnlyOneInstanceOfUserOrder: Invalid data input")
        
# #Initializing Datas....
# ListRawData = []
# #Input dataset
# for index,row in df.iterrows():
#     ListRawData.append(RawData(*row))
# #initializing Lists to Calculate...
# ListRawData = RemoveOnlyOneInstanceOfUserOrder(ListRawData)
# ListProcessingData = []
# ListOutputData = []
# #Main program
# while ListRawData != []:
#     for object in ListRawData:
#         if(ListOutputData == [] or ListProcessingData == []):
#             ListProcessingData.append(RawData(object.UserID,object.ProductType,object.DayCreated))
#             ListRawData.remove(object)
#         elif(ListProcessingData!=[] and 
#              CheckingForSimilarObjects(object,ListProcessingData) and 
#              CheckingForSimilarObjects(object,ListOutputData)==False):
#             ListProcessingData.append(RawData(object.UserID,object.ProductType,object.DayCreated))
#             ListRawData.remove(object)
#     if(len(ListProcessingData)>1):
#         ListOutputData.append(ApproximateTimeCalculation(ListProcessingData))
#         ListProcessingData.clear()
# print(ListOutputData)
# dfout = pd.DataFrame([x.to_dict() for x in ListOutputData])
# dfout = dfout.set_index('UserID')
# dfout.to_excel("DiscountModel.xlsx",sheet_name='FinalModel') #final result
########################################################################################
#			Training a model using only cosine_similartiy || i rated this 2 out of 10||
#                                          WRONG MAJOR
#           TẤT CẢ LÀ TẠI THẰNG MINH!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#######################################################################################
import pyodbc
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

#Variable name rule:
#Files inputs or Files output = Upperscore all first letter of a character and the name must be nouns
#Variables name(ALL MUST BE NOUNS):
# -Big Variable(Lists, Dataframes, Return of a libary functions, Widespread uses) = scores same as Files name
# -Small Variable(Temporary holders, Small uses, Return of simple types like string, int, 
# floats). = Upperscore the first word only
#Functions naming must be Verb Form and Upperscore all first letters
#Warning: FUNCTIONS INPUT HAVE TO BE NAMED THE SAME AS DEF REQUIREMENTS. 
# EXAMPLE: DEF FOO(index,columns)- calling
# FOO(index, columns) || REMEMBER!

#I want to die....

#Connecting to DB and initializing data
connectionstring = r'Driver=ODBC Driver 17 for SQL Server;Server=DESKTOP-HJ7PLGE;Database=DICHO;Trusted_Connection=yes;' #connection strings, Driver is important.
TheDBConnection= pyodbc.connect(connectionstring)
ReadDataResult = pd.read_sql_query("Select	ApplicationUsers_Id as UserID, tb_OrderDetail.ProductId as ProductID, tb_OrderDetail.Quantity as Amount FROM tb_OrderDetail LEFT JOIN tb_Product ON tb_OrderDetail.ProductId=tb_Product.Id RIGHT JOIN tb_Order ON tb_Order.Id=tb_OrderDetail.OrderId INNER JOIN tb_ProductCategories ON tb_ProductCategories.Id=tb_Product.ProductCategoryId",TheDBConnection)
#########################################Full Query:
# Select	ApplicationUsers_Id as UserID,
# 		tb_OrderDetail.ProductId as ProductID,
# 		tb_OrderDetail.Quantity as Amount
# FROM tb_OrderDetail
# LEFT JOIN tb_Product ON tb_OrderDetail.ProductId=tb_Product.Id
# RIGHT JOIN tb_Order ON tb_Order.Id=tb_OrderDetail.OrderId
# INNER JOIN tb_ProductCategories ON tb_ProductCategories.Id=tb_Product.ProductCategoryId
## //WHERE tb_ProductCategories.Tiltle != N'Gia vị'//Unused part
#######################################
#Formatting the Query results
df = pd.DataFrame(ReadDataResult)
df.to_csv(r'E:\Zero\Study\DoAnChuyenNganh\Python\API\DiscountAIBuildModel\CSVFiles\ReadytoReadModel.csv',index=False)
ReadDataResult = pd.read_sql_query("Select Id as ProductID, Title, ProductCategoryId as Category FROM tb_Product",TheDBConnection)
df = pd.DataFrame(ReadDataResult)
df.to_csv(r'E:\Zero\Study\DoAnChuyenNganh\Python\API\DiscountAIBuildModel\CSVFiles\ProductsList.csv',index=False)
#Inputs
PurchaseHistory = pd.read_csv("E:\Zero\Study\DoAnChuyenNganh\Python\API\DiscountAIBuildModel\CSVFiles\ReadytoReadModel.csv")
ProductsList = pd.read_csv("E:\Zero\Study\DoAnChuyenNganh\Python\API\DiscountAIBuildModel\CSVFiles\ProductsList.csv")
PurchaseHistory = pd.DataFrame(PurchaseHistory) #initializing dataframes.
ProductsList = pd.DataFrame(ProductsList)
FullPurchaseHistory = PurchaseHistory
#Categorize the Unique IDs || Warning: DO NOT USE THIS TABLE TO COMPARE ANYTHING!!
FullPurchaseHistory['UserID'] = PurchaseHistory['UserID'].astype('category').cat.codes
FullPurchaseHistory['ProductID'] = PurchaseHistory['ProductID'].astype('category').cat.codes
#Pivoting the table
User_ItemMatrix = FullPurchaseHistory.pivot_table(index='UserID', columns='ProductID', values='Amount', fill_value=0)
#Cosine similarity
ItemSimilarityMatrix = cosine_similarity(User_ItemMatrix.T)
#Save the trained model
with open('TrainedModel.pkl','wb') as file:
    pickle.dump(ItemSimilarityMatrix,file)
#Done for initializing TrainedModel