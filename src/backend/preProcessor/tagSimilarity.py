import spacy
import csv
from spacytextblob.spacytextblob import SpacyTextBlob

nlp = spacy.load('en_core_web_lg')
nlp.add_pipe('spacytextblob')


class PreProcessor():
    def __init__(self):
        self.similarWords = []
        self.tags = []
        self.docs=[]

    def loadCSV(self):
        with open('../data/tags.csv', 'r') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                self.tags.append(row[2])
        csvFile.close()
        self.tags = self.tags[1:]
        self.tags = list(set([x.lower() for x in self.tags]))
        self.tags = sorted(self.tags)


    def tags2doc(self):
        for tag in self.tags:
            tokens = nlp(tag)
            self.docs.append(tokens)

    def getSimilarWords(self):
        for i in range(len(self.docs)):
            for j in range(i+1, len(self.docs)):
                similarity = self.docs[i].similarity(self.docs[j])
                leftPolarity = self.docs[i]._.polarity
                rightPolarity = self.docs[j]._.polarity
                polarity = leftPolarity * rightPolarity
                print(self.tags[i], self.tags[j], similarity)
                if similarity >= 0.65 and polarity >= 0:
                    self.similarWords.append([self.tags[i], self.tags[j],leftPolarity,rightPolarity, similarity])

    def saveCSV(self):
        with open('../data/similarTags.csv', 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(['tag1', 'tag2','polarity1','polarity2','similarity'])
            for similarWord in self.similarWords:
                writer.writerow(similarWord)
        csvFile.close()

    def run(self):
        self.loadCSV()
        self.tags2doc()
        self.getSimilarWords()
        self.saveCSV()
            




pp=PreProcessor()
pp.run()
