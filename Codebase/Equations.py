import json
import os
import re
import matplotlib.pyplot as plt

plt.rcParams["figure.facecolor"] = "2b2b2b"
plt.rcParams["axes.facecolor"] = "2b2b2b"
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.default'] = 'regular'

data = json.load(file := open(os.path.dirname(__file__) + "/DataBase/equations.json", "r+", encoding="utf-8"))

def getFigure(reactantsInput):
        reactantsInput = reactantsInput.replace("+", " ").split()
        equations = json.load(file := open(os.path.dirname(__file__) + "/DataBase/equations.json", "r+", encoding="utf-8")); file.close()

        latex = ""
        for eq in list(equations.values())[2:]:
            if sorted([re.sub(r"^[0-9./]+", "", reactant) for reactant in eq["reactants"]]) == sorted([re.sub(r"^[0-9./]+", "", reactant) for reactant in reactantsInput]):
                latex = (" + ".join([re.sub(r'([a-zA-Z])(\d+)', r'\1_{\2}', re.sub(r'(\d+)/(\d+)', r'\frac{\1}{\2}', reactant)) for reactant in eq["reactants"]]) + " " + eq["arrow"] + " " + " + ".join([re.sub(r'([a-zA-Z])(\d+)', r'\1_{\2}', re.sub(r'(\d+)/(\d+)', r'\frac{\1}{\2}', product)) for product in eq["products"]])).replace("\x0c", "\\f")
                break

        if latex:
            figure = plt.figure(figsize=(13.25, 2))
            ax = figure.add_subplot(111)

            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_visible(False)

            ax.text(-0.15, 0.37, f"${latex}$", fontsize=45, fontdict=None).set_color("white")
            
        else: figure = None

        return figure