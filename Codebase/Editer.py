import os
import json  

class EditJsonFile():
    def Edit(self, JsonFile:str, FirstData:str, SecondData:str, ThirdData:str,):
        self.JsonFile = JsonFile
        self.FirstData = FirstData
        self.SecondData = SecondData
        self.third = ThirdData
        self.CPTH = os.path.dirname(__file__) + '\\'
        self.JsonFile = self.CPTH + self.JsonFile
        with open(self.JsonFile, 'r') as f:
            self.data = json.load(f)
            for i in self.data[self.FirstData]:
                i[self.SecondData] = self.third
    def start(self,):
        os.remove(self.JsonFile)
        with open(self.JsonFile, 'w') as f:
            json.dump(self.data, f, indent=4)