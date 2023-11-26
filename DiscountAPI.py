import numpy as np
import pandas as pd
import pickle
from flask import Flask,jsonify
from flask import request
from typing import List, Union
from datetime import datetime as dt
import json
#Functions
def LoadingTrainedMatrix():    
    #Loading TrainedModel...
    with open('TrainedModel.pkl','rb') as file:
        ItemSimilarityMatrix = pickle.load(file)
    return ItemSimilarityMatrix
def LoadingProductsList():
    #Loading Products
    ProductsList = pd.read_csv("CSVFiles\ProductsList.csv")
    return ProductsList
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
def ReturnByCategory(Similarproductids,UserInput,ProductsList):
    UserProductID = UserInput[0][0]
    Similarproductbycategory = []
    Userinputcategory = ProductsList.loc[ProductsList['ProductID']==UserProductID,'Category'].values[0]
    for ProductID in Similarproductids:
        Similarproduct = ProductsList.loc[(ProductsList['ProductID']==ProductID)&(ProductsList['Category']== Userinputcategory)]
        if not Similarproduct.empty:
            Similarproductbycategory.append(ProductID)
    return Similarproductbycategory[0]
#Change return value from proudct ids to product titles
def ReturnToTitles(Similarproductids,ProductsList):
    Similar_product_titles = ProductsList.loc[ProductsList['ProductID'].isin(Similarproductids), 'Title'].tolist()
    return Similar_product_titles
#Starting app
app = Flask(__name__)
@app.route('/GetDiscountVouchers',methods=['POST'])
def GetPredictions():
    UserInput = request.json
    UserInput = [(UserInput[0][0],UserInput[0][1])]
    if UserInput is None:
        return jsonify({"error": "Invalid UserInput format"}), 400
    else:
        ProductID = ReturnByCategory(PredictSimilarItems(UserInput,LoadingTrainedMatrix(),LoadingProductsList(),10),UserInput,LoadingProductsList())
        return jsonify({"ProductID": ProductID})
if __name__ == '__main__':
    app.run(debug=True)