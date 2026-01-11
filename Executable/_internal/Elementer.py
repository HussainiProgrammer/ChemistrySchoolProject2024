import json
import os
from PIL import Image


superscript_map = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶",
    "7": "⁷", "8": "⁸", "9": "⁹", "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ",
    "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ᶦ", "j": "ʲ", "k": "ᵏ",
    "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "۹", "r": "ʳ",
    "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ",
    "z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ᶜ", "D": "ᴰ", "E": "ᴱ", "F": "ᶠ",
    "G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ",
    "N": "ᴺ", "O": "ᴼ", "P": "ᴾ", "Q": "Q", "R": "ᴿ", "S": "ˢ", "T": "ᵀ",
    "U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "X": "ˣ", "Y": "ʸ", "Z": "ᶻ", "+": "⁺",
    "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾"}

trans = str.maketrans(
    ''.join(superscript_map.keys()),
    ''.join(superscript_map.values()))

class GetElement():
    def __init__(self):
        self.JSON_PATH = os.path.dirname(
            __file__) + "\\DataBase\\periodic-table-lookup.json"
        self.PHOTO_PATH = os.path.dirname(__file__) + "\\DataBase\\Ch\\"
        self.PHOTO_LIST = os.listdir(self.PHOTO_PATH)
    def getElementByName(self, element: str) -> str:
        """
        Return the element Symbol as a stirng by using its Name.
            element: String Value
        """
        self.element = element.lower()
        with open(self.JSON_PATH, encoding="utf8") as data:
            elemntsInfo = json.load(data)
            return str(elemntsInfo[self.element]["symbol"])

    def getElementBySymbol(self, symbol: str) -> str:
        """
        Return the element name as a stirng by using its Symbol.
            symbol: String Value
        """
        self.symbol = symbol
        with open(self.JSON_PATH, encoding="utf8") as data:
            elemntsInfo = json.load(data)
            elemntsOrder = elemntsInfo["order"]
            for ElemntsLoop in elemntsOrder:
                try:
                    if self.symbol == elemntsInfo[ElemntsLoop]["symbol"]:
                        return str(elemntsInfo[ElemntsLoop]["name"])
                except Exception as e:
                    print(e)
                    return 0, "You have entered wrong element symbol."

    def getElementByAtomicNumber(self, atomic_number: int) -> str:
        """
        Return the element name as a stirng by using its Atomic Number.
            atomic_number: Intger Value
        """

        self.atomic_number = atomic_number
        with open(self.JSON_PATH, encoding="utf8") as data:
            elemntsInfo = json.load(data)
            elemntsOrder = elemntsInfo["order"]
            for ElemntsLoop in elemntsOrder:
                try:
                    if self.atomic_number == elemntsInfo[ElemntsLoop]["number"]:
                        return str(elemntsInfo[ElemntsLoop]["name"])
                except Exception as e:
                    print(e)
                    return 0 ,"You have entered wrong element Atomic number."

    def getElementInfo(self, element: str) -> str:
        """
        Return the element Information as a stirng by using its Element names.
        Which you can get by using the Three Functions getElementByName, getElementBySymbol and getElementByAtomicNumber
            element: String Value
        """
        element = element.lower()
        with open(self.JSON_PATH, encoding="utf8") as data:
            elemntsInfo = json.load(data)
            Xelement = elemntsInfo[element]
            return Xelement["summary"] + "\nAtomic Mass:" + str(Xelement["atomic_mass"]) + f"\nPhase: {str(Xelement['phase'])}" + f'\nElectron Affinity: {str(Xelement["electron_affinity"])}'+f'\nCategory: {str(Xelement["category"])}' + "\nDiscovered By: "+str(Xelement["discovered_by"]).replace("None", "Unknown")+"\nNamed By: "+str(Xelement["named_by"]).replace("None", "Unknown") + "\nPeriod: "+str(Xelement["period"]) +"\nAppearance: " +str(Xelement['appearance']).replace('None','Unkown') +"\nBoils at: "+str(Xelement['boil']).replace('None','Unkown')+"\nMelts at: "+str(Xelement['melt']).replace('None','Unkown')

    def getElementElectroneConfiguration(self, element: str) -> str:
        """
        Return the Electrone Configuration of an element as a stirng by using its Element's name.
        Which you can get by using the Three Functions getElementByName, getElementBySymbol and getElementByAtomicNumber
            element: String Value
        """
        with open(self.JSON_PATH, encoding="utf8") as data:
            elemntsInfo = json.load(data)
            try:
                Xelement = str(elemntsInfo[element.lower()]["electron_configuration"]).replace("1", "¹").replace("2", "²").replace("3", "³").replace("4", "⁴").replace("5", "⁵").replace("6", "⁶").replace("7", "⁷").replace("8", "⁸").replace("9", "⁹").replace("0", "⁰")
                return "Electron Configuration:\n"+Xelement.replace('¹s','1s').replace('²s','2s').replace('²p','2p').replace('³s','3s').replace('³p','3p').replace('⁴s','4s').replace('³d','3d').replace('⁴p','4p').replace('⁵s','5s').replace('⁴d','4d').replace('⁵p','5p').replace('⁶s','6s').replace('⁴f','4f').replace('⁵d','5d').replace('⁶p','6p').replace('⁷s','7s').replace('⁵f','5f').replace('⁶d','6d').replace('⁷p','7p').replace('⁸s','8s')
            except:
                return f"There is no element in the name of {element}"
    def getElementColor(self,element_name:str) -> str:
        self.element_name = element_name

        with open(self.JSON_PATH, encoding="utf8") as data:
            elemntsInfo = json.load(data)
            elemntsOrder = elemntsInfo["order"]
            for ElemntsLoop in elemntsOrder:
                if self.element_name == elemntsInfo[ElemntsLoop]["name"]:
                    self.IMGsymbol = str(elemntsInfo[ElemntsLoop]["symbol"])
        for names in self.PHOTO_LIST:
            if f"{self.IMGsymbol}.png"  == names or f"{self.IMGsymbol}.jpg" == names:
                path = self.PHOTO_PATH + names
                image =  Image.open(path)
                return image

         
    def getElementSymbolByName(self,elementName:str) -> str:
        """
        Return the element's symbol as a stirng by using its Name.
            elementName: String Value
        """
        self.elementName = elementName
        with open(self.JSON_PATH, encoding="utf8") as data:
            elemntsInfo = json.load(data)
            elemntsOrder = elemntsInfo["order"]
            for ElemntsLoop in elemntsOrder:
                if self.elementName == elemntsInfo[ElemntsLoop]["name"]:
                    return str(elemntsInfo[ElemntsLoop]["symbol"])
    def getElementImage(self,element:str) -> Image:
        self.element = element
        image_bohr_path  = os.path.dirname(__file__) + '\\DataBase\\images'
        images_bohr_list = os.listdir(image_bohr_path)
        self.found = ''
        for each_image in images_bohr_list:
            if self.element == each_image.replace('.jpg','').replace('.png',''):
                image = Image.open(os.path.dirname(__file__) + '\\DataBase\\images\\' + each_image)
                self.found = 'normal'
                return image.resize((420,420)).crop((10,110,420,392))
            elif self.element == 'Ununennium':
                image = Image.open(os.path.dirname(__file__) + '\\DataBase\\images\\image-not-found.png')
                self.found = 'disabled'
                return image.resize((620,420)).crop((200,110,430,392))
            
    def _get_state(self) -> str:return self.found
    
    def _getNotImage(self,) -> Image:return Image.open(os.path.dirname(__file__) + '\\DataBase\\images\\image-not-found.png').resize((1050,620)).crop((200,160,700,592))
    
    
    def _getElementElectroneConfiguration(self, element: str) -> str:
        """
        Return the Electrone Configuration of an element as a stirng by using its Element's name.
        Which you can get by using the Three Functions getElementByName, getElementBySymbol and getElementByAtomicNumber
            element: String Value
        """
        with open(self.JSON_PATH, encoding="utf8") as data:
            elemntsInfo = json.load(data)
            try:
                Xelement = str(elemntsInfo[element.lower()]["electron_configuration"])
                return Xelement
            except:
                return f"There is no element in the name of {element}"
#Testing the lib.
if __name__ == "__main__":
    elementRoot = GetElement()
    elementName = elementRoot.getElementBySymbol('Uue')
    electron_configuration = elementRoot._getElementElectroneConfiguration(elementName) 
    blocks_list = electron_configuration.split()
    for i in range(len(blocks_list)):
         blocks_list[i][2] = blocks_list[i][2].translate(trans)
         ''.join(blocks_list)
    print(blocks_list)