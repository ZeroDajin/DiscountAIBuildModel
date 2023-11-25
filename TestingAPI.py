import pyodbc
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


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
#Functions
def PredictSimilarItems(UserInput, ItemSimilarityMatrix, ProductsList, Numberofidoutput):
    # Convert new user's purchase history to a user-item vector
    UserInputVector = np.zeros((ItemSimilarityMatrix.shape[0],))
    for Productid, Amount in UserInput:
        if Productid in ProductsList['ProductID'].values:
            index = ProductsList.index[ProductsList['ProductID'] == Productid][0]
            UserInputVector[index] = Amount

    # Calculate similarity of new user's purchases with all items
    UserInputSimilarity = np.dot(ItemSimilarityMatrix, UserInputVector) / (np.linalg.norm(ItemSimilarityMatrix) * np.linalg.norm(UserInputVector))

    #Get the number of most similar indexes
    SimilarItemIndexes = UserInputSimilarity.argsort()[-Numberofidoutput:][::-1]

    # Convert indexes to ProductID
    Similarproductids = ProductsList.loc[SimilarItemIndexes, 'ProductID'].tolist()
    # Remove the same ProductID 
    Similarproductids = [ProductID for ProductID in Similarproductids if ProductID not in [product[0] for product in UserInput]]
    
    return Similarproductids[:Numberofidoutput]
#return only from the same type of category
def ReturnByCategory(Similarproductids,UserInput):
    UserProductID = UserInput[0][0]
    Similarproductbycategory = []
    Userinputcategory = ProductsList.loc[ProductsList['ProductID']==UserProductID,'Category'].values[0]
    for ProductID in Similarproductids:
        Similarproduct = ProductsList.loc[(ProductsList['ProductID']==ProductID)&(ProductsList['Category']== Userinputcategory)]
        if not Similarproduct.empty:
            Similarproductbycategory.append(ProductID)
    return Similarproductbycategory
#Change return value from proudct ids to product titles
def ReturnToTitles(Similarproductids):
    Similar_product_titles = ProductsList.loc[ProductsList['ProductID'].isin(Similarproductids), 'Title'].tolist()
    return Similar_product_titles

#Cosine similarity
ItemSimilarityMatrix = cosine_similarity(User_ItemMatrix.T)
#Open a trained model
#Testing
UserInput = [(1002, 4)]
print(UserInput)
Numberofidoutput = 5
Similar_items = PredictSimilarItems(UserInput, ItemSimilarityMatrix, ProductsList, Numberofidoutput)
print("Similar item ids for the new user:", Similar_items)
########### WARNING!! THIS FUNCTION ONLY RETURN BASED ON USERINPUT HAVE ONLY ONE CATEGORY, 
# DONT TRY MORE THAN TWO DIFFERENT CATEGORY!!
###################
print("Similar item Titles for the new user:", ReturnToTitles(Similar_items))
print("Similar items with similar category:", ReturnByCategory(Similar_items,UserInput))
