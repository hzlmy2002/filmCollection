import csv
import requests

class DataExtender:
    def __init__(self):
        self.imdbIDs = []
        self.apiKey = ""
        self.results = [] # [imdbID, content, date, director, leadActor, rotten tomatoes rating]

    def loadImdbIDs(self):
        with open("links.csv","r") as f:
            reader = csv.reader(f)
            for row in reader:
                self.imdbIDs.append(row[1])

        self.imdbIDs = self.imdbIDs[1:]
        with open("omdb_apikeys","r") as f:
            self.apiKey = f.read().strip()

    def getMovieData(self,imdbID):
        url = "http://www.omdbapi.com/?apikey={}&i=tt{}".format(self.apiKey,imdbID)
        r = requests.get(url).json()
        result=[imdbID, r["Plot"], r["Released"], r["Director"], r["Actors"]]
        find=False
        for rating in r["Ratings"]:
            if rating["Source"] == "Rotten Tomatoes":
                result.append(rating["Value"])
                find=True
                break
        if not find:
            result.append("N/A")
        return result

    def getMovieDataAll(self):
        for i in range(len(self.imdbIDs)):
            imdbID = self.imdbIDs[i]
            print("Getting data for movie {} of {}".format(i+1,len(self.imdbIDs)))
            self.results.append(self.getMovieData(imdbID))
    
    def saveAsCSV(self):
        with open("extendedMovieData.csv","w") as f:
            writer = csv.writer(f)
            writer.writerow(["imdbID","content","date","director","leadActor","rotten_tomatoes_rating"])
            for result in self.results:
                writer.writerow(result)

    def run(self):
        self.loadImdbIDs()
        self.getMovieDataAll()
        self.saveAsCSV()
        


de=DataExtender()
de.run()
    