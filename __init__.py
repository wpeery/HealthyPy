import math
import json
import requests
import os
from pprint import pprint

class NutrientLib1:
    """Can act as a day or week to store nutrients consumed"""

    def __init__(self):
        self.gov_api_key = "XXXXXXXXX" # your api key goes here
        self.nutrientDictionary = {} # name:quantity
        self.unitDictionary = {} # name of nutrient : unit
        self.jsonDictionary = {} # foodID : json of page
        self.exclusionList = ["Water"] # list of nutrients to be excluded

    def getStoredFood(self,foodID):          ### Returns foodSearch if stored or False if not
        if foodID in self.jsonDictionary: 
            foodSearch = self.jsonDictionary[foodID]
            return foodSearch
        return False

    def requestByID(self,foodID):
        url = "http://api.nal.usda.gov/ndb/reports/?ndbno=" + foodID + "&type=f&format=json&api_key=" + self.gov_api_key
        response = requests.get(url)
        foodSearch = response.json()
        self.jsonDictionary[foodID] = foodSearch            # add food to jsonDictionary (memory)
        return foodSearch
    
    def addNutrients(self,foodSearch,amount):            ## (private)
        # iterates through request 
        # gets each nutrient 
        # multiplys it by the amount
        # checks nutrientaDictionary if its already in there increment the amount 
        # if not: adds name and quantity to nutrientDictionary
        if(str(foodSearch) == foodSearch):
            foodSearch = json.loads(foodSearch)
        for nutrient in foodSearch["report"]["food"]["nutrients"]:
            if nutrient["name"] not in self.exclusionList:
                if nutrient["name"] not in self.unitDictionary:          # if not in unitDicitonary; update
                    self.unitDictionary[nutrient["name"]] = nutrient["unit"]
                if nutrient["name"] not in self.nutrientDictionary:      # if not in nutrientDictionary; update
                    self.nutrientDictionary[nutrient["name"]] = 0
                rawAmount = nutrient["value"]                       # value is given per 100 grams of food
                rawAmount = rawAmount/100                           # adjust amount by dividing by 100
                rawAmount = float(rawAmount)
                amount = float(amount)
                adjustedAmount = rawAmount*amount
                self.nutrientDictionary[nutrient["name"]] += adjustedAmount        # add amount to nutrient Dictionary

    def printNutrients(self):                                           # prints nutrients and amounts and units
        for nutrient in self.nutrientDictionary:
            print('{:_<50}'.format(nutrient),self.nutrientDictionary[nutrient],self.unitDictionary[nutrient])

    def printExclusions(self):                                          # prints nutrients exclude
        for food in self.exclusionList:
            print(food)
    
    def excludeNutrient(self,nutrient):                                  # adds nutrient to exclusionList
        if nutrient not in self.exclusionList:
            self.exclusionList.append(nutrient)

    def includeNutrient(self,nutrient):                                  # removes nutrient from exclusionList
        if nutrient in self.exclusionList:
            self.exclusionList.remove(nutrient)

import time

class TokenBucket1:
    """limits requests"""
    def __init__(self,tokens,coolDown):
        self.numTokens = float(tokens)              # max number of tokens
        self.tokens = float(tokens)                 # number of tokens available
        self.coolDown = float(coolDown)
        self.timeStamp = time.time()

    def removeTokens(self,tokens):                  # removes a given amount of tokens
        if (tokens <= self.tokens):
            self.tokens = self.tokens - tokens
            return True
        else:
            return False

    def refreshTokens(self):                            # refreshes tokens if an hour has passed
        currentTime = time.time()
        if((currentTime - self.timeStamp) > self.coolDown()):
            self.tokens = self.numTokens
            self.timeStamp = time.time()
            return True
        else:
            timeLeft = (time.time() - self.timeStamp)
            print(timeLeft)
            return False


class IDSearch1:
    """Search for an ID of a food and store previous searches"""

    def __init__(self):
        self.gov_api_key = "9ZH2gqcl0QxJfd7aqlhaeIdckvl0ha3qFWnHtVUH"
        self.tmpFoodDictionary = {} # offset : ndbno (FoodID)
        self.foodHistory = {} # foodsearched : ndbno (contains a history of foods consumed)
  
    def searchByName(self,foodName):
        url = "http://api.nal.usda.gov/ndb/search/?format=json&q=" + foodName + "&sort=r&max=25&offset=0&api_key=" + self.gov_api_key
        response = requests.get(url)
        foodSearch = response.json()
        if "errors" in foodSearch:                      # if the food returns zero results 
            print(foodSearch["errors"]["error"][0]["message"])
            return -1
        print()                                                                 # print line for Format
        for food in foodSearch["list"]["item"]:                                 # iterates through API Dictionary containg foods
            print('{:_<50}'.format(food["name"]), "Key: " + str(food["offset"])) #prints: "food      Key: number in list"  ####TODO: edit this so it lines up
            print()
            self.tmpFoodDictionary[food["offset"]] = food["ndbno"]
        offset_number = input("Enter the key of the desired food: ")
        offset_number = int (offset_number)
        self.foodHistory[foodName] = self.tmpFoodDictionary[offset_number] # adds to foodHistory
        foodID = self.tmpFoodDictionary[offset_number]
        self.tmpFoodDictionary.clear()
        return foodID
    
    def storedFoodID(self,foodName):                    # returns foodID if it is stored in foodHistory or -1 if it isnt                   
        if (foodName in self.foodHistory):
            foodID = self.foodHistory[foodName]
            return foodID
        return -1
       

    def printFoodHistory(self):
        for food in self.foodHistory:
            print(food)

