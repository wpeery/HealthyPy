class FoodLibrary:
    """stores food"""
    def __init__(self):
        self.jsonDictionary = {}  # foodID : json of page
        self.foodHistory = {}  # foodname : ndbno (contains a history of foods consumed)

    def addFood(self,foodSearch_ByID):
        foodName = foodSearch_ByID["report"]["food"]["name"]
        foodID = foodSearch_ByID["report"]["food"]["ndbno"]
        self.jsonDictionary[foodID] = foodSearch_ByID
        self.foodHistory[foodName] = foodID

    def isIDStored(self,foodID):
        if foodID in self.jsonDictionary:
            return True
        return False

    def isNameStored(self,foodName):
        if foodName in self.foodHistory:
            return True
        return False

    def getFoodID(self,foodName):
        return self.foodHistory[foodName]

    def getFoodSearch(self,foodID):
        return self.jsonDictionary[foodID]