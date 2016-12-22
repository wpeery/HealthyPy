class NutrientLibrary:
    """stores nutrients"""
    def __init__(self):
        self.nutrientDictionary = {}  # name:quantity
        self.unitDictionary = {}  # name of nutrient : unit
        self.exclusionList = ["Water"]  # list of nutrients to be excluded

    def addNutrients(self,foodSearch_ByID,amount):
        for nutrient in foodSearch_ByID["report"]["food"]["nutrients"]:
            if nutrient["name"] not in self.exclusionList:
                if nutrient["name"] not in self.unitDictionary:  # if not in unitDicitonary; update
                    self.unitDictionary[nutrient["name"]] = nutrient["unit"]
                if nutrient["name"] not in self.nutrientDictionary:  # if not in nutrientDictionary; update
                    self.nutrientDictionary[nutrient["name"]] = 0
                rawAmount = float(nutrient["value"]) / 100  # value is given per 100 grams of food
                                                            # adjust amount by dividing by 100
                amount = float(amount)
                adjustedAmount = rawAmount * amount
                self.nutrientDictionary[nutrient["name"]] += adjustedAmount  # add amount to nutrient Dictionary


    def printNutrients(self):  # prints nutrients and amounts and units
        for nutrient in self.nutrientDictionary:
            print('{:_<50}'.format(nutrient), self.nutrientDictionary[nutrient], self.unitDictionary[nutrient])

    def printExclusions(self):  # prints nutrients exclude
        for food in self.exclusionList:
            print(food)

    def excludeNutrient(self, nutrient):  # adds nutrient to exclusionList
        if nutrient not in self.exclusionList:
            self.exclusionList.append(nutrient)

    def includeNutrient(self, nutrient):  # removes nutrient from exclusionList
        if nutrient in self.exclusionList:
            self.exclusionList.remove(nutrient)