Searcher = IDSearch1()
Library = NutrientLib1()
Bucket = TokenBucket1(950,3600)
import sqlite3

def getFoodID(foodName):                           ## uses TokenBucket and IDSearch
    foodID = Searcher.storedFoodID(foodName)
    if(foodID != -1):
        return foodID
    if(not Bucket.removeTokens(1)):
        if(Bucket.refreshTokens()):
            Bucket.removeTokens(1)
        else:
            return -1
    foodID = Searcher.searchByName(foodName)
    return foodID
    

def addFood(foodName,amount):                              ## uses TokenBucket and IDSearch
    foodID = getFoodID(foodName)
    if(foodID == -1):
        return False
    foodSearch = Library.getStoredFood(foodID)             
    if (foodSearch == False):
        if(not Bucket.removeTokens(1)):
            if(Bucket.refreshTokens()):
                Bucket.removeTokens(1)
            else:
                return False
        foodSearch = Library.requestByID(foodID)
    Library.addNutrients(foodSearch,amount)
    return True
    
    
def getAmount(food):
    number = input("Enter the amount of " + food + " in grams: ")
    return number
    
def getFoodName():
    name = input("enter the name of the food: ")
    return name

def fillLibrary():
    print("type 'exit' when finished")
    name = ""
    amount = ""
    while (True):
        name = getFoodName()
        if( name == "exit"):
            break
        amount = getAmount(name)
        addFood(name,amount)

def save():
    conn = sqlite3.connect('USDAData.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS foods
        (name TEXT,
        foodid TEXT,
        json BLOB);''')
    
    for food in Searcher.foodHistory:
        foodID = (Searcher.foodHistory[food])
        string = json.dumps(Library.jsonDictionary[foodID])
        cur.execute("INSERT INTO foods VALUES (?,?,?)", (food,foodID,string)) 
    
    cur.execute('''CREATE TABLE IF NOT EXISTS NUTRIENTS
        (NAME TEXT,
        AMOUNT REAL,
        UNIT TEXT);''')

    for nutrient in Library.nutrientDictionary:
        cur.execute("INSERT INTO NUTRIENTS VALUES (?,?,?)",(nutrient,Library.nutrientDictionary[nutrient],Library.unitDictionary[nutrient]))

    cur.execute('''CREATE TABLE IF NOT EXISTS ATTRIBUTES
        (EXCLIST BLOB,
        COOLDOWN REAL,
        NUMTOKENS INTEGER,
        TIMESTAMP REAL,
        TOKENS INTEGER);''')
    string = str(Library.exclusionList)
    cur.execute("INSERT INTO ATTRIBUTES VALUES (?,?,?,?,?)", (string, Bucket.coolDown, Bucket.numTokens, Bucket.timeStamp, Bucket.tokens))

    conn.commit()
    conn.close()

def load():
    if(os.path.isfile('USDAData.db')):
        conn = sqlite3.connect('USDAData.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM FOODS')
        for row in cur:
            Searcher.foodHistory[row[0]] = row[1]  # 0:Name 1:FoodID 2:Json
            Library.jsonDictionary[row[1]] = row[2]
        
        cur.execute('SELECT * FROM NUTRIENTS')
        for row in cur:
            Library.nutrientDictionary[row[0]] = row[1] # 0 name, 2 amount, 3 unit
            Library.unitDictionary[row[0]] = row[2]
            
        cur.execute('SELECT * FROM ATTRIBUTES')
        row = cur.fetchone()
        Library.exclusionList = row[0]
        Bucket.coolDown = row[1]
        Bucket.numTokens = row[2]
        Bucket.timeStamp = row[3]
        Bucket.tokens = row[4]
        conn.commit()
        conn.close()

def RESET():
    conn = sqlite3.connect('USDAData.db')
    cur = conn.cursor()
    cur.execute('DROP TABLE NUTRIENTS')
    cur.execute('DROP TABLE FOODS')
    cur.execute('DROP TABLE ATTRIBUTES')
    conn.commit()
    conn.close()
         

    

def Main():
    answer = input('Do you want to load?: ')
    if (answer == 'yes'):
        load()
    fillLibrary()
    print("printing food History")
    Searcher.printFoodHistory()
    print("printing Nutrients") 
    Library.printNutrients()
    print("printing raw")
    sear = Searcher.__dict__
    buk = Bucket.__dict__
    print("SEARCHER")
    pprint(sear)
    print('BUCKET')
    pprint(buk)
    print('exclusion list')
    print(Library.exclusionList)
    answer = input('Do you want to save?: ')
    if (answer == 'yes'): 
        save()
    answer = input('RESET?(Drop all Tables): ')
    if (answer == 'yes'):
        RESET()
    
    ##TODO
        # WRITE COMMENTS
        # SORT DICTIONARIES AND LISTS
        # PUT A SPACE IN BETWEEN EACH NUTRIENT WHEN LISTING
        # ASK THE USER IF THEY WANT TO PRINT ANYTHING
        # FUNCTION TO CLEAR TABLES
        # LOOK INTO THE PROBLEM WITH AUTOMATICALLY ASSIGNING A FOODSEARCH TO A FOODID
        # IMPLEMENT A SEARCH FUNCTION

Main()
