import re

molarMasses = {'H': 1, 'He': 4, 'Li': 7, 'Be': 9, 'B': 11, 'C': 12, 'N': 14, 'O': 16, 'F': 19, 'Ne': 20, 'Na': 23, 'Mg': 24.5, 'Al': 27, 'Si': 28, 'P': 31, 'S': 32, 'Cl': 35.5, 'K': 39, 'Ar': 40, 'Ca': 40, 'Sc': 45, 'Ti': 48, 'V': 51, 'Cr': 52, 'Mn': 55, 'Fe': 56, 'Ni': 58.5, 'Co': 59, 'Cu': 63.5, 'Zn': 65.5, 'Ga': 69.5, 'Ge': 72.5, 'As': 75, 'Se': 79, 'Br': 80, 'Kr': 84, 'Rb': 85.5, 'Sr': 87.5, 'Y': 89, 'Zr': 91, 'Nb': 93, 'Mo': 96, 'Tc': 98, 'Ru': 101, 'Rh': 103, 'Pd': 106.5, 'Ag': 108, 'Cd': 112.5, 'In': 115, 'Sn': 118.5, 'Sb': 122, 'Te': 127.5, 'I': 127, 'Xe': 131.5, 'Cs': 133, 'Ba': 137.5, 'La': 139, 'Ce': 140, 'Pr': 141, 'Nd': 144, 'Pm': 145, 'Sm': 150.5, 'Eu': 152, 'Gd': 157.5, 'Tb': 159, 'Dy': 162.5, 'Ho': 165, 'Er': 167.5, 'Tm': 169, 'Yb': 173, 'Lu': 174, 'Hf': 178.5, 'Ta': 181, 'W': 184, 'Re': 186, 'Os': 190, 'Ir': 192, 'Pt': 195, 'Au': 197, 'Hg': 200.5, 'Tl': 204.5, 'Pb': 207, 'Bi': 209, 'Th': 232, 'Pa': 231, 'U': 238, 'Np': 237, 'Pu': 244, 'Am': 243, 'Cm': 247, 'Bk': 247, 'Cf': 251, 'Es': 252, 'Fm': 257, 'Md': 258, 'No': 259, 'Lr': 262, 'Rf': 267, 'Db': 270, 'Sg': 271, 'Bh': 270, 'Hs': 277, 'Mt': 276, 'Ds': 281, 'Rg': 280, 'Cn': 285, 'Nh': 284, 'Fl': 289, 'Mc': 288, 'Lv': 293, 'Ts': 294, 'Og': 294, "H2O": 18}

def toInt(number):
    if number == int(number): number = int(number)
    return number

def findSubstance(text: str) -> bool:
    return re.findall("\\b[A-Z][a-z]?\\d*(?:[A-Z][a-z]?\\d*)*(?:\\.\\d*H2O)?\\b", text)

def getElements(formula: str):
    if formula == "H2O": return {"H2O": 1}
    
    if "." in formula: # i.e. if crystallization water is in the compound
        if (match := re.match("(^\\d+)", formula)) is not None: m = int(match.groups()[0])
        else: m = 1

        elements = {element.group(1): int(element.group(2) or "1")*m for element in re.finditer("([A-Z][a-z]?)(\\d*)", formula[:formula.index(".")])}
        
        if (match := re.match("(\\d+)H2O", formula[formula.index(".")+1:])): nOfH2O = int(match.groups()[0])
        else: nOfH2O = 1

        elements["H2O"] = nOfH2O

    else:
        elements = {element.group(1): int(element.group(2) or "1") for element in re.finditer("([A-Z][a-z]?)(\\d*)", formula)}

    return elements

def formula_to_LaTeX(formula: str) -> str:
    return re.sub("([A-Z][a-z]?)(\\d+)", "\\1_{\\2}", formula)

class Substance:
    def __init__(self, formula: str):
        self.formula = formula
        self.LaTeX = formula_to_LaTeX(formula)
        self.elements = getElements(formula) # Without accounting for crystallization water (which is found in some compounds e.g. Na2SO4.7H2O somewhere in the textbook), this line could be used instead: self.elements = {element.group(1): int(element.group(2) or "1") for element in re.finditer("([A-Z][a-z]?)(\\d*)", formula)}
        self.molarMass = sum([molarMasses[element] * number for element, number in self.elements.items()])

    def __eq__(self, __value) -> bool:
        return type(__value) == Substance and __value.formula == self.formula
    
    def __repr__(self) -> str:
        return self.LaTeX