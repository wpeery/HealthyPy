import requests

class Searcher:

    """Searches for a food using the gov api key"""

    def __init__(self):                            ##TODO PASS API KEY THROUGH CONSTRUCTOR
        self.gov_api_key = "9ZH2gqcl0QxJfd7aqlhaeIdckvl0ha3qFWnHtVUH"  # api key goes here

    def requestByName(self, foodName):
        url = "http://api.nal.usda.gov/ndb/search/?format=json&q=" + foodName + "&sort=r&max=25&offset=0&api_key=" + self.gov_api_key
        response = requests.get(url)
        foodSearch = response.json()
        return foodSearch

    def requestByID(self, foodID):
        url = "http://api.nal.usda.gov/ndb/reports/?ndbno=" + foodID + "&type=f&format=json&api_key=" + self.gov_api_key
        response = requests.get(url)
        foodSearch = response.json()
        return foodSearch
