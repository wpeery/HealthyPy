import json
import os
import pprint
import sqlite3

import FoodLibrary
import NutrientLibrary
import Searcher
import TokenBucket


class HealthyPy:
    """Descriprion goes here"""

    def __init__(self):
        self.searcher = Searcher.Searcher()
        self.foodLibrary = FoodLibrary.FoodLibrary()
        self.nutrientLibrary = NutrientLibrary.NutrientLibrary()
        self.bucket = TokenBucket.TokenBucket(950, 3600)

    def consumeTokens(self, numTokens):
        if (self.bucket.areTokensLeft(numTokens)):
            self.bucket.removeTokens(numTokens)
            return True
        elif(self.bucket.refreshTokens()):
            self.bucket.removeTokens(numTokens)
            return True
        return False

    def searchByName(self, foodName):
        if self.consumeTokens(1):
            foodSearch = self.searcher.requestByName(foodName)
            print(foodSearch)
            return foodSearch
        else:
            return -1

    def searchByID(self, foodID):
        if self.consumeTokens(1):
            foodSearch = self.searcher.requestByID(foodID)
            return foodSearch
        else:
            return -1

    def getFoodID(self, foodName):
        if (self.foodLibrary.isNameStored(foodName)):
            return self.foodLibrary.getFoodID(foodName)
        foodSearch = self.searchByName(foodName)
        if "errors" in foodSearch:  # if the food returns zero results
            print(foodSearch["errors"]["error"][0]["message"])
            return -1
        if (foodSearch == -1):
            print('out of tokens')
            return -1

        print()  # print line for Format
        tmpFoodDictionary = {}
        for food in foodSearch["list"]["item"]:  # iterates through API Dictionary containg foods
            print('{:_<50}'.format(food["name"]), "Key: " + str(
                food["offset"]))  # prints: "food      Key: number in list"  ####TODO: edit this so it lines up
            print()
            tmpFoodDictionary[food["offset"]] = food["ndbno"]
        offset_number = input("Enter the key of the desired food: ")
        offset_number = int(offset_number)
        foodID = tmpFoodDictionary[offset_number]
        return foodID

    def getFoodSearch(self, foodName):
        foodID = self.getFoodID(foodName)
        if (foodID == -1):
            return False
        if (self.foodLibrary.isIDStored(foodID)):
            foodSearch = self.foodLibrary.getFoodSearch(foodID)
        else:
            foodSearch = self.searchByID(foodID)
        if (foodSearch == -1):
            return False
        return foodSearch

    def addFood(self, foodName, amount):  ## uses TokenBucket and IDSearch
        foodSearch = self.getFoodSearch(foodName)
        if (foodSearch):
            self.foodLibrary.addFood(foodSearch)
            self.nutrientLibrary.addNutrients(foodSearch, amount)
            return True
        return False

    @staticmethod
    def getAmount(food):
        number = input("Enter the amount of " + food + " in grams: ")
        return number

    @staticmethod
    def getFoodName():
        name = input("enter the name of the food: ")
        return name

    def fillLibrary(self):
        print("type 'exit' when finished")
        while (True):
            name = HealthyPy.getFoodName()
            if (name == "exit"):
                break
            amount = HealthyPy.getAmount(name)
            self.addFood(name, amount)

    def save(self):
        conn = sqlite3.connect('USDAData.db')
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS FOODS
            (name TEXT,
            foodid TEXT,
            json BLOB);''')

        for food in self.foodLibrary.foodHistory:
            foodID = (self.foodLibrary.foodHistory[food])
            string = json.dumps(self.foodLibrary.jsonDictionary[foodID])
            cur.execute("INSERT INTO FOODS VALUES (?,?,?)", (food, foodID, string))

        cur.execute('''CREATE TABLE IF NOT EXISTS NUTRIENTS
            (NAME TEXT,
            AMOUNT REAL,
            UNIT TEXT);''')

        for nutrient in self.nutrientLibrary.nutrientDictionary:
            cur.execute("INSERT INTO NUTRIENTS VALUES (?,?,?)",
                        (nutrient, self.nutrientLibrary.nutrientDictionary[nutrient],
                         self.nutrientLibrary.unitDictionary[nutrient]))

        cur.execute('''CREATE TABLE IF NOT EXISTS ATTRIBUTES
            (EXCLIST BLOB,
            COOLDOWN REAL,
            NUMTOKENS INTEGER,
            TIMESTAMP REAL,
            TOKENS INTEGER);''')
        string = str(self.nutrientLibrary.exclusionList)
        cur.execute("INSERT INTO ATTRIBUTES VALUES (?,?,?,?,?)",
                    (string, self.bucket.coolDown, self.bucket.numTokens, self.bucket.timeStamp, self.bucket.tokens))

        conn.commit()
        conn.close()

    def load(self):
        if (os.path.isfile('USDAData.db')):
            conn = sqlite3.connect('USDAData.db')
            cur = conn.cursor()
            cur.execute('SELECT * FROM FOODS')
            for row in cur:
                self.foodLibrary.foodHistory[row[0]] = row[1]  # 0:Name 1:FoodID 2:Json
                self.foodLibrary.jsonDictionary[row[1]] = row[2]

            cur.execute('SELECT * FROM NUTRIENTS')
            for row in cur:
                self.nutrientLibrary.nutrientDictionary[row[0]] = row[1]  # 0 name,1 amount, 2 unit
                self.nutrientLibrary.unitDictionary[row[0]] = row[2]

            cur.execute('SELECT * FROM ATTRIBUTES')
            row = cur.fetchone()
            self.nutrientLibrary.exclusionList = row[0]
            self.bucket.coolDown = row[1]
            self.bucket.numTokens = row[2]
            self.bucket.timeStamp = row[3]
            self.bucket.tokens = row[4]
            conn.commit()
            conn.close()

    @staticmethod
    def RESET():
        conn = sqlite3.connect('USDAData.db')
        cur = conn.cursor()
        cur.execute('DROP TABLE NUTRIENTS')
        cur.execute('DROP TABLE FOODS')
        cur.execute('DROP TABLE ATTRIBUTES')
        conn.commit()
        conn.close()

    def Main(self):
        answer = input('Do you want to load?: ')
        if (answer == 'yes'):
            self.load()
        self.fillLibrary()
        print("printing raw")
        nutrilib = self.nutrientLibrary.__dict__
        foodlib = self.foodLibrary.__dict__
        sear = self.searcher.__dict__
        buk = self.bucket.__dict__
        print("foodLibrary")
        pprint.pprint(foodlib)
        print("nutrientLibrary")
        pprint.pprint(nutrilib)
        print("SEARCHER")
        pprint.pprint(sear)
        print('BUCKET')
        pprint.pprint(buk)
        answer = input('Do you want to save?: ')
        if (answer == 'yes'):
            self.save()
        answer = input('RESET?(Drop all Tables): ')
        if (answer == 'yes'):
            HealthyPy.RESET()
