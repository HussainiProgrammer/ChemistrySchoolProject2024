from value import Value
from scientific_notation import ScientificNotation
from substance import Substance, findSubstance
import math
import re

AvogadrosNumber = ScientificNotation(6.023, 23)

units = {
    "Mass": ["g", "kg", "mg"],
    "Number of Moles": ["mol"],
    "Number of Particles": [],
    "Equivalent Mass": ["g"],
    "Valance": [],
    "Volume": ["L", "mL", "m³", "cm³"],
    "Temperature": ["K", "°C"],
    "Pressure": ["atm", "Torr", "mmHg", "cmHg", "Pa"],
    "Density": ["g/L", "g/mL", "g/m³", "g/cm³", "kg/L", "kg/mL", "kg/m³", "kg/cm³", "mg/L", "mg/mL", "mg/m³", "mg/cm³", "ppm"],
    "Molar Volume": ["L/mol"],
    "Mole Fraction": [],
    "Diffusion Rate": ["mL/s"],
    "Diffusion Time": ["s"]
}

def toInt(number):
    if number == int(number): number = int(number)
    return number

def findValue(quantity: str, objects: list, values: list[Value]) -> Value:
    for value in values:
        if value.quantity == quantity and value.objects == objects:
            return value

def getSolution(givenValues: list[Value], requiredValues: list[dict]):
    for index, g in enumerate(givenValues):
        gObjects = g[3].replace(" ", "").split(",")
        for p, object in enumerate(gObjects):
            if type(object) == str:
                if (formula:= findSubstance(object)):
                    gObjects[p] = Substance(formula[0])
                elif object.isdigit():
                    gObjects[p] = int(object)

        g[3] = gObjects

        givenValues[index] = Value(*g)

    for index, r in enumerate(requiredValues):
        rObjects = r[2].replace(" ", "").split(",")
        for p, object in enumerate(rObjects):
            if type(object) == str:
                if (formula:= findSubstance(object)):
                    rObjects[p] = Substance(formula[0])
                elif object.isdigit():
                    rObjects[p] = int(object)

        requiredValues[index] = {"quantity": r[0], "objects": rObjects, "unit": r[1]}

    if givenValues and requiredValues:
        listOfSolutions = []

        for value in requiredValues:
            requiredFunction: function = eval(value["quantity"].replace(" ", "_"))
            solution = requiredFunction(givenValues, value["objects"], value["unit"]) if len(units[value["quantity"]]) > 1 else requiredFunction(givenValues, value["objects"])

            if solution is None:
                listOfSolutions.append(f"Sorry$, we couldn't find the {value["quantity"]} of ${value["objects"][0]}.")

            else:
                listOfSolutions.append(solution[0])
                givenValues.append(solution[1])

        return "$\n\n$".join(listOfSolutions)

def Mass(values: list[Value], objects: list, unit: str, exceptions: list[str]=[]):
    solutions = []

    if "n=m/M" not in exceptions:
        sol = ""
        steps = 0

        if type(objects[0]) == Substance:
            molar_mass = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)

            number_of_moles = findValue("Number of Moles", objects, values)

            if (number_of_moles is None) and (find_number_of_moles := Number_of_Moles(values, objects, exceptions+["n=m/M"])):
                sol += find_number_of_moles[0] + "$\n$"
                number_of_moles = find_number_of_moles[1]
                steps += 1

            if number_of_moles:            
                steps += 1

                result = Value("Mass", toInt(round(number_of_moles.value * molar_mass.value, 2)), "g", objects)
                sol += "n_{mole}$ $=$ $\\frac{m}{M}$\n$" + number_of_moles.LaTeX() + "$) $=$ $\\frac{m}{" + molar_mass.LaTeX() + "}$\n$" + number_of_moles.LaTeX() + "$ $\\times$ $" + molar_mass.LaTeX() + "$ $=$ $m$\n$" + result.LaTeX() + "$ $=$ $m"

                if unit != "g":
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $m"

                solutions.append((sol, result, steps))

    if "density" not in exceptions:
        sol = ""
        steps = 0

        volume = findValue("Volume", objects, values)

        if (volume is None) and (find_volume := Volume(values, objects, "L", exceptions+["density"])):
            sol += find_volume[0] + "$\n$"
            volume = find_volume[1]
            steps += 1

        if volume:
            density = findValue("Density", objects, values)

            if (not density) and (find_density := Density(values, objects, f"{unit}/{volume.unit}", exceptions+["density"])):
                sol += find_density[0] + "$\n$"
                density = find_density[1]
                steps += 1

            if density:
                if density.unit != f"{unit}/{volume.unit}": sol += "ρ$ $=$ $" + density.LaTeX() + "$ $=$ $" + (density := density.in_another_unit(f"{unit}/{volume.unit}")).LaTeX() + "$\n\n$"

                steps += 1

                result = Value("Mass", toInt(round(density.value * volume.value, 2)), unit, objects)
                sol += "ρ$ $=$ $\\frac{m}{V}$\n$" + density.LaTeX() + "$ $=$ $\\frac{m}{" + volume.LaTeX() + "}$\n$" + density.LaTeX() + "$ $\\times$ $" + volume.LaTeX() + "$ $=$ $m$\n$" + result.LaTeX() + "$ $=$ $m"

                solutions.append((sol, result, steps))

    if "m=A*n*m/M" not in exceptions:
        sol = ""
        steps = 0

        if len(objects) >= 2 and type(objects[0]) == type(objects[1]) == Substance:
            molar_mass = objects[0].molarMass
            compound_molar_mass = objects[1].molarMass
            number_of_substance = objects[1].elements[list(objects[0].elements.keys())[0]]

            compound_mass = findValue("Mass", objects[1:], values)

            if (compound_mass is None) and (find_compound_mass := Mass(values, objects, "g", exceptions+["m=A*n*m/M"])):
                sol += find_compound_mass[0] + "$\n$"
                compound_mass = find_compound_mass[1]
                steps += 1

            if compound_mass:
                if compound_mass.unit != "g": sol += "m_{" + objects[1].LaTeX + "}$ $=$  $" + compound_mass.LaTeX() + "$ $=$ $" + (compound_mass := compound_mass.in_another_unit("g")).LaTeX() + "$\n\n$"

                steps += 1

                result = Value("Mass", toInt(round(molar_mass * number_of_substance * compound_mass.value / compound_molar_mass, 2)), "g", objects)
                sol += "m_{element}$ $=$ $\\frac{M_{element} \\times n_{particle} \\times m_{compound}}{M_{compound}}$\n$m_{" + objects[0].LaTeX + "}$ $=$ $\\frac{" + str(molar_mass) + " \\times " + str(number_of_substance) + " \\times " + compound_mass.LaTeX() + "}{" + str(compound_molar_mass) + "}$\n$m_{" + objects[0].LaTeX + "}$ $=$ $" + result.LaTeX()

                if unit != "g":
                    sol += "$\n$m_{" + objects[0].LaTeX + "}$ $=$ $" + result.in_another_unit(unit).LaTeX()
                    result.change_unit(unit)

                solutions.append((sol, result, steps))

    if "ideal gas" not in exceptions:
        sol = ""
        steps = 0

        if type(objects[0]) == Substance:
            if objects[-1] == 1:
                molar_mass1 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)

                pressure1 = findValue("Pressure", objects, values)
                volume1 = findValue("Volume", objects, values)
                temperature1 = findValue("Temperature", objects, values)

                if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                    sol += find_pressure1[0] + "$\n$"
                    pressure1 = find_pressure1[1]
                    steps += 1

                if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["ideal gas"])):
                    sol += find_volume1[0] + "$\n$"
                    volume1 = find_volume1[1]
                    steps += 1

                if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                    sol += find_temperature1[0] + "$\n$"
                    temperature1 = find_temperature1[1]
                    steps += 1

                objects2 = objects[:-1]+[2]
                for value in values:
                    if value.objects[-1] == 2 and objects2 != value.objects:
                        objects2 = value.objects
                        break

                pressure2 = findValue("Pressure", objects2, values)
                volume2 = findValue("Volume", objects2, values)
                temperature2 = findValue("Temperature", objects2, values)
                number_of_moles2 = findValue("Number of Moles", objects2, values)

                if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+["ideal gas"])):
                    sol += find_pressure2[0] + "$\n$"
                    pressure2 = find_pressure2[1]
                    steps += 1

                if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["ideal gas"])):
                    sol += find_volume2[0] + "$\n$"
                    volume2 = find_volume2[1]
                    steps += 1

                if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
                    sol += find_temperature2[0] + "$\n$"
                    temperature2 = find_temperature2[1]
                    steps += 1

                if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["ideal gas"])):
                    sol += find_number_of_moles2[0] + "$\n$"
                    number_of_moles2 = find_number_of_moles2[1]
                    steps += 1

                if pressure1 and volume1 and temperature1 and pressure2 and volume2 and temperature2 and number_of_moles2:
                    a,b,c,d,e,f = False,False,False,False,False, False
                    if pressure1.unit != pressure2.unit:
                        if a := (pressure1.unit != "atm"):
                            sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                        if b := (pressure2.unit != "atm"):
                            if a: sol += "$"
                            sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                    if volume1.unit != volume2.unit:
                        if c := (volume1.unit != "L"):
                            if a or b: sol += "$"
                            sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                        if d := (volume2.unit != "L"):
                            if a or b or c: sol += "$"
                            sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                    if e := (temperature1.unit != "K"):
                        if a or b or c or d: sol += "$"
                        sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                    if f := (temperature2.unit != "K"):
                        if a or b or c or d or e: sol += "$"
                        sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                    if a or b or c or d or e or f: sol += "\n$"

                    steps += 1

                    result = Value("Mass", toInt(round((number_of_moles2.value * temperature2.value * molar_mass1.value * pressure1.value * volume1.value)/(pressure2.value * volume2.value * temperature1.value), 2)), "g", objects)
                    sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $k$ $=$ $\\frac{nRT}{PV}$\n$\\therefore \\frac{n_{1}RT_{1}}{P_{1}V_{1}}$ $=$ $\\frac{n_{2}RT_{2}}{P_{2}V_{2}}$\n$\\frac{\\frac{m_{1}}{M_{1}}RT_{1}}{P_{1}V_{1}}$ $=$ $\\frac{n_{2}RT_{2}}{P_{2}V_{2}}$\n$\\frac{\\frac{m_{1}}{" + molar_mass1.LaTeX() + "} \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}$ $=$ $\\frac{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}$\n$m_{1}$ $=$ $\\frac{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + " \\times " + molar_mass1.LaTeX() + " \\times " + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() +" \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}$\n$m_{1}$ $=$ $" + result.LaTeX()

                    if unit != "g":
                        result.change_unit(unit)
                        sol += "$\n$m_{1}$ $=$ $" + result.LaTeX()

                    solutions.append((sol, result, steps))

            elif objects[-1] == 2:
                molar_mass2 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)

                pressure2 = findValue("Pressure", objects, values)
                volume2 = findValue("Volume", objects, values)
                temperature2 = findValue("Temperature", objects, values)

                if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                    sol += find_pressure2[0] + "$\n$"
                    pressure2 = find_pressure2[1]
                    steps += 1

                if (volume2 is None) and (find_volume2 := Volume(values, objects, "L", exceptions+["ideal gas"])):
                    sol += find_volume1[0] + "$\n$"
                    volume2 = find_volume1[1]
                    steps += 1

                if (temperature2 is None) and (find_temperature2 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                    sol += find_temperature2[0] + "$\n$"
                    temperature2 = find_temperature2[1]
                    steps += 1

                objects1 = objects[:-1]+[1]
                for value in values:
                    if value.objects[-1] == 1 and objects1 != value.objects:
                        objects1 = value.objects
                        break

                pressure1= findValue("Pressure", objects1, values)
                volume1 = findValue("Volume", objects1, values)
                temperature1 = findValue("Temperature", objects1, values)
                number_of_moles1 = findValue("Number of Moles", objects1, values)

                if (pressure1 is None) and (find_pressure1 := Pressure(values, objects1, "atm", exceptions+["ideal gas"])):
                    sol += find_pressure1[0] + "$\n$"
                    pressure1 = find_pressure1[1]
                    steps += 1

                if (volume1 is None) and (find_volume1 := Volume(values, objects1, "L", exceptions+["ideal gas"])):
                    sol += find_volume1[0] + "$\n$"
                    volume1 = find_volume1[1]
                    steps += 1

                if (temperature1 is None) and (find_temperature1 := Temperature(values, objects1, "K", exceptions+["ideal gas"])):
                    sol += find_temperature1[0] + "$\n$"
                    temperature1 = find_temperature1[1]
                    steps += 1

                if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects1, exceptions+["ideal gas"])):
                    sol += find_number_of_moles1[0] + "$\n$"
                    number_of_moles1 = find_number_of_moles1[1]
                    steps += 1

                if pressure2 and volume2 and temperature2 and pressure1 and volume1 and temperature1 and number_of_moles1:
                    a,b,c,d,e,f = False,False,False,False,False, False
                    if pressure1.unit != pressure2.unit:
                        if a := (pressure1.unit != "atm"):
                            sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                        if b := (pressure2.unit != "atm"):
                            if a: sol += "$"
                            sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                    if volume1.unit != volume2.unit:
                        if c := (volume1.unit != "L"):
                            if a or b: sol += "$"
                            sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                        if d := (volume2.unit != "L"):
                            if a or b or c: sol += "$"
                            sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                    if e := (temperature1.unit != "K"):
                        if a or b or c or d: sol += "$"
                        sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                    if f := (temperature2.unit != "K"):
                        if a or b or c or d or e: sol += "$"
                        sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                    if a or b or c or d or e or f: sol += "\n$"

                    steps += 1

                    result = Value("Mass", toInt(round((number_of_moles1.value * temperature1.value * molar_mass2.value * pressure2.value * volume2.value)/(pressure1.value * volume1.value * temperature2.value), 2)), "g", objects)
                    sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $k$ $=$ $\\frac{nRT}{PV}$\n$\\therefore \\frac{n_{1}RT_{1}}{P_{1}V_{1}}$ $=$ $\\frac{n_{2}RT_{2}}{P_{2}V_{2}}$\n$\\frac{n_{1}RT_{1}}{P_{1}V_{1}}$ $=$ $\\frac{\\frac{m_{2}}{M_{2}}RT_{2}}{P_{2}V_{2}}$\n$\\frac{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}$ $=$ $\\frac{\\frac{m_{2}}{" + molar_mass2.LaTeX() + "} \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}$\n$\\frac{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + " \\times " + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + " \\times " + molar_mass2.LaTeX() + "}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() +" \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}$ $=$ $m_{2}$\n$" + result.LaTeX() + "$ $=$ $m_{2}"

                    if unit != "g":
                        result.change_unit(unit)
                        sol += "$\n$" + result.LaTeX() + "$ $=$ $m_{2}"

                    solutions.append((sol, result, steps))
            
            else:
                molar_mass = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)
                pressure = findValue("Pressure", objects, values)
                volume = findValue("Volume", objects, values)
                temperature = findValue("Temperature", objects, values)

                if (pressure is None) and (find_pressure := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                    sol += find_pressure[0] + "$\n$"
                    pressure = find_pressure[1]
                    steps += 1

                if (volume is None) and (find_volume := Volume(values, objects, "L", exceptions+["ideal gas"])):
                    sol += find_volume[0] + "$\n$"
                    volume = find_volume[1]
                    steps += 1

                if (temperature is None) and (find_temperature := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                    sol += find_temperature[0] + "$\n$"
                    temperature = find_temperature[1]
                    steps += 1

                if pressure and volume and temperature:
                    if a := (pressure.unit != "atm"):
                        sol += "P$ $=$ $" + pressure.LaTeX() + "$ $=$ $" + (pressure := pressure.in_another_unit("atm")).LaTeX() + "$\n"

                    if b := (volume.unit != "L"):
                        if a: sol += "$"
                        sol += "V$ $=$ $" + volume.LaTeX() + "$ $=$ $" + (volume := volume.in_another_unit("L")).LaTeX() + "$\n"
                    
                    if c := (temperature.unit != "K"):
                        if a or b: sol += "$"
                        sol += "T$ $=$ $" + temperature.LaTeX() + "$ $=$ $" + (temperature := temperature.in_another_unit("K")).LaTeX() + "$\n"

                    if a or b or c: sol += "\n$"

                    steps += 1

                    result = Value("Mass", toInt(round((pressure.value * volume.value * molar_mass.value) / (0.082 * temperature.value), 2)), "g", objects)
                    sol += "PV$ $=$ $nRT$\n$PV$ $=$ $\\frac{m}{M}RT$\n$" + pressure.LaTeX() + "\\times " + volume.LaTeX() + "$ $=$ $\\frac{m}{" + molar_mass.LaTeX() +"} \\times 0.082 \\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature.LaTeX() + "$\n$\\frac{" + pressure.LaTeX() + " \\times " + volume.LaTeX() + " \\times " + molar_mass.LaTeX() + "}{0.082 \\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature.LaTeX() + "}$ $=$ $m$\n$" + result.LaTeX() + "$ $=$ $m"

                    if unit != "g":
                        result.change_unit(unit)
                        sol += "$\n$" + result.LaTeX() + "$ $=$ $m"

                    solutions.append((sol, result, steps))

    if "m/eq" not in exceptions:
        if objects[-1] == 1:
            objects2 = None
            for value in values:
                if value.objects[-1] == 2:
                    objects2 = value.objects

            if objects2:
                equivalent_mass1 = findValue("Equivalent Mass", objects, values)

                if (equivalent_mass1 is None) and (find_equivalent_mass1 := Equivalent_Mass(values, objects, exceptions+["m/eq"])):
                    sol += find_equivalent_mass1[0] + "$\n$"
                    equivalent_mass1 = find_equivalent_mass1[1]
                    steps += 1

                mass2 = findValue("Mass", objects2, values)
                equivalent_mass2 = findValue("Equivalent Mass", objects2, values)

                if (mass2 is None) and (find_mass2 := Mass(values, objects2, "g", exceptions+["m/eq"])):
                    sol += find_mass2[0] + "$\n$"
                    mass2 = find_mass2[1]
                    steps += 1

                if (equivalent_mass2 is None) and (find_equivalent_mass2 := Equivalent_Mass(values, objects2, exceptions+["m/eq"])):
                    sol += find_equivalent_mass2[0] + "$\n$"
                    equivalent_mass2 = find_equivalent_mass2[1]
                    steps += 1

                if equivalent_mass1 and equivalent_mass2 and mass2:
                    steps += 1

                    result = Value("Mass", toInt(round((mass2.value * equivalent_mass1.value)/(equivalent_mass2.value), 2)), mass2.unit)
                    sol += "\\frac{m_{1}}{eq_{1}}$ $=$ $\\frac{m_{2}}{eq_{2}}$\n$\\frac{m_{1}}{" + equivalent_mass1.LaTeX() + "}$ $=$ $\\frac{" + mass2.LaTeX() + "}{" + equivalent_mass2.LaTeX() + "}$\n$m_{1}$ $=$ $\\frac{" + mass2.LaTeX() + " \\times " + equivalent_mass1.LaTeX() + "}{" + equivalent_mass2.LaTeX() + "}$\n$m_{1}$ $=$ $" + result.LaTeX()

                    if result.unit != unit:
                        result.change_unit(unit)
                        sol += "$\n$m_{1}$ $=$ $" + result.LaTeX()

                    solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            objects1 = None
            for value in values:
                if value.objects[-1] == 1:
                    objects1 = value.objects

            if objects1:
                equivalent_mass2 = findValue("Equivalent Mass", objects, values)

                if (equivalent_mass2 is None) and (find_equivalent_mass2 := Equivalent_Mass(values, objects, exceptions+["m/eq"])):
                    sol += find_equivalent_mass2[0] + "$\n$"
                    equivalent_mass2 = find_equivalent_mass2[1]
                    steps += 1

                mass1 = findValue("Mass", objects1, values)
                equivalent_mass1 = findValue("Equivalent Mass", objects1, values)

                if (mass1 is None) and (find_mass1 := Mass(values, objects1, "g", exceptions+["m/eq"])):
                    sol += find_mass1[0] + "$\n$"
                    mass1 = find_mass1[1]
                    steps += 1

                if (equivalent_mass1 is None) and (find_equivalent_mass1 := Equivalent_Mass(values, objects1, exceptions+["m/eq"])):
                    sol += find_equivalent_mass1[0] + "$\n$"
                    equivalent_mass1 = find_equivalent_mass1[1]
                    steps += 1

                if equivalent_mass1 and equivalent_mass2 and mass1:
                    steps += 1

                    result = Value("Mass", toInt(round((mass1.value * equivalent_mass2.value)/(equivalent_mass1.value), 2)), mass1.unit)
                    sol += "\\frac{m_{1}}{eq_{1}}$ $=$ $\\frac{m_{2}}{eq_{2}}$\n$\\frac{" + mass1.LaTeX() + "}{" + equivalent_mass1.LaTeX() + "}$ $=$ $\\frac{m_{2}}{" + equivalent_mass2.LaTeX() + "}$\n$\\frac{" + mass1.LaTeX() + " \\times " + equivalent_mass2.LaTeX() + "}{" + equivalent_mass1.LaTeX() + "}$ $=$ $m_{2}$\n$" + result.LaTeX() + "$ $=$ $m_{2}"

                    if result.unit != unit:
                        result.change_unit(unit)
                        sol += "$\n$" + result.LaTeX() + "$ $=$ $m_{2}" 

                    solutions.append((sol, result, steps))

    if len(solutions) == 0:
        return

    elif len(solutions) == 1:
        return solutions[0][:2]

    else:
        return min(solutions, key=lambda x: x[2])[:2]

def Number_of_Moles(values: list[Value], objects: list, exceptions: list[str]=[]):
    solutions = []

    if "n=n/N" not in exceptions:
        if (number_of_particles := findValue("Number of Particles", objects, values)):
            result = Value("Number of Moles", number_of_particles.value/AvogadrosNumber, "mol", objects)
            sol = "n_{mole}$ $=$ $\\frac{n_{particle}}{N_{A}}$\n$n_{mole}$ $=$ $\\frac{" + number_of_particles.LaTeX() + "}{" + AvogadrosNumber.LaTeX() + "}$\n$n_{mole}$ $=$ $" + result.LaTeX()

            solutions.append((sol, result, 1, 1))

    if "n=m/M" not in exceptions:
        sol = ""
        steps = 0

        if type(objects[0]) == Substance:
            molar_mass = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)

            mass = findValue("Mass", objects, values)

            if (mass is None) and (find_mass := Mass(values, objects, "g", exceptions+["n=m/M"])):
                sol += find_mass[0] + "$\n$"
                mass = find_mass[1]
                steps += 1

            if mass:
                if mass.unit != "g": sol += "m$ $=$ $" + mass.LaTeX() + "$ $=$ $" + (mass := mass.in_another_unit("g")).LaTeX() + "$\n\n$"

                steps += 1

                result = Value("Number of Moles", toInt(round(mass.value / molar_mass.value, 2)), "mol", objects)
                sol = "n_{mole}$ $=$ $\\frac{m}{M}$\n$n_{mole}$ $=$ $\\frac{" + mass.LaTeX() + "}{" + molar_mass.LaTeX() + "}$\n$n_{mole}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

    if "molar volume" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            objects2 = None
            for value in values:
                if value.objects[-1] == 2:
                    objects2 = value.objects

            if objects2:
                volume1 = findValue("Volume", objects, values)

                if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["molar volume"])):
                    sol += find_volume1[0] + "$\n$"
                    volume1 = find_volume1[1]
                    steps += 1

                volume2 = findValue("Volume", objects2, values)

                if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["molar volume"])):
                    sol += find_volume2[0] + "$\n$"
                    volume2 = find_volume2[1]
                    steps += 1

                number_of_moles2 = findValue("Number of Moles", objects2, values)

                if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["molar volume"])):
                    sol += find_number_of_moles2[0] + "$\n$"
                    number_of_moles2 = find_number_of_moles2[1]
                    steps += 1

                if volume1 and volume2 and number_of_moles2:
                    if volume1.unit != volume2.unit:
                        if a := (volume1.unit != "L"):
                            sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                        if volume2.unit != "L":
                            if a: sol += "$"
                            sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                        sol += "\n$"

                    steps += 1

                    result = Value("Number of Moles", toInt(round((volume1.value * number_of_moles2.value)/(volume2.value), 2)), "mol", objects)
                    sol += "\\frac{V_{1}}{n_{1}}$ $=$ $\\frac{V_{2}}{n_{2}}$\n$\\frac{" + volume1.LaTeX() + "}{n_{1}}$ $=$ $\\frac{" + volume2.LaTeX() + "}{" + number_of_moles2.LaTeX() + "}$\n$\\frac{" + volume1.LaTeX() + " \\times " + number_of_moles2.LaTeX() + "}{" + volume2.LaTeX() + "}$ $=$ $n_{1}$\n$" + result.LaTeX() + "$ $=$ $n_{1}"

                    solutions.append((sol, result, steps))
 
        elif objects[-1] == 2:
            objects1 = None
            for value in values:
                if value.objects[-1] == 1:
                    objects1 = value.objects

            if objects1:
                volume2 = findValue("Volume", objects, values)

                if (volume2 is None) and (find_volume2 := Volume(values, objects, "L", exceptions+["molar volume"])):
                    sol += find_volume2[0] + "$\n$"
                    volume2 = find_volume2[1]
                    steps += 1

                volume1 = findValue("Volume", objects1, values)

                if (volume1 is None) and (find_volume1 := Volume(values, objects1, "L", exceptions+["molar volume"])):
                    sol += find_volume1[0] + "$\n$"
                    volume1 = find_volume1[1]
                    steps += 1

                number_of_moles1 = findValue("Number of Moles", objects1, values)

                if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects1, exceptions+["molar volume"])):
                    sol += find_number_of_moles1[0] + "$\n$"
                    number_of_moles1 = find_number_of_moles1[1]
                    steps += 1

                if volume1 and volume2 and number_of_moles1:
                    if volume1.unit != volume2.unit:
                        if a := (volume1.unit != "L"):
                            sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                        if volume2.unit != "L":
                            if a: sol += "$"
                            sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                        sol += "\n$"

                    steps += 1

                    result = Value("Number of Moles", toInt(round((volume2.value * number_of_moles1.value)/(volume1.value), 2)), "mol", objects)
                    sol += "\\frac{V_{1}}{n_{1}}$ $=$ $\\frac{V_{2}}{n_{2}}$\n$\\frac{" + volume1.LaTeX() + "}{" + number_of_moles1.LaTeX() + "}$ $=$ $\\frac{" + volume2.LaTeX() + "}{n_{2}}$\n$n_{2}$ $=$ $\\frac{" + volume2.LaTeX() + " \\times " + number_of_moles1.LaTeX() + "}{" + volume1.LaTeX() + "}$\n$n_{2}$ $=$ $" + result.LaTeX()

                    solutions.append((sol, result, steps))
 
        else:
            volume = findValue("Volume", objects, values)

            if (volume is None) and (find_volume := Volume(values, objects, "L", exceptions+["molar volume"])):
                sol += find_volume[0] + "$\n$"
                volume = find_volume[1]
                steps += 1

            if volume is not None:
                molar_volume = findValue("Molar Volume", objects, values)

                if (molar_volume is None) and (find_molar_volume := Molar_Volume(values, objects, exceptions+["molar volume"])):
                    sol += find_molar_volume[0] + "$\n$"
                    molar_volume = find_molar_volume[1]
                    steps += 1

                if molar_volume is not None:
                    steps += 1

                    if volume.unit != "L":
                        sol += "V$ $=$ $" + volume.LaTeX() + "$ $=$ $" + (volume := volume.in_another_unit("L")).LaTeX() + "$\n\n$"

                    result = Value("Number of Moles", toInt(round(volume.value / molar_volume.value, 2)), "mol", objects)
                    sol += "V_{m}$ $=$ $\\frac{V}{n_{mole}}$\n$" + molar_volume.LaTeX() + "$ $=$ $\\frac{" + volume.LaTeX() +  "}{n_{mole}}$\n$n_{mole}$ $=$ $\\frac{" + volume.LaTeX() + "}{" + molar_volume.LaTeX() + "}$\n$n_{mole}$ $=$ $" + result.LaTeX()

                    solutions.append((sol, result, steps))

    if "ideal gas" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            pressure1 = findValue("Pressure", objects, values)
            volume1 = findValue("Volume", objects, values)
            temperature1 = findValue("Temperature", objects, values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["ideal gas"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            objects2 = objects[:-1]+[2]
            for value in values:
                if value.objects[-1] == 2 and objects2 != value.objects:
                    objects2 = value.objects
                    break

            pressure2 = findValue("Pressure", objects2, values)
            volume2 = findValue("Volume", objects2, values)
            temperature2 = findValue("Temperature", objects2, values)
            number_of_moles2 = findValue("Number of Moles", objects2, values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+["ideal gas"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["ideal gas"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["ideal gas"])):
                sol += find_number_of_moles2[0] + "$\n$"
                number_of_moles2 = find_number_of_moles2[1]
                steps += 1

            if pressure1 and volume1 and temperature1 and pressure2 and volume2 and temperature2 and number_of_moles2:
                a,b,c,d,e,f = False,False,False,False,False, False
                if pressure1.unit != pressure2.unit:
                    if a := (pressure1.unit != "atm"):
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if b := (pressure2.unit != "atm"):
                        if a: sol += "$"
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if volume1.unit != volume2.unit:
                    if c := (volume1.unit != "L"):
                        if a or b: sol += "$"
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if d := (volume2.unit != "L"):
                        if a or b or c: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                if e := (temperature1.unit != "K"):
                    if a or b or c or d: sol += "$"
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if f := (temperature2.unit != "K"):
                    if a or b or c or d or e: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b or c or d or e or f: sol += "\n$"

                steps += 1

                result = Value("Number of Moles", toInt(round((number_of_moles2.value * temperature2.value * pressure1.value * volume1.value)/(pressure2.value * volume2.value * temperature1.value), 2)), "mol", objects)
                sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $k$ $=$ $\\frac{nRT}{PV}$\n$\\therefore \\frac{n_{1}RT_{1}}{P_{1}V_{1}}$ $=$ $\\frac{n_{2}RT_{2}}{P_{2}V_{2}}$\n$\\frac{n_{1} \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}$ $=$ $\\frac{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}$\n$n_{1}$ $=$ $\\frac{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + " \\times " + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() +" \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}$\n$n_{1}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            pressure2 = findValue("Pressure", objects, values)
            volume2 = findValue("Volume", objects, values)
            temperature2 = findValue("Temperature", objects, values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects, "L", exceptions+["ideal gas"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            objects1 = objects[:-1]+[1]
            for value in values:
                if value.objects[-1] == 1 and objects1 != value.objects:
                    objects1 = value.objects
                    break

            pressure1 = findValue("Pressure", objects1, values)
            volume1 = findValue("Volume", objects1, values)
            temperature1 = findValue("Temperature", objects1, values)
            number_of_moles1 = findValue("Number of Moles", objects1, values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects1, "atm", exceptions+["ideal gas"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            if (volume1 is None) and (find_volume1 := Volume(values, objects1, "L", exceptions+["ideal gas"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects1, "K", exceptions+["ideal gas"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects1, exceptions+["ideal gas"])):
                sol += find_number_of_moles1[0] + "$\n$"
                number_of_moles1 = find_number_of_moles1[1]
                steps += 1

            if pressure1 and volume1 and temperature1 and pressure2 and volume2 and temperature2 and number_of_moles1:
                a,b,c,d,e,f = False,False,False,False,False, False
                if pressure1.unit != pressure2.unit:
                    if a := (pressure1.unit != "atm"):
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if b := (pressure2.unit != "atm"):
                        if a: sol += "$"
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if volume1.unit != volume2.unit:
                    if c := (volume1.unit != "L"):
                        if a or b: sol += "$"
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if d := (volume2.unit != "L"):
                        if a or b or c: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                if e := (temperature1.unit != "K"):
                    if a or b or c or d: sol += "$"
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if f := (temperature2.unit != "K"):
                    if a or b or c or d or e: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b or c or d or e or f: sol += "\n$"

                steps += 1

                result = Value("Number of Moles", toInt(round((number_of_moles1.value * temperature1.value * pressure2.value * volume2.value)/(pressure1.value * volume1.value * temperature2.value), 2)), "mol", objects)
                sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $k$ $=$ $\\frac{nRT}{PV}$\n$\\therefore \\frac{n_{1}RT_{1}}{P_{1}V_{1}}$ $=$ $\\frac{n_{2}RT_{2}}{P_{2}V_{2}}$\n$\\frac{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}$ $=$ $\\frac{n_{2} \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}$\n$\\frac{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + " \\times " + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() +" \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}$ $=$ $n_{2}$\n$" + result.LaTeX() + "$ $=$ $n_{2}"

        else:
            pressure = findValue("Pressure", objects, values)
            volume = findValue("Volume", objects, values)
            temperature = findValue("Temperature", objects, values)

            if (pressure is None) and (find_pressure := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                sol += find_pressure[0] + "$\n$"
                pressure = find_pressure[1]
                steps += 1

            if (volume is None) and (find_volume := Volume(values, objects, "L", exceptions+["ideal gas"])):
                sol += find_volume[0] + "$\n$"
                volume = find_volume[1]
                steps += 1

            if (temperature is None) and (find_temperature := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                sol += find_temperature[0] + "$\n$"
                temperature = find_temperature[1]
                steps += 1

            if pressure and volume and temperature:
                if a := (pressure.unit != "atm"):
                    sol += "P$ $=$ $" + pressure.LaTeX() + "$ $=$ $" + (pressure := pressure.in_another_unit("atm")).LaTeX() + "$\n"

                if b := (volume.unit != "L"):
                    if a: sol += "$"
                    sol += "V$ $=$ $" + volume.LaTeX() + "$ $=$ $" + (volume := volume.in_another_unit("L")).LaTeX() + "$\n"
                
                if c := (temperature.unit != "K"):
                    if a or b: sol += "$"
                    sol += "T$ $=$ $" + temperature.LaTeX() + "$ $=$ $" + (temperature := temperature.in_another_unit("K")).LaTeX() + "$\n"

                if a or b or c: sol += "\n$"

                steps += 1

                result = Value("Number of Moles", toInt(round((pressure.value * volume.value) / (0.082 * temperature.value), 2)), "mol", objects)
                sol += "PV$ $=$ $nRT$\n$" + pressure.LaTeX() + " \\times " + volume.LaTeX() + "$ $=$ $n_{mole}\\times 0.082 \\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature.LaTeX() + "$\n$\\frac{" + pressure.LaTeX() + " \\times " + volume.LaTeX() + "}{0.082 \\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature.LaTeX() + "}$ $=$ $n_{mole}$\n$" + result.LaTeX() + "$ $=$ $n_{mole}"

                solutions.append((sol, result, steps))

    if "x=n/n" not in exceptions:
        if objects[-1] == "Partial":
            mole_fraction = findValue("Mole Fraction", objects, values)
            total_number_of_moles = findValue("Number of Moles", [objects[1], "Total"], values)

            if (mole_fraction is None) and (find_mole_fraction := Mole_Fraction(values, objects, exceptions+["x=n/n"])):
                sol += find_mole_fraction[0] + "$\n$"
                mole_fraction = find_mole_fraction[1]
                steps += 1

            if (total_number_of_moles is None) and (find_total_number_of_moles := Number_of_Moles(values, [objects[1], "Total"], exceptions+["x=n/n"])):
                sol += find_total_number_of_moles[0] + "$\n$"
                total_number_of_moles = find_total_number_of_moles[1]
                steps += 1

            if mole_fraction and total_number_of_moles:
                steps += 1

                result = Value("Number of Moles", toInt(round(mole_fraction.value * total_number_of_moles.value, 2)), "mol", objects)
                sol += "x_{element}$ $=\\frac{n_{element}}{n_{T}}$\n$" + mole_fraction.LaTeX() + "$ $=$ $\\frac{n_{" + objects[0] + "}}{" + total_number_of_moles.LaTeX() + "}$\n$" + mole_fraction.LaTeX() + " \\times " + total_number_of_moles.LaTeX() + "$ $=$ $n_{" + objects[0] + "}$\n$" + result.LaTeX() + "$ $=$ $n_{" + objects[0] + "}" 

                solutions.append((sol, result, steps))

        elif objects[-1] == "Total":
            partial_objects = None
            for value in values:
                if value.objects[-2:] == [objects[0], "Partial"]:
                    partial_objects = value.objects

            if partial_objects is not None:
                mole_fraction = findValue("Mole Fraction", partial_objects, values)
                partial_number_of_moles = findValue("Number of Moles", partial_objects, values)

                if (mole_fraction is None) and (find_mole_fraction := Mole_Fraction(values, objects, exceptions+["x=n/n"])):
                    sol += find_mole_fraction[0] + "$\n$"
                    mole_fraction = find_mole_fraction[1]
                    steps += 1

                if (partial_number_of_moles is None) and (find_partial_number_of_moles := Number_of_Moles(values, [objects[1], "Total"], exceptions+["x=n/n"])):
                    sol += find_partial_number_of_moles[0] + "$\n$"
                    partial_number_of_moles = find_partial_number_of_moles[1]
                    steps += 1

                if mole_fraction and partial_number_of_moles:
                    steps += 1

                    result = Value("Number of Moles", toInt(round(partial_number_of_moles.value/mole_fraction.value, 2)), "mol", objects)
                    sol += "x_{element}$ $=\\frac{n_{element}}{n_{T}}$\n$" + mole_fraction.LaTeX() + "$ $=$ $\\frac{" + partial_number_of_moles.LaTeX() + "}{n_{" + objects[0] + "}}$\n$n_{" + objects[0] + "}$ $=$ $\\frac{" + partial_number_of_moles.LaTeX() + "}{" + mole_fraction.LaTeX() + "}$\n$n_{" + objects[0] + "}$ $=$ $" + result.LaTeX()

                    solutions.append((sol, result, steps))

    if len(solutions) == 0:
        return

    elif len(solutions) == 1:
        return solutions[0][:2]

    else:
        return min(solutions, key=lambda x: x[2])[:2]

def Number_of_Particles(values: list[Value], objects: list, exceptions: list[str]=[]):
    sol = ""

    number_of_moles = findValue("Number of Moles", objects, values)

    if (not number_of_moles) and (find_number_of_moles := Number_of_Moles(values, objects, exceptions+["n=n/N"])):
        sol += find_number_of_moles[0] + "$\n$"
        number_of_moles = find_number_of_moles[1]

    if number_of_moles:
        result = Value("Number of Particles", number_of_moles.value*AvogadrosNumber, objects=objects)
        sol += "n_{mole}$ $=$ $\\frac{n_{particle}}{N_{A}}$\n$" + (number_of_moles.value.LaTeX() if type(number_of_moles.value) == Substance else str(number_of_moles.value)) + "$ $=$ $\\frac{n_{particle}}{" + AvogadrosNumber.LaTeX() + "}$\n$" + (number_of_moles.value.LaTeX() if type(number_of_moles.value) == Substance else str(number_of_moles.value)) + "\\times " + AvogadrosNumber.LaTeX() + "$ $=$ $n_{particle}$\n$" + result.LaTeX() + "$ $=$ $n_{particle}"

        return (sol, result)

def Equivalent_Mass(values: list[Value], objects: list, exceptions: list[str]=[]):
    solutions = []

    if "eq=A/valance" not in exceptions:
        sol = ""
        steps = 0

        if type(objects[0]) == Substance:
            atomic_mass = Value("Atomic Mass", objects[0].molarMass, unit="", objects=objects)
            valance = findValue("Valance", objects, values)

            if valance:
                steps += 1

                result = Value("Equivalent Mass", toInt(round(atomic_mass.value/valance.value, 2)), "g", objects)
                sol += "eq$ $=$ $\\frac{Atomic Mass}{Valance}$\n$eq$ $=$ $\\frac{" + atomic_mass.LaTeX() + "}{" + valance.LaTeX() +"}$\n$eq$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

    if "m/eq" not in exceptions:
        if objects[-1] == 1:
            objects2 = None
            for value in values:
                if value.objects[-1] == 2:
                    objects2 = value.objects

            if objects2:
                mass1 = findValue("Mass", objects, values)

                if (mass1 is None) and (find_mass1 := Mass(value, objects, "g", exceptions+["m/eq"])):
                    sol += find_mass1[0] + "$\n$"
                    mass1 = find_mass1[1]
                    steps += 1

                mass2 = findValue("Mass", objects2, values)
                equivalent_mass2 = findValue("Equivalent Mass", objects2, values)

                if (mass2 is None) and (find_mass2 := Mass(values, objects2, "g", exceptions+["m/eq"])):
                    sol += find_mass2[0] + "$\n$"
                    mass2 = find_mass2[1]
                    steps += 1

                if (equivalent_mass2 is None) and (find_equivalent_mass2 := Equivalent_Mass(values, objects2, exceptions+["m/eq"])):
                    sol += find_equivalent_mass2[0] + "$\n$"
                    equivalent_mass2 = find_equivalent_mass2[1]
                    steps += 1

                if mass1 and mass2 and equivalent_mass2:
                    if mass1.unit != mass2.unit:
                        if a := (mass1.unit != "g"):
                            sol += "m_{1}$ $=$ $" + mass1.LaTeX() + "$ $=$ $" + (mass1 := mass1.in_another_unit("g")).LaTeX() + "$\n"

                        if mass2.unit != "g":
                            if a: sol += "$"
                            sol += "m_{2}$ $=$ $" + mass2.LaTeX() + "$ $=$ $" + (mass2 := mass2.in_another_unit("g")).LaTeX() + "$\n"

                        sol += "\n$"

                    steps += 1

                    result = Value("Equivalent Mass", toInt(round((mass1.value * equivalent_mass2.value)/(mass2.value), 2)), "g", objects)
                    sol += "\\frac{m_{1}}{eq_{1}}$ $=$ $\\frac{m_{2}}{eq_{2}}$\n$\\frac{" + mass1.LaTeX() + "}{eq_{1}}$ $=$ $\\frac{" + mass2.LaTeX() + "}{" + equivalent_mass2.LaTeX() + "}$\n$\\frac{" + mass1.LaTeX() + " \\times " + equivalent_mass2.LaTeX() + "}{" + mass2.LaTeX() + "}$ $=$ $eq_{1}$\n$" + result.LaTeX() + "$ $=$ $eq_{1}"

                    solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            objects1 = None
            for value in values:
                if value.objects[-1] == 1:
                    objects1 = value.objects

            if objects1:
                mass2 = findValue("Mass", objects, values)

                if (mass2 is None) and (find_mass2 := Mass(value, objects, "g", exceptions+["m/eq"])):
                    sol += find_mass2[0] + "$\n$"
                    mass2 = find_mass2[1]
                    steps += 1

                mass1 = findValue("Mass", objects1, values)
                equivalent_mass1 = findValue("Equivalent Mass", objects1, values)

                if (mass1 is None) and (find_mass2 := Mass(values, objects1, "g", exceptions+["m/eq"])):
                    sol += find_mass1[0] + "$\n$"
                    mass1 = find_mass1[1]
                    steps += 1

                if (equivalent_mass1 is None) and (find_equivalent_mass1 := Equivalent_Mass(values, objects1, exceptions+["m/eq"])):
                    sol += find_equivalent_mass1[0] + "$\n$"
                    equivalent_mass1 = find_equivalent_mass1[1]
                    steps += 1

                if mass1 and mass2 and equivalent_mass1:
                    if mass1.unit != mass2.unit:
                        if a := (mass1.unit != "g"):
                            sol += "m_{1}$ $=$ $" + mass1.LaTeX() + "$ $=$ $" + (mass1 := mass1.in_another_unit("g")).LaTeX() + "$\n"

                        if mass2.unit != "g":
                            if a: sol += "$"
                            sol += "m_{2}$ $=$ $" + mass2.LaTeX() + "$ $=$ $" + (mass2 := mass2.in_another_unit("g")).LaTeX() + "$\n"

                        sol += "\n$"

                    steps += 1

                    result = Value("Equivalent Mass", toInt(round((mass2.value * equivalent_mass1.value)/(mass1.value), 2)), "g", objects)
                    sol += "\\frac{m_{1}}{eq_{1}}$ $=$ $\\frac{m_{2}}{eq_{2}}$\n$\\frac{" + mass1.LaTeX() + "}{eq_{1}}$ $=$ $\\frac{" + mass2.LaTeX() + "}{" + equivalent_mass2.LaTeX() + "}$\n$\\frac{" + mass1.LaTeX() + " \\times " + equivalent_mass2.LaTeX() + "}{" + mass2.LaTeX() + "}$ $=$ $eq_{1}$\n$" + result.LaTeX() + "$ $=$ $eq_{1}"


                    solutions.append((sol, result, steps))

    if len(solutions) == 0:
        return

    elif len(solutions) == 1:
        return solutions[0][:2]

    else:
        return min(solutions, key=lambda x: x[2])[:2]

def Valance(values: list[Value], objects: list, exceptions: list[str]=[]):
    sol = ""
    if type(objects[0]) == Substance:
        atomic_mass = Value("Atomic Mass", objects[0].molarMass, "", objects)
    
        equivalent_mass = findValue("Equivalent Mass", objects, values)

        if (equivalent_mass is None) and (find_equivalent_mass := Equivalent_Mass(values, objects, exceptions+["eq=A/valance"])):
            sol += find_equivalent_mass[0] + "$\n$"
            equivalent_mass = find_equivalent_mass[1]

        if equivalent_mass:
            result = Value("Equivalent Mass", toInt(round(atomic_mass.value * equivalent_mass.value, 2)), objects=objects)
            sol += "eq$ $=$ $\\frac{Atomic Mass}{Valance}$\n$" + equivalent_mass.LaTeX() + "$ $=$ $\\frac{" + atomic_mass.LaTeX() + "}{Valance}$\n$Valance$ $=$ $\\frac{" + atomic_mass.LaTeX() + "}{" + equivalent_mass.LaTeX() + "}$\n$Valance$ $=$ $" + result.LaTeX()

            return (sol, result)

def Volume(values: list[Value], objects: list, unit: str, exceptions: list[str]=[]):
    solutions = []

    if "density" not in exceptions:
        sol = ""
        steps = 0

        mass = findValue("Mass", objects, values)

        if (mass is None) and (find_mass := Mass(values, objects, "g", exceptions+["density"])):
            sol += find_mass[0] + "$\n$"
            mass = find_mass[1]
            steps += 1

        if mass:
            density = findValue("Density", objects, values)

            if (density is None) and (find_density := Density(values, objects, f"{mass.unit}/{unit}", exceptions+["density"])):
                sol += find_density[0] + "$\n$"
                density = find_density[1]
                steps += 1

            if density:
                if density.unit != f"{mass.unit}/{unit}":
                    sol += "ρ$ $=$ $" + density.LaTeX() + "$ $=$ $" + density.in_another_unit(f"{mass.unit}/{unit}").LaTeX() + "$\n\n$"

                steps += 1

                result = Value("Mass", toInt(round(mass.value / density.value,2)), unit, objects)
                sol += "ρ$ $=$ $\\frac{m}{V}$\n$" + density.LaTeX() + "$ $=$ $\\frac{" + mass.LaTeX() + "}{V}$\n$V$ $=$ $\\frac{" + mass.LaTeX() + "}{" + density.LaTeX() + "}$\n$V$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

    if "PV" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            pressure1 = findValue("Pressure", objects, values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["PV"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            pressure2 = findValue("Pressure", objects[:-1]+[2], values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects[:-1]+[2], "atm", exceptions+["PV"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            volume2 = findValue("Volume", objects[:-1]+[2], values)

            if (volume2 is None) and (find_volume2 := Volume(values, objects[:-1]+[2], unit, exceptions+["PV"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if pressure1 and pressure2 and volume2:
                if pressure1.unit != pressure2.unit:
                    if (a := (pressure1.unit != "atm")):
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if pressure2.unit != "atm":
                        if a: sol += "$"
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                    sol += "\n$"

                steps += 1

                result = Value("Volume", toInt(round((pressure2.value * volume2.value)/pressure1.value, 2)), volume2.unit)
                sol += "P_{1}V_{1}$ $=$ $P_{2}V_{2}$\n$" + pressure1.LaTeX() + " \\times V_{1}$ $=$ $" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "$\n$V_{1}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + pressure1.LaTeX() + "}$\n$V_{1}$ $=$ $" + result.LaTeX()

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$V_{1}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            pressure2 = findValue("Pressure", objects, values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+["PV"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            pressure1 = findValue("Pressure", objects[:-1]+[1], values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects[:-1]+[1], "atm", exceptions+["PV"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            volume1 = findValue("Volume", objects[:-1]+[1], values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects[:-1]+[1], unit, exceptions+["PV"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if pressure1 and pressure2 and volume1:
                if pressure1.unit != pressure2.unit:
                    if a := (pressure1.unit != "atm"):
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if pressure2.unit != "atm":
                        if a: sol += "$"
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                    sol += "\n$"

                steps += 1

                result = Value("Volume", toInt(round((pressure1.value * volume1.value)/pressure2.value, 2)), volume1.unit)
                sol += "P_{1}V_{1}$ $=$ $P_{2}V_{2}$\n$" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "$ $=$ $" + pressure2.LaTeX() + " \\times V_{2}$\n$\\frac{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}{" + pressure2.LaTeX() + "}$ $=$ $V_{2}$\n$" + result.LaTeX() + "$ $=$ $V_{2}"

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $V_{2}"

                solutions.append((sol, result, steps))

    if "V/T" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            temperature1 = findValue("Temperature", objects, values)

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["V/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            temperature2 = findValue("Temperature", objects[:-1]+[2], values)

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects[:-1]+[2], "K", exceptions+["V/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            volume2 = findValue("Volume", objects[:-1]+[2], values)

            if (volume2 is None) and (find_volume2 := Volume(values, objects[:-1]+[2], unit, exceptions+["V/T"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if temperature1 and temperature2 and volume2:
                if a := (temperature1.unit != "K"):
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if b := (temperature2.unit != "K"):
                    if a: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b: sol += "\n$"

                steps += 1

                result = Value("Volume", toInt(round((volume2.value * temperature1.value)/(temperature2.value), 2)), volume2.unit, objects)
                sol += "\\frac{V_{1}}{T_{1}}$ $=$ $\\frac{V_{2}}{T_{2}}$\n$\\frac{V_{1}}{" + temperature1.LaTeX() + "}$ $=$ $\\frac{" + volume2.LaTeX() + "}{" + temperature2.LaTeX() + "}$\n$V_{1}$ $=$ $\\frac{" + volume2.LaTeX() + " \\times " + temperature1.LaTeX() + "}{" + temperature2.LaTeX() + "}$\n$V_{1}$ $=$ $" + result.LaTeX()

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$V_{1}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            temperature2 = findValue("Temperature", objects, values)

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects, "K", exceptions+["V/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            temperature1 = findValue("Temperature", objects[:-1]+[1], values)

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects[:-1]+[1], "K", exceptions+["V/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            volume1 = findValue("Volume", objects[:-1]+[1], values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects[:-1]+[1], unit, exceptions+["V/T"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if temperature1 and temperature2 and volume1:
                if a := (temperature1.unit != "K"):
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if b := (temperature2.unit != "K"):
                    if a: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b: sol += "\n$"

                steps += 1

                result = Value("Volume", toInt(round((volume1.value * temperature2.value)/(temperature1.value), 2)), volume1.unit, objects)
                sol += "\\frac{V_{1}}{T_{1}}$ $=$ $\\frac{V_{2}}{T_{2}}$\n$\\frac{" + volume1.LaTeX() + "}{" + temperature1.LaTeX() + "}$ $=$ $\\frac{V_{2}}{" + temperature2.LaTeX() + "}$\n$\\frac{" + volume1.LaTeX() + " \\times " + temperature2.LaTeX() + "}{" + temperature1.LaTeX() + "}$ $=$ $V_{2}$\n$" + result.LaTeX() + "$ $=$ $" + "V_{2}"

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $V_{2}"

                solutions.append((sol, result, steps))

    if "PV/T" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            pressure1 = findValue("Pressure", objects, values)
            temperature1 = findValue("Temperature", objects, values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["PV/T"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["PV/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            pressure2 = findValue("Pressure", objects[:-1]+[2], values)
            temperature2 = findValue("Temperature", objects[:-1]+[2], values)
            volume2 = findValue("Volume", objects[:-1]+[2], values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects[:-1]+[2], "atm", exceptions+["PV/T"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects[:-1]+[2], "K", exceptions+["PV/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects[:-1]+[2], unit, exceptions+["PV/T"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if pressure1 and temperature1 and pressure2 and temperature2 and volume2:
                a = False
                b = False
                if pressure1.unit != pressure2.unit:
                    if pressure1.unit != "atm":
                        a = True
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if pressure2.unit != "atm":
                        if a: sol += "$"
                        b = True
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if c := (temperature1.unit != "K"):
                    if a or b: sol += "$"
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if d := (temperature2.unit != "K"):
                    if a or b or c: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b or c or d: sol += "\n$"

                steps += 1

                result = Value("Volume", toInt(round((pressure2.value * volume2.value * temperature1.value)/(temperature2.value * pressure1.value), 2)), volume2.unit, objects)
                sol += "\\frac{P_{1}V_{1}}{T_{1}}$ $=$ $\\frac{P_{2}V_{2}}{T_{2}}$\n$\\frac{" + pressure1.LaTeX() + " \\times V_{1}}{" + temperature1.LaTeX() +"}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + temperature2.LaTeX() + "}$\n$V_{1}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + " \\times " + temperature1.LaTeX() + "}{" + temperature2.LaTeX() + " \\times " + pressure1.LaTeX() + "}$\n$V_{1}$ $=$ $" + result.LaTeX()

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$V_{1}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            pressure2 = findValue("Pressure", objects, values)
            temperature2 = findValue("Temperature", objects, values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+["PV/T"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects, "K", exceptions+["PV/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            pressure1 = findValue("Pressure", objects[:-1]+[1], values)
            temperature1 = findValue("Temperature", objects[:-1]+[1], values)
            volume1 = findValue("Volume", objects[:-1]+[1], values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects[:-1]+[1], "atm", exceptions+["PV/T"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects[:-1]+[1], "K", exceptions+["PV/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            if (volume1 is None) and (find_volume1 := Volume(values, objects[:-1]+[1], unit, exceptions+["PV/T"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if pressure1 and temperature1 and volume1 and pressure2 and temperature2:
                a = False
                b = False
                if pressure1.unit != pressure2.unit:
                    if pressure1.unit != "atm":
                        a = True
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if pressure2.unit != "atm":
                        if a: sol += "$"
                        b = True
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if c := (temperature1.unit != "K"):
                    if a or b: sol += "$"
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if d := (temperature2.unit != "K"):
                    if a or b or c: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b or c or d: sol += "\n$"

                steps += 1

                result = Value("Volume", toInt(round((pressure1.value * volume1.value * temperature2.value)/(temperature1.value * pressure2.value), 2)), volume1.unit, objects)
                sol += "\\frac{P_{1}V_{1}}{T_{1}}$ $=$ $\\frac{P_{2}V_{2}}{T_{2}}$\n$\\frac{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}{" + temperature1.LaTeX() + "}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times V_{2}}{" + temperature2.LaTeX() + "}$\n$\\frac{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + " \\times " + temperature2.LaTeX() + "}{" + temperature1.LaTeX() + " \\times " + pressure2.LaTeX() + "}$ $=$ $V_{2}"

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $V_{2}"

                solutions.append((sol, result, steps))

    if "ideal gas" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            number_of_moles1 = findValue("Number of Moles", objects, values)
            pressure1 = findValue("Pressure", objects, values)
            temperature1 = findValue("Temperature", objects, values)

            if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects, exceptions+["ideal gas"])):
                sol += find_number_of_moles1[0] + "$\n$"
                number_of_moles1 = find_number_of_moles1[1]
                steps += 1

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            objects2 = objects[:-1]+[2]
            for value in values:
                if value.objects[-1] == 2 and objects2 != value.objects:
                    objects2 = value.objects
                    break

            pressure2 = findValue("Pressure", objects2, values)
            volume2 = findValue("Volume", objects2, values)
            temperature2 = findValue("Temperature", objects2, values)
            number_of_moles2 = findValue("Number of Moles", objects2, values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+["ideal gas"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["ideal gas"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["ideal gas"])):
                sol += find_number_of_moles2[0] + "$\n$"
                number_of_moles2 = find_number_of_moles2[1]
                steps += 1

            if number_of_moles1 and pressure1 and temperature1 and number_of_moles2 and pressure2 and temperature2 and volume2:
                a,b,c,d,e,f = False,False,False,False,False,False
                if pressure1.unit != pressure2.unit:
                    if a := (pressure1.unit != "atm"):
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if b := (pressure2.unit != "atm"):
                        if a: sol += "$"
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if e := (temperature1.unit != "K"):
                    if a or b: sol += "$"
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if f := (temperature2.unit != "K"):
                    if a or b or e: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b or c or d or e or f: sol += "\n$"

                steps += 1

                result = Value("Volume", toInt(round((pressure2.value * volume2.value * number_of_moles1.value * temperature1.value)/(number_of_moles2.value * temperature2.value * pressure1.value), 2)), volume2.unit, objects)
                sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $\\frac{PV}{nRT}$ $=$ $k$\n$\\therefore \\frac{P_{1}V_{1}}{n_{1}RT_{1}}$ $=$ $\\frac{P_{2}V_{2}}{n_{2}RT_{2}}$\n$\\frac{" + pressure1.LaTeX() + " \\times V_{1}}{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}$\n$V_{1}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + " \\times " + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + " \\times " + pressure1.LaTeX() + "}$\n$V_{1}$ $=$ $" + result.LaTeX()

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$V_{1}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            number_of_moles2 = findValue("Number of Moles", objects, values)
            pressure2 = findValue("Pressure", objects, values)
            temperature2 = findValue("Temperature", objects, values)

            if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects, exceptions+["ideal gas"])):
                sol += find_number_of_moles2[0] + "$\n$"
                number_of_moles2 = find_number_of_moles2[1]
                steps += 1

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            objects1 = objects[:-1]+[1]
            for value in values:
                if value.objects[-1] == 1 and objects1 != value.objects:
                    objects1 = value.objects
                    break

            pressure1 = findValue("Pressure", objects1, values)
            volume1 = findValue("Volume", objects1, values)
            temperature1 = findValue("Temperature", objects1, values)
            number_of_moles1 = findValue("Number of Moles", objects1, values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects1, "atm", exceptions+["ideal gas"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            if (volume1 is None) and (find_volume1 := Volume(values, objects1, "L", exceptions+["ideal gas"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects1, "K", exceptions+["ideal gas"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects1, exceptions+["ideal gas"])):
                sol += find_number_of_moles1[0] + "$\n$"
                number_of_moles1 = find_number_of_moles1[1]
                steps += 1

            if number_of_moles1 and pressure1 and volume1 and temperature1 and pressure2 and temperature2 and number_of_moles2:
                a,b,e,f = False,False,False,False,False, False
                if pressure1.unit != pressure2.unit:
                    if a := (pressure1.unit != "atm"):
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if b := (pressure2.unit != "atm"):
                        if a: sol += "$"
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if e := (temperature1.unit != "K"):
                    if a or b: sol += "$"
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if f := (temperature2.unit != "K"):
                    if a or b or e: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b or e or f: sol += "\n$"

                steps += 1

                result = Value("Volume", toInt(round((pressure1.value * volume1.value * number_of_moles2.value * temperature2.value)/(number_of_moles1.value * temperature1.value * pressure2.value), 2)), volume2.unit, objects)
                sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $\\frac{PV}{nRT}$ $=$ $k$\n$\\therefore \\frac{P_{1}V_{1}}{n_{1}RT_{1}}$ $=$ $\\frac{P_{2}V_{2}}{n_{2}RT_{2}}$\n$\\frac{" + pressure1.LaTeX() + " \\times " + volume1 + "}{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times V_{2}}{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}$\n$\\frac{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + " \\times " + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + " \\times " + pressure2.LaTeX() + "}$ $=$ $V_{2}$\n$" + result.LaTeX() + "$ $=$ $V_{2}"

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $V_{2}"

                solutions.append((sol, result, steps))

        else:
            number_of_moles = findValue("Number of Moles", objects, values)

            if (number_of_moles is None) and (find_number_of_moles := Number_of_Moles(values, objects, exceptions+["ideal gas"])):
                sol += find_number_of_moles[0] + "$\n$"
                number_of_moles = find_number_of_moles[1]
                steps += 1

            pressure = findValue("Pressure", objects, values)

            if (pressure is None) and (find_pressure := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                sol += find_pressure[0] + "$\n$"
                pressure = find_pressure[1]
                steps += 1

            temperature = findValue("Number of Moles", objects, values)

            if (temperature is None) and (find_temperature := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                sol += find_temperature[0] + "$\n$"
                temperature = find_temperature[1]
                steps += 1

    if "molar volume" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            objects2 = None
            for value in values:
                if value.objects[-1] == 2:
                    objects2 = value.objects

            if objects2:
                volume2 = findValue("Volume", objects2, values)

                if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["molar volume"])):
                    sol += find_volume2[0] + "$\n$"
                    volume2 = find_volume2[1]
                    steps += 1

                number_of_moles2 = findValue("Number of Moles", objects2, values)

                if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["molar volume"])):
                    sol += find_number_of_moles2[0] + "$\n$"
                    number_of_moles2 = find_number_of_moles2[1]
                    steps += 1

                number_of_moles1 = findValue("Number of Moles", objects, values)

                if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects, exceptions+["molar volume"])):
                    sol += find_number_of_moles1[0] + "$\n$"
                    number_of_moles1 = find_number_of_moles1[1]
                    steps += 1

                if volume2 and number_of_moles1 and number_of_moles2:
                    steps += 1

                    result = Value("Volume", toInt(round((volume2.value * number_of_moles1.value)/(number_of_moles2.value), 2)), volume2.unit, objects)
                    sol += "\\frac{V_{1}}{n_{1}}$ $=$ $\\frac{V_{2}}{n_{2}}$\n$\\frac{V_{1}}{" + number_of_moles1.LaTeX() + "}$ $=$ $\\frac{" + volume2.LaTeX() + "}{" + number_of_moles2.LaTeX() + "}$\n$V_{1}$ $=$ $\\frac{" + volume2.LaTeX() + " \\times " + number_of_moles1.LaTeX() + "}{" + number_of_moles2.LaTeX() + "}$\n$V_{1}$ $=$ $" + result.LaTeX()

                    if result.unit != unit:
                        result.change_unit(unit)
                        sol += "$\n$V_{1}$ $=$ $" + result.LaTeX()

                    solutions.append((sol, result, steps))
 
        elif objects[-1] == 2:
            objects1 = None
            for value in values:
                if value.objects[-1] == 1:
                    objects1 = value.objects

            if objects1:
                volume1 = findValue("Volume", objects1, values)

                if (volume1 is None) and (find_volume1 := Volume(values, objects1, "L", exceptions+["molar volume"])):
                    sol += find_volume1[0] + "$\n$"
                    volume1 = find_volume1[1]
                    steps += 1

                number_of_moles1 = findValue("Number of Moles", objects1, values)

                if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects1, exceptions+["molar volume"])):
                    sol += find_number_of_moles1[0] + "$\n$"
                    number_of_moles1 = find_number_of_moles1[1]
                    steps += 1

                number_of_moles2 = findValue("Number of Moles", objects, values)

                if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects, exceptions+["molar volume"])):
                    sol += find_number_of_moles2[0] + "$\n$"
                    number_of_moles2 = find_number_of_moles2[1]
                    steps += 1

                if volume1 and number_of_moles1 and number_of_moles2:
                    steps += 1

                    result = Value("Volume", toInt(round((volume1.value * number_of_moles2.value)/(number_of_moles1.value), 2)), volume1.unit, objects)
                    sol += "\\frac{V_{1}}{n_{1}}$ $=$ $\\frac{V_{2}}{n_{2}}$\n$\\frac{" + volume1.LaTeX() + "}{" + number_of_moles1.LaTeX() + "}$ $=$ $\\frac{V_{2}}{" + number_of_moles2.LaTeX() + "}$\n$\\frac{" + volume1.LaTeX() + " \\times " + number_of_moles2.LaTeX() + "}{" + number_of_moles1.LaTeX() + "}$ $=$ $V_{2}$\n$" + result.LaTeX() + "$ $=$ $V_{2}"

                    if result.unit != unit:
                        result.change_unit(unit)
                        sol += "$\n$" + result.LaTeX() + "$ $=$ $V_{2}"

                    solutions.append((sol, result, steps))
 
        else:
            molar_volume = findValue("Molar Volume", objects, values)

            if (molar_volume is None) and (find_molar_volume := Molar_Volume(values, objects, exceptions+["molar volume"])):
                sol += find_molar_volume[0] + "$\n$"
                molar_volume = find_molar_volume[1]
                steps += 1

            if molar_volume:
                number_of_moles = findValue("Number of Moles", objects, values)

                if (not number_of_moles) and (find_number_of_moles := Number_of_Moles(values, objects, exceptions+["molar volume"])):
                    sol += find_number_of_moles[0] + "$\n$"
                    number_of_moles = find_number_of_moles[1]
                    steps += 1

                if number_of_moles:
                    steps += 1

                    result = Value("Volume", toInt(round(molar_volume.value * number_of_moles.value, 2)), "L", objects)
                    sol += "V_{m}$ $=$ $\\frac{V}{n_{mole}}$\n$" + molar_volume.LaTeX() + "$ $=$ $\\frac{V}{" + number_of_moles.LaTeX() + "}$\n$" + molar_volume.LaTeX() + " \\times " + number_of_moles.LaTeX() + "$ $=$ $V$\n$" + result.LaTeX() + "$ $=$ $V"

                    if unit != "L":
                        result.change_unit(unit)
                        sol += "$\n$" + result.LaTeX() + "$ $=$ $V"

                    solutions.append((sol, result, steps))

    if len(solutions) == 0:
        return

    elif len(solutions) == 1:
        return solutions[0][:2]

    else:
        return min(solutions[::-1], key=lambda x: x[2])[:2]

def Temperature(values: list[Value], objects: list, unit: str, exceptions: list[str]=[]):
    solutions = []

    if "P/T" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            pressure1 = findValue("Pressure", objects, values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["P/T"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            pressure2 = findValue("Pressure", objects[:-1]+[2], values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects[:-1]+[2], "atm", exceptions+["P/T"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            temperature2 = findValue("Temperature", objects[:-1]+[2], values)

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects[:-1]+[2], "K", exceptions+["P/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            if pressure1 and pressure2 and temperature2:
                a = False
                b = False
                if pressure1.unit != pressure2.unit:
                    if pressure1.unit != "atm":
                        a = True
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if pressure2.unit != "atm":
                        if a: sol += "$"
                        b = True
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if c := (temperature2.unit != "K"):
                    if a or b: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b or c: sol += "\n$"

                steps += 1

                result = Value("Temperature", toInt(round((pressure1.value * temperature2.value)/ pressure2.value, 2)), "K", objects)
                sol += "\\frac{P_{1}}{T_{1}}$ $=$ $\\frac{P_{2}}{T_{2}}$\n$\\frac{" + pressure1.LaTeX() + "}{T_{1}}$ $=$ $\\frac{" + pressure2.LaTeX() + "}{" + temperature2.LaTeX() + "}$\n$\\frac{" + pressure1.LaTeX() + " \\times " + temperature2.LaTeX() + "}{" + pressure2.LaTeX() + "}$ $=$ $T_{1}$\n$" + result.LaTeX() + "$ $=$ $T_{1}"

                if unit != "K":
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $T_{1}"

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            pressure2 = findValue("Pressure", objects, values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+["P/T"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            pressure1 = findValue("Pressure", objects[:-1]+[1], values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects[:-1]+[1], "atm", exceptions+["P/T"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            temperature1 = findValue("Temperature", objects[:-1]+[1], values)

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects[:-1]+[1], "K", exceptions+["P/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            if pressure1 and pressure2 and temperature1:
                a = False
                b = False
                if pressure1.unit != pressure2.unit:
                    if pressure1.unit != "atm":
                        a = True
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if pressure2.unit != "atm":
                        if a: sol += "$"
                        b = True
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if c := (temperature1.unit != "K"):
                    if a or b: sol += "$"
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if a or b or c: sol += "\n$"

                steps += 1

                result = Value("Temperature", toInt(round((pressure2.value * temperature1.value)/ pressure1.value, 2)), "K", objects)
                sol += "\\frac{P_{1}}{T_{1}}$ $=$ $\\frac{P_{2}}{T_{2}}$\n$\\frac{" + pressure1.LaTeX() + "}{" + temperature1.LaTeX() + "}$ $=$ $\\frac{" + pressure2.LaTeX() + "}{T_{2}}$\n$T_{2}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + temperature1.LaTeX() + "}{" + pressure1.LaTeX() + "}$\n$T_{2}$ $=$ $" + result.LaTeX()

                if unit != "K":
                    result.change_unit(unit)
                    sol += "$\n$T_{2}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

    if "V/T" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            temperature2 = findValue("Temperature", objects[:-1]+[2], values)

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects[:-1]+[2], "K", exceptions+["V/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            volume1 = findValue("Volume", objects, values)
            volume2 = findValue("Volume", objects[:-1]+[2], values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["V/T"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects[:-1]+[2], "L", exceptions+["V/T"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if temperature2 and volume1 and volume2:
                a, b, c = False, False, False
                if a := (temperature2.unit != "K"):
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if volume1.unit != volume2.unit:
                    if b := (volume1.unit != "L"):
                        if a: sol += "$"
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if c := (volume2.unit != "L"):
                        if a or b: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                if a or b or c: sol += "\n$"

                steps += 1

                result = Value("Temperature", toInt(round((volume1.value * temperature2.value) / volume2.value, 2)), "K", objects)
                sol += "\\frac{V_{1}}{T_{1}}$ $=$ $\\frac{V_{2}}{T_{2}}$\n$\\frac{" + volume1.LaTeX() + "}{T_{1}}$ $=$ $\\frac{" + volume2.LaTeX() +"}{" + temperature2.LaTeX() + "}$\n$\\frac{" + volume1.LaTeX() + " \\times " + temperature2.LaTeX() + "}{" + volume2.LaTeX() + "}$ $=$ $T_{1}$\n$" + result.LaTeX() + "$ $=$ $T_{1}"

                if unit != "K":
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $T_{1}"

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            temperature1 = findValue("Temperature", objects[:-1]+[1], values)

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects[:-1]+[1], "K", exceptions+["V/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            volume1 = findValue("Volume", objects[:-1]+[1], values)
            volume2 = findValue("Volume", objects, values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects[:-1]+[1], "L", exceptions+["V/T"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects, "L", exceptions+["V/T"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if temperature1 and volume1 and volume2:
                a, b, c = False, False, False
                if a := (temperature1.unit != "K"):
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if volume1.unit != volume2.unit:
                    if b := (volume1.unit != "L"):
                        if a: sol += "$"
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if c := (volume2.unit != "L"):
                        if a or b: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                if a or b or c: sol += "\n$"

                steps += 1

                result = Value("Temperature", toInt(round((volume2.value * temperature1.value) / volume1.value, 2)), "K", objects)
                sol += "\\frac{V_{1}}{T_{1}}$ $=$ $\\frac{V_{2}}{T_{2}}$\n$\\frac{" + volume1.LaTeX() + "}{" + temperature1.LaTeX() + "}$ $=$ $\\frac{" + volume2.LaTeX() +"}{T_{2}}$\n$T_{2}$ $=$ $\\frac{" + volume2.LaTeX() + " \\times " + temperature1.LaTeX() + "}{" + volume1.LaTeX() + "}$\n$T_{2}$ $=$ $" + result.LaTeX()

                if unit != "K":
                    result.change_unit(unit)
                    sol += "$\n$T_{2}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

    if "PV/T" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            temperature2 = findValue("Temperature", objects[:-1]+[2], values)

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects[:-1]+[2], "K", exceptions+["PV/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            pressure1 = findValue("Pressure", objects, values)
            pressure2 = findValue("Pressure", objects[:-1]+[2], values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["PV/T"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects[:-1]+[2], "atm", exceptions+["PV/T"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            volume1 = findValue("Volume", objects, values)
            volume2 = findValue("Volume", objects[:-1]+[2], values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["PV/T"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects[:-1]+[2], "L", exceptions+["PV/T"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if temperature2 and pressure1 and pressure2 and volume1 and volume2:
                a,b,c,d,e = False, False, False, False, False
                if a := (temperature2.unit != "K"):
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if pressure1.unit != pressure2.unit:
                    if b := (pressure1.unit != "atm"):
                        if a: sol += "$"
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if c := (pressure2.unit != "atm"):
                        if a or b: sol += "$"
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if volume1.unit != volume2.unit:
                    if d := (volume1.unit != "L"):
                        if a or b or c: sol += "$"
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if e := (volume2.unit != "L"):
                        if a or b or c or d: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                if a or b or c or d or e: sol += "\n$"

                steps += 1

                result = Value("Temperature", toInt(round((pressure1.value * volume1.value * temperature2.value) / (pressure2.value * volume2.value), 2)), "K", objects)
                sol += "\\frac{P_{1}V_{1}}{T_{1}}$ $=$ $\\frac{P_{2}V_{2}}{T_{2}}$ $=$ $\\frac{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}{T_{1}}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + temperature2.LaTeX() + "}$ $\n$ $\\frac{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + " \\times " + temperature2.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}$ $=$ $T_{1}$\n$" + result.LaTeX() + "$ $=$ $T_{1}"

                if unit != "K":
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $T_{1}"

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            temperature1 = findValue("Temperature", objects[:-1]+[1], values)

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects[:-1]+[1], "K", exceptions+["PV/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            pressure1 = findValue("Pressure", objects[:-1]+[1], values)
            pressure2 = findValue("Pressure", objects, values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects[:-1]+[1], "atm", exceptions+["PV/T"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+["PV/T"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            volume1 = findValue("Volume", objects[:-1]+[1], values)
            volume2 = findValue("Volume", objects, values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects[:-1]+[1], "L", exceptions+["PV/T"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects, "L", exceptions+["PV/T"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if temperature1 and pressure1 and pressure2 and volume1 and volume2:
                a,b,c,d,e = False, False, False, False, False
                if a := (temperature1.unit != "K"):
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if pressure1.unit != pressure2.unit:
                    if b := (pressure1.unit != "atm"):
                        if a: sol += "$"
                        sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

                    if c := (pressure2.unit != "atm"):
                        if a or b: sol += "$"
                        sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

                if volume1.unit != volume2.unit:
                    if d := (volume1.unit != "L"):
                        if a or b or c: sol += "$"
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if e := (volume2.unit != "L"):
                        if a or b or c or d: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                if a or b or c or d or e: sol += "\n$"

                steps += 1

                result = Value("Temperature", toInt(round((pressure2.value * volume2.value * temperature1.value) / (pressure1.value * volume1.value), 2)), "K", objects)
                sol += "\\frac{P_{1}V_{1}}{T_{1}}$ $=$ $\\frac{P_{2}V_{2}}{T_{2}}$ $=$ $\\frac{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}{" + temperature1.LaTeX() + "}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{T_{2}}$\n$T_{2}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + " \\times " + temperature1.LaTeX() + "}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() +"}$\n$T_{2}$ $=$ $" + result.LaTeX()

                if unit != "K":
                    result.change_unit(unit)
                    sol += "$\n$T_{2}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

    if "ideal gas" not in exceptions:
            sol = ""
            steps = 0

        # if objects[-1] == 1:
        #     number_of_moles1 = findValue("Number of Moles", objects, values)
        #     pressure1 = findValue("Pressure", objects, values)
        #     volume1 = findValue("Volume", objects, values)

        #     if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles1[0] + "$\n$"
        #         number_of_moles1 = find_number_of_moles1[1]
        #         steps += 1

        #     if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure1[0] + "$\n$"
        #         pressure1 = find_pressure1[1]
        #         steps += 1

        #     if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["ideal gas"])):
        #         sol += find_volume1[0] + "$\n$"
        #         volume1 = find_volume1[1]
        #         steps += 1

        #     objects2 = objects[:-1]+[2]
        #     for value in values:
        #         if value.objects[-1] == 2 and objects2 != value.objects:
        #             objects2 = value.objects
        #             break

        #     pressure2 = findValue("Pressure", objects2, values)
        #     volume2 = findValue("Volume", objects2, values)
        #     temperature2 = findValue("Temperature", objects2, values)
        #     number_of_moles2 = findValue("Number of Moles", objects2, values)

        #     if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure2[0] + "$\n$"
        #         pressure2 = find_pressure2[1]
        #         steps += 1

        #     if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["ideal gas"])):
        #         sol += find_volume2[0] + "$\n$"
        #         volume2 = find_volume2[1]
        #         steps += 1

        #     if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature2[0] + "$\n$"
        #         temperature2 = find_temperature2[1]
        #         steps += 1

        #     if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles2[0] + "$\n$"
        #         number_of_moles2 = find_number_of_moles2[1]
        #         steps += 1

        #     if pressure1 and volume1 and number_of_moles1 and pressure2 and volume2 and number_of_moles2 and temperature2:
        #         a,b,c,d,e,f = False,False,False,False,False, False
        #         if pressure1.unit != pressure2.unit:
        #             if a := (pressure1.unit != "atm"):
        #                 sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

        #             if b := (pressure2.unit != "atm"):
        #                 if a: sol += "$"
        #                 sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

        #         if volume1.unit != volume2.unit:
        #             if c := (volume1.unit != "L"):
        #                 if a or b: sol += "$"
        #                 sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

        #             if d := (volume2.unit != "L"):
        #                 if a or b or c: sol += "$"
        #                 sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

        #         if f := (temperature2.unit != "K"):
        #             if a or b or c or d or e: sol += "$"
        #             sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #         if a or b or c or d or e or f: sol += "\n$"

        #         steps += 1

        #         result = Value("Temperature", toInt(round((number_of_moles2.value * temperature2.value * pressure1.value * volume1.value)/(pressure2.value * volume2.value * number_of_moles1.value), 2)), "K", objects)
        #         sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $k$ $=$ $\\frac{nRT}{PV}$\n$\\therefore \\frac{n_{1}RT_{1}}{P_{1}V_{1}}$ $=$ $\\frac{n_{2}RT_{2}}{P_{2}V_{2}}$\n$\\frac{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times T_{1}}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}$ $=$ $\\frac{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}$\n$T_{1}$ $=$ $\\frac{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + " \\times " + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + " \\times " + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K}}$\n$T_{1}$ $=$ $" + result.LaTeX()

        #         if unit != "K":
        #             result.change_unit(unit)
        #             sol += "$\n$T_{1}$ $=$ $" + result.LaTeX()

        #         solutions.append((sol, result, steps))

        #     elif (type(objects[0]) == type(objects2[0]) == Substance) and pressure1 and pressure2 and temperature2:
        #         sol = ""
        #         steps = 0

        #         molar_mass1 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)
        #         molar_mass2 = Value("Molar Mass", objects2[0].molarMass, "g/mol", objects2)

        #         pressure1 = findValue("Pressure", objects, values)

        #         if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
        #             sol += find_pressure1[0] + "$\n$"
        #             pressure1 = find_pressure1[1]
        #             steps += 1

        #         density1 = findValue("Density", objects, values)

        #         if (density1 is None) and (find_density1 := Density(values, objects, "g/L", exceptions+["ideal gas"])):
        #             sol += find_density1[0] + "$\n$"
        #             density1 = find_density1[1]
        #             steps += 1

        #         pressure2 = findValue("Pressure", objects2, values)

        #         if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+["ideal gas"])):
        #             sol += find_pressure2[0] + "$\n$"
        #             pressure2 = find_pressure2[1]
        #             steps += 1

        #         temperature2 = findValue("Temperature", objects2, values)

        #         if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "atm", exceptions+["ideal gas"])):
        #             sol += find_temperature2[0] + "$\n$"
        #             temperature2 = find_temperature2[1]
        #             steps += 1

        #         density2 = findValue("Density", objects2, values)

        #         if (density2 is None) and (find_density2 := Density(values, objects2, "g/L", exceptions+["ideal gas"])):
        #             sol += find_density2[0] + "$\n$"
        #             density2 = find_density2[1]
        #             steps += 1

        #         if pressure1 and pressure2 and temperature2 and density1 and density2:
        #             a,b,c,d,e = False, False, False, False, False
        #             if pressure1.unit != pressure2.unit:
        #                 if a := (pressure1.unit != "atm"):
        #                     sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

        #                 if b := (pressure2.unit != "atm"):
        #                     if a: sol += "$"
        #                     sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

        #             if c := (temperature1.unit != "K"):
        #                 if a or b: sol += "$"
        #                 sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #             if density1.unit != density2.unit:
        #                 if d := (density1.unit != "g/L"):
        #                     if a or b or c: sol += "$"
        #                     sol += "P_{1}$ $=$ $" + density1.LaTeX() + "$ $=$ $" + (pressure1 := density1.in_another_unit("g/L")).LaTeX() + "$\n"

        #                 if e := (density2.unit != "g/L"):
        #                     if a or b or c or d: sol += "$"
        #                     sol += "P_{2}$ $=$ $" + density2.LaTeX() + "$ $=$ $" + (density2 := density2.in_another_unit("g/L")).LaTeX() + "$\n"

        #             if a or b or c or d or e: sol += "\n$"

        #             steps += 1

        #             result = Value("Temperature", toInt(round((density2.value * temperature2.value * pressure1.value * molar_mass1.value)/(pressure2.value * molar_mass2.value * density1.value), 2)), "K", objects)
        #             sol += "PM$ $=$ $ρRT$ $\\Rightarrow$ $k$ $=$ $\\frac{ρRT}{PM}$\n$\\frac{ρ_{1}RT_{1}}{P_{1}M_{1}}$ $=$ $\\frac{ρ_{2}RT_{2}}{P_{2}M_{2}}$\n$\\frac{" + density1.LaTeX() + " \\times 0.082\\frac{atm \\cdot K}{mol \\cdot K} \\times " + temperature1.LaTeX + "}{" + pressure1.LaTeX() + " \\times " + molar_mass1.LaTeX() + "}$ $=$ $\\frac{" + density2.LaTeX() + " \\times 0.082\\frac{atm \\cdot K}{mol \\cdot K} \\times T_{2}}{" + pressure2.LaTeX() + " \\times " + molar_mass2.LaTeX() + "}$\n$T_{1}$ $=$ $\\frac{" + density2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + " \\times " + pressure1.LaTeX() + " \\times" +  molar_mass1.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + molar_mass2.LaTeX() + " \\times " + density1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K}}$ $=$ $T_{2}$\n$" + result.LaTeX() + "$ $=$ $T_{2}"

        #             if unit != "K":
        #                 result.change_unit(unit)
        #                 sol += "$\n$" + result.LaTeX() + "$ $=$ $T_{2}"

        #             solutions.append((sol, result, steps))

        # elif objects[-1] == 2:
        #     number_of_moles2 = findValue("Number of Moles", objects, values)
        #     pressure2 = findValue("Pressure", objects, values)
        #     volume2 = findValue("Volume", objects, values)

        #     if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles2[0] + "$\n$"
        #         number_of_moles2 = find_number_of_moles2[1]
        #         steps += 1

        #     if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure2[0] + "$\n$"
        #         pressure2 = find_pressure2[1]
        #         steps += 1

        #     if (volume2 is None) and (find_volume2 := Volume(values, objects, "L", exceptions+["ideal gas"])):
        #         sol += find_volume2[0] + "$\n$"
        #         volume2 = find_volume2[1]
        #         steps += 1

        #     objects1 = objects[:-1]+[1]
        #     for value in values:
        #         if value.objects[-1] == 1 and objects1 != value.objects:
        #             objects1 = value.objects
        #             break

        #     pressure1 = findValue("Pressure", objects1, values)
        #     volume1 = findValue("Volume", objects1, values)
        #     temperature1 = findValue("Temperature", objects1, values)
        #     number_of_moles1 = findValue("Number of Moles", objects1, values)

        #     if (pressure1 is None) and (find_pressure1 := Pressure(values, objects1, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure1[0] + "$\n$"
        #         pressure1 = find_pressure1[1]
        #         steps += 1

        #     if (volume1 is None) and (find_volume1 := Volume(values, objects1, "L", exceptions+["ideal gas"])):
        #         sol += find_volume1[0] + "$\n$"
        #         volume1 = find_volume1[1]
        #         steps += 1

        #     if (temperature1 is None) and (find_temperature1 := Temperature(values, objects1, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature1[0] + "$\n$"
        #         temperature1 = find_temperature1[1]
        #         steps += 1

        #     if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects1, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles1[0] + "$\n$"
        #         number_of_moles1 = find_number_of_moles1[1]
        #         steps += 1

        #     if pressure1 and volume1 and number_of_moles1 and temperature1 and pressure2 and volume2 and number_of_moles2:
        #         a,b,c,d,e,f = False,False,False,False,False, False
        #         if pressure1.unit != pressure2.unit:
        #             if a := (pressure1.unit != "atm"):
        #                 sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

        #             if b := (pressure2.unit != "atm"):
        #                 if a: sol += "$"
        #                 sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

        #         if volume1.unit != volume2.unit:
        #             if c := (volume1.unit != "L"):
        #                 if a or b: sol += "$"
        #                 sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

        #             if d := (volume2.unit != "L"):
        #                 if a or b or c: sol += "$"
        #                 sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

        #         if f := (temperature1.unit != "K"):
        #             if a or b or c or d or e: sol += "$"
        #             sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #         if a or b or c or d or e or f: sol += "\n$"

        #         steps += 1

        #         result = Value("Temperature", toInt(round((number_of_moles1.value * temperature1.value * pressure2.value * volume2.value)/(pressure1.value * volume1.value * number_of_moles2.value), 2)), "K", objects)
        #         sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $k$ $=$ $\\frac{nRT}{PV}$\n$\\therefore \\frac{n_{1}RT_{1}}{P_{1}V_{1}}$ $=$ $\\frac{n_{2}RT_{2}}{P_{2}V_{2}}$\n$\\frac{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times T_{1}}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}$ $=$ $\\frac{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}$\n$\\frac{" + number_of_moles1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + " \\times " + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + " \\times " + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K}}$ $=$ $T_{2}$\n$" + result.LaTeX() + "$ $=$ $T_{2}"

        #         if unit != "K":
        #             result.change_unit(unit)
        #             sol += "$\n$" + result.LaTeX() + "$ $=$ $T_{2}"

        #         solutions.append((sol, result, steps))

        #     elif (type(objects[0]) == type(objects1[0]) == Substance) and pressure1 and pressure2 and temperature2:
        #         sol = ""
        #         steps = 0

        #         molar_mass1 = Value("Molar Mass", objects1[0].molarMass, "g/mol", objects2)
        #         molar_mass2 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)

        #         pressure2 = findValue("Pressure", objects, values)

        #         if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
        #             sol += find_pressure2[0] + "$\n$"
        #             pressure2 = find_pressure2[1]
        #             steps += 1

        #         density1 = findValue("Density", objects1, values)

        #         if (density1 is None) and (find_density1 := Density(values, objects1, "g/L", exceptions+["ideal gas"])):
        #             sol += find_density1[0] + "$\n$"
        #             density1 = find_density1[1]
        #             steps += 1

        #         pressure2 = findValue("Pressure", objects1, values)

        #         if (pressure1 is None) and (find_pressure1 := Pressure(values, objects1, "atm", exceptions+["ideal gas"])):
        #             sol += find_pressure1[0] + "$\n$"
        #             pressure1 = find_pressure1[1]
        #             steps += 1

        #         temperature1 = findValue("Temperature", objects1, values)

        #         if (temperature1 is None) and (find_temperature1 := Temperature(values, objects1, "atm", exceptions+["ideal gas"])):
        #             sol += find_temperature2[0] + "$\n$"
        #             temperature1 = find_temperature1[1]
        #             steps += 1

        #         density2 = findValue("Density", objects2, values)

        #         if (density1 is None) and (find_density1 := Density(values, objects1, "g/L", exceptions+["ideal gas"])):
        #             sol += find_density1[0] + "$\n$"
        #             density2 = find_density1[1]
        #             steps += 1

        #         if pressure1 and pressure2 and temperature2 and density1 and density2:
        #             a,b,c,d,e = False, False, False, False, False
        #             if pressure1.unit != pressure2.unit:
        #                 if a := (pressure1.unit != "atm"):
        #                     sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

        #                 if b := (pressure2.unit != "atm"):
        #                     if a: sol += "$"
        #                     sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

        #             if c := (temperature2.unit != "K"):
        #                 if a or b: sol += "$"
        #                 sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #             if density1.unit != density2.unit:
        #                 if d := (density1.unit != "g/L"):
        #                     if a or b or c: sol += "$"
        #                     sol += "P_{1}$ $=$ $" + density1.LaTeX() + "$ $=$ $" + (pressure1 := density1.in_another_unit("g/L")).LaTeX() + "$\n"

        #                 if e := (density2.unit != "g/L"):
        #                     if a or b or c or d: sol += "$"
        #                     sol += "P_{2}$ $=$ $" + density2.LaTeX() + "$ $=$ $" + (density2 := density2.in_another_unit("g/L")).LaTeX() + "$\n"

        #             if a or b or c or d or e: sol += "\n$"

        #             steps += 1

        #             result = Value("Temperature", toInt(round((density1.value * temperature1.value * pressure2.value * molar_mass2.value)/(pressure1.value * molar_mass1.value * density2.value), 2)), "K", objects)
        #             sol += "PM$ $=$ $ρRT$ $\\Rightarrow$ $k$ $=$ $\\frac{ρRT}{PM}$\n$\\frac{ρ_{1}RT_{1}}{P_{1}M_{1}}$ $=$ $\\frac{ρ_{2}RT_{2}}{P_{2}M_{2}}$\n$\\frac{" + density1.LaTeX() + " \\times 0.082\\frac{atm \\cdot K}{mol \\cdot K} \\times T_{1}}{" + pressure1.LaTeX() + " \\times " + molar_mass1.LaTeX() + "}$ $=$ $\\frac{" + density2.LaTeX() + " \\times 0.082\\frac{atm \\cdot K}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}{" + pressure2.LaTeX() + " \\times " + molar_mass2.LaTeX() + "}$\n$\\frac{" + density1.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + " \\times " + pressure2.LaTeX() + " \\times" +  molar_mass2.LaTeX() + "}{" + pressure1.LaTeX() + " \\times " + molar_mass1.LaTeX() + " \\times " + density2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K}}$ $=$ $T_{2}$\n$" + result.LaTeX() + "$ $=$ $T_{2}"

        #             if unit != "K":
        #                 result.change_unit(unit)
        #                 sol += "$\n$" + result.LaTeX() + "$ $=$ $T_{2}"

        #             solutions.append((sol, result, steps))

        #else:
            pressure = findValue("Pressure", objects, values)
            volume = findValue("Volume", objects, values)
            number_of_moles = findValue("Number of Moles", objects, values)

            if (pressure is None) and (find_pressure := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                sol += find_pressure[0] + "$\n$"
                pressure = find_pressure[1]
                steps += 1

            if (volume is None) and (find_volume := Volume(values, objects, "L", exceptions+["ideal gas"])):
                sol += find_volume[0] + "$\n$"
                volume = find_volume[1]
                steps += 1

            if (number_of_moles is None) and (find_number_of_moles := Number_of_Moles(values, objects, exceptions+["ideal gas"])):
                sol += find_number_of_moles[0] + "$\n$"
                number_of_moles = find_number_of_moles[1]
                steps += 1

            if pressure and volume and number_of_moles:
                a, b = False, False
                if a := (pressure.unit != "atm"):
                    sol += "P$ $=$ $" + pressure.LaTeX() + "$ $=$ $" + (pressure := pressure.in_another_unit("atm")).LaTeX() + "$\n"

                if b := (volume.unit != "L"):
                    if a: sol += "$"
                    sol += "V$ $=$ $" + volume.LaTeX() + "$ $=$ $" + (volume := volume.in_another_unit("L")).LaTeX() + "$\n"

                if a or b: sol += "\n$"

                steps += 1

                result = Value("Temperature", toInt(round((pressure.value * volume.value)/(number_of_moles.value * 0.082), 2)), "K", objects)
                sol += "PV$ $=$ $nRT$\n$" + pressure.LaTeX() + " \\times " + volume.LaTeX() + "$ $=$ $" + number_of_moles.LaTeX() + " \\times 0.082 \\frac{atm \\cdot L}{mol \\cdot K} \\times T$\n$\\frac{" + pressure.LaTeX() + " \\times " + volume.LaTeX() + "}{" + number_of_moles.LaTeX() + " \\times 0.082 \\frac{atm \\cdot L}{mol \\cdot K}}$ $=$ $T$\n$" + result.LaTeX() + "$ $=$ $T"

                if unit != "K":
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $T"

                solutions.append((sol, result, steps))

            elif pressure is not None and type(objects[0]) == Substance:
                sol = ""
                steps = 0

                molar_mass = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)

                pressure = findValue("Pressure", objects, values)

                if (pressure is None) and (find_pressure := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                    sol += find_pressure[0] + "$\n$"
                    pressure = find_pressure[1]
                    steps += 1

                density = findValue("Denisty", objects, values)

                if (density is None) and (find_density := Density(values, objects, "g/L", exceptions+["ideal gas"])):
                    sol += find_density[0] + "$\n$"
                    density = find_density[1]
                    steps += 1

                if density:
                    if a := (density.unit != "g/L"):
                        sol += "ρ$ $=$ $" + density.LaTeX() + "$ $=$ $" + (density := density.in_another_unit("g/L")).LaTeX() + "$\n"

                    if b := (pressure.unit != "atm"):
                        if a: sol += "$"
                        sol += "P$ $=$ $" + pressure.LaTeX() + "$ $=$ $" + (pressure := pressure.in_another_unit("atm")).LaTeX() + "$\n"

                    if a or b: sol += "\n$"

                    steps += 1

                    result = Value("Temperature", toInt(round((pressure.value * molar_mass.value)/(density.value * 0.082), 2)), "K", objects)
                    sol += "PM$ $=$ $ρRT$\n$" + pressure.LaTeX() + " \\times " + molar_mass.LaTeX() + "$ $=$ $" + density.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times T$\n$\\frac{" + pressure.LaTeX() + " \\times " + molar_mass.LaTeX() + "}{" + density.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K}}$ $=$ $T$\n$" + result.LaTeX() + "$ $=$ $T"

                    if unit != "K":
                        result.change_unit(unit)
                        sol += "$\n$" + result.LaTeX() + "$ $=$ $T"

                    solutions.append((sol, result, steps))

    if len(solutions) == 0:
        return

    elif len(solutions) == 1:
        return solutions[0][:2]

    else:
        return min(solutions[::-1], key=lambda x: x[2])[:2]

def Pressure(values: list[Value], objects: list, unit: str, exceptions: list[str]=[]):
    solutions = []

    if "PV" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            pressure2 = findValue("Pressure", objects[:-1]+[2], values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects[:-1]+[2], "atm", exceptions+["PV"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            volume1 = findValue("Volume", objects, values)
            volume2 = findValue("Volume", objects[:-1]+[2], values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["PV"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects[:-1]+[2], "L", exceptions+["PV"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if pressure2 and volume1 and volume1:
                if volume1.unit != volume2.unit:
                    if a := (volume1.unit != "L"):
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if volume2.unit != "L":
                        if a: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                    sol += "\n$"

                steps += 1

                result = Value("Pressure", toInt(round((pressure2.value * volume2.value)/(volume1.value), 2)), pressure2.unit, objects)
                sol += "P_{1}V_{1}$ $=$ $P_{2}V_{2}$\n$P_{1} \\times " + volume1.LaTeX() + "$ $=$ $" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "$\n$P_{1}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + volume1.LaTeX() + "}$\n$P_{1}$ $=$ $" + result.LaTeX()

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "P_{1}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            pressure1 = findValue("Pressure", objects[:-1]+[1], values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects[:-1]+[1], "atm", exceptions+["PV"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            volume1 = findValue("Volume", objects[:-1]+[1], values)
            volume2 = findValue("Volume", objects, values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects[:-1]+[1], "L", exceptions+["PV"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects, "L", exceptions+["PV"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if pressure1 and volume1 and volume2:
                if volume1.unit != volume2.unit:
                    if a := (volume1.unit != "L"):
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if volume2.unit != "L":
                        if a: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                    sol += "\n$"

                steps += 1

                result = Value("Pressure", toInt(round((pressure1.value * volume1.value)/volume2.value, 2)), pressure1.unit, objects)
                sol += "P_{1}V_{1}$ $=$ $P_{2}V_{2}$\n$" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "$ $=$ $P_{2} \\times " + volume2.LaTeX() + "$\n$\\frac{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + "}{" + volume2.LaTeX() + "}$ $=$ $P_{2}$\n$" + result.LaTeX() + "$ $=$ $P_{2}"

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $P_{2}"

                solutions.append((sol, result, steps))

    if "P/T" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            pressure2 = findValue("Pressure", objects[:-1]+[2], values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects[:-1]+[2], "atm", exceptions+["P/T"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            temperature1 = findValue("Temperature", objects, values)

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["P/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            temperature2 = findValue("Temperature", objects[:-1]+[2], values)

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects[:-1]+[2], "K", exceptions+["P/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            if pressure2 and temperature1 and temperature2:
                if a := (temperature1.unit != "K"):
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if b := (temperature2.unit != "K"):
                    if a: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b: sol += "\n$"

                steps += 1

                result = Value("Pressure", toInt(round((pressure2.value * temperature1.value)/temperature2.value, 2)), pressure2.unit, objects)
                sol += "\\frac{P_{1}}{T_{1}}$ $=$ $\\frac{P_{2}}{T_{2}}$\n$\\frac{P_{1}}{" + temperature1.LaTeX() + "}$ $=$ $\\frac{" + pressure2.LaTeX() + "}{" + temperature2.LaTeX() + "}$\n$P_{1}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + temperature1.LaTeX() + "}{" + temperature2.LaTeX() + "}$\n$P_{1}$ $=$ $" + result.LaTeX()

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$P_{1}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            pressure1 = findValue("Pressure", objects[:-1]+[1], values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects[:-1]+[1], "atm", exceptions+["P/T"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            temperature1 = findValue("Temperature", objects[:-1]+[1], values)

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects[:-1]+[1], "K", exceptions+["P/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            temperature2 = findValue("Temperature", objects, values)

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects, "K", exceptions+["P/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            if pressure1 and temperature1 and temperature2:
                if a := (temperature1.unit != "K"):
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if b := (temperature2.unit != "K"):
                    if a: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if a or b: sol += "\n$"

                steps += 1

                result = Value("Pressure", toInt(round((pressure1.value * temperature2.value)/(temperature1.value),2)), pressure1.unit, objects)
                sol += "\\frac{P_{1}}{T_{1}}$ $=$ $\\frac{P_{2}}{T_{2}}$\n$\\frac{" + pressure1.LaTeX() + "}{" + temperature1.LaTeX() + "}$ $=$ $\\frac{P_{2}}{" + temperature2.LaTeX() + "}$\n$\\frac{" + pressure1.LaTeX() + " \\times " + temperature2.LaTeX() + "}{" + temperature1.LaTeX() + "}$ $=$ $P_{2}$\n$" + result.LaTeX() + "$ $=$ $P_{2}"

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $P_{2}"

                solutions.append((sol, result, steps))

    if "PV/T" not in exceptions:
        sol = ""
        steps = 0

        if objects[-1] == 1:
            pressure2 = findValue("Pressure", objects[:-1]+[2], values)

            if (pressure2 is None) and (find_pressure2 := Pressure(values, objects[:-1]+[2], "atm", exceptions+["PV/T"])):
                sol += find_pressure2[0] + "$\n$"
                pressure2 = find_pressure2[1]
                steps += 1

            volume1 = findValue("Volume", objects, values)
            volume2 = findValue("Volume", objects[:-1]+[2], values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["PV/T"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects[:-1]+[2], "L", exceptions+["PV/T"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            temperature1 = findValue("Temperature", objects, values)

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["PV/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            temperature2 = findValue("Temperature", objects[:-1]+[2], values)

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects[:-1]+[2], "K", exceptions+["PV/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            if pressure2 and volume1 and volume2 and temperature1 and temperature2:
                a,b,c,d = False, False, False, False
                if a := (temperature1.unit != "K"):
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if b := (temperature2.unit != "K"):
                    if a: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if volume1.unit != volume2.unit:
                    if c := (volume1.unit != "L"):
                        if a or b: sol += "$"
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if d := (volume2.unit != "L"):
                        if a or b or c: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                if a or b or c or d: sol += "\n$"

                steps += 1

                result = Value("Pressure", toInt(round((pressure2.value * volume2.value * temperature1.value)/(temperature2.value * volume2.value), 2)), pressure2.unit, objects)
                sol += "\\frac{P_{1}V_{1}}{T_{1}}$ $=$ $\\frac{P_{2}V_{2}}{T_{2}}$\n$\\frac{P_{1} \\times " + volume1.LaTeX() + "}{" + temperature1.LaTeX() +"}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + temperature2.LaTeX() + "}$\n$P_{1}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + " \\times " + temperature1.LaTeX() + "}{" + temperature2.LaTeX() + " \\times " + volume1.LaTeX() + "}$\n$P_{1}$ $=$ $" + result.LaTeX()

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$P_{1}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

        elif objects[-1] == 2:
            pressure1 = findValue("Pressure", objects[:-1]+[1], values)

            if (pressure1 is None) and (find_pressure1 := Pressure(values, objects[:-1]+[1], "atm", exceptions+["PV/T"])):
                sol += find_pressure1[0] + "$\n$"
                pressure1 = find_pressure1[1]
                steps += 1

            temperature1 = findValue("Temperature", objects[:-1]+[1], values)

            if (temperature1 is None) and (find_temperature1 := Temperature(values, objects[:-1]+[1], "K", exceptions+["PV/T"])):
                sol += find_temperature1[0] + "$\n$"
                temperature1 = find_temperature1[1]
                steps += 1

            temperature2 = findValue("Temperature", objects, values)

            if (temperature2 is None) and (find_temperature2 := Temperature(values, objects, "K", exceptions+["PV/T"])):
                sol += find_temperature2[0] + "$\n$"
                temperature2 = find_temperature2[1]
                steps += 1

            volume1 = findValue("Volume", objects[:-1]+[1], values)
            volume2 = findValue("Volume", objects, values)

            if (volume1 is None) and (find_volume1 := Volume(values, objects[:-1]+[1], "L", exceptions+["PV/T"])):
                sol += find_volume1[0] + "$\n$"
                volume1 = find_volume1[1]
                steps += 1

            if (volume2 is None) and (find_volume2 := Volume(values, objects, "L", exceptions+["PV/T"])):
                sol += find_volume2[0] + "$\n$"
                volume2 = find_volume2[1]
                steps += 1

            if pressure1 and volume1 and volume2 and temperature1 and temperature2:
                a,b,c,d = False, False, False, False
                if a := (temperature1.unit != "K"):
                    sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

                if b := (temperature2.unit != "K"):
                    if a: sol += "$"
                    sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

                if volume1.unit != volume2.unit:
                    if c := (volume1.unit != "L"):
                        if a or b: sol += "$"
                        sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

                    if d := (volume2.unit != "L"):
                        if a or b or c: sol += "$"
                        sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

                if a or b or c or d: sol += "\n$"

                steps += 1

                result = Value("Pressure", toInt(round((pressure1.value * volume1.value * temperature2.value)/(temperature1.value * volume2.value), 2)), pressure1.unit, objects)
                sol += "\\frac{P_{1}V_{1}}{T_{1}}$ $=$ $\\frac{P_{2}V_{2}}{T_{2}}$\n$\\frac{" + (pressure1.LaTeX()) + " \\times " + volume1.LaTeX() + "}{" + temperature1.LaTeX() +"}$ $=$ $\\frac{P_{2} \\times " + volume2.LaTeX() + "}{" + temperature2.LaTeX() + "}$\n$\\frac{" + pressure1.LaTeX() + " \\times " + volume1.LaTeX() + " \\times " + temperature2.LaTeX() + "}{" + temperature1.LaTeX() + " \\times " + volume2.LaTeX() + "}$ $=$ $P_{2}$\n$" + result.LaTeX() + "$ $=$ $P_{2}"

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $P_{2}"

                solutions.append((sol, result, steps))

    if "ideal gas" not in exceptions:
            sol = ""
            steps = 0

        # if objects[-1] == 1:
        #     number_of_moles1 = findValue("Number of Moles", objects, values)
        #     volume1 = findValue("Volume", objects, values)
        #     temperature1 = findValue("Temperature", objects, values)

        #     if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles1[0] + "$\n$"
        #         number_of_moles2 = find_number_of_moles1[1]
        #         steps += 1

        #     if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["ideal gas"])):
        #         sol += find_volume1[0] + "$\n$"
        #         volume1 = find_volume1[1]
        #         steps += 1

        #     if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature1[0] + "$\n$"
        #         temperature1 = find_temperature1[1]
        #         steps += 1

        #     objects2 = objects[:-1]+[2]
        #     for value in values:
        #         if value.objects[-1] == 2 and objects2 != value.objects:
        #             objects2 = value.objects
        #             break

        #     pressure2 = findValue("Pressure", objects2, values)
        #     volume2 = findValue("Volume", objects2, values)
        #     temperature2 = findValue("Temperature", objects2, values)
        #     number_of_moles2 = findValue("Number of Moles", objects2, values)

        #     if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure2[0] + "$\n$"
        #         pressure2 = find_pressure2[1]
        #         steps += 1

        #     if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["ideal gas"])):
        #         sol += find_volume2[0] + "$\n$"
        #         volume2 = find_volume2[1]
        #         steps += 1

        #     if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature2[0] + "$\n$"
        #         temperature2 = find_temperature2[1]
        #         steps += 1

        #     if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles2[0] + "$\n$"
        #         number_of_moles2 = find_number_of_moles2[1]
        #         steps += 1

        #     if volume1 and temperature1 and pressure2 and volume2 and temperature2 and number_of_moles2:
        #         a,b,c,d,e,f = False,False,False,False,False, False
        #         if volume1.unit != volume2.unit:
        #             if c := (volume1.unit != "L"):
        #                 sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

        #             if d := (volume2.unit != "L"):
        #                 if a or b or c: sol += "$"
        #                 sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

        #         if e := (temperature1.unit != "K"):
        #             if a or b or c or d: sol += "$"
        #             sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #         if f := (temperature2.unit != "K"):
        #             if a or b or c or d or e: sol += "$"
        #             sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #         if a or b or c or d or e or f: sol += "\n$"

        #         steps += 1

        #         result = Value("Pressure", toInt(round(1, 2)), pressure2.unit, objects)
        #         sol += ""

        #         if result.unit != unit:
        #             result.change_unit(unit)
        #             sol += "$\n$P_{1}$ $=$ $" + result.LaTeX()

        #         solutions.append((sol, result, steps))

        #     elif (type(objects[0]) == type(objects2[0]) == Substance) and temperature1 and temperature2 and pressure2:
        #         sol = ""
        #         steps = 0

        #         molar_mass1 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)
        #         molar_mass2 = Value("Molar Mass", objects2[0].molarMass, "g/mol", objects2)

        #         temperature1 = findValue("Temperature", objects, values)

        #         if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
        #             sol += find_temperature1[0] + "$\n$"
        #             temperature1 = find_temperature1[1]
        #             steps += 1

        #         temperature2 = findValue("Temperature", objects2, values)

        #         if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
        #             sol += find_temperature2[0] + "$\n$"
        #             temperature2 = find_temperature2[1]
        #             steps += 1

        #         pressure2 = findValue("Pressure", objects2, values)

        #         if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, unit, exceptions+["ideal"])):
        #             sol += find_pressure2[0] + "$\n$"
        #             pressure2 = find_pressure2[1]
        #             steps += 1

        #         if temperature1 and temperature2 and pressure2:
        #             if a := (temperature1.unit != "K"):
        #                 sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #             if b := (temperature2.unit != "K"):
        #                 if a: sol += "$"
        #                 sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #             if a or b: sol += "\n$"

        #             steps += 1

        #             result = Value("Pressure", toInt(round(1, 2)), pressure2.unit, objects)
        #             sol += ""

        #             if result.unit != unit:
        #                 result.change_unit(unit)
        #                 sol += "$\n$P_{1}$ $=$ $" + result.LaTeX()

        #             solutions.append((sol, result, steps))

        # elif objects[-1] == 2:
        #     number_of_moles1 = findValue("Number of Moles", objects, values)
        #     volume1 = findValue("Volume", objects, values)
        #     temperature1 = findValue("Temperature", objects, values)

        #     if (number_of_moles1 is None) and (find_number_of_moles1 := Number_of_Moles(values, objects, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles1[0] + "$\n$"
        #         number_of_moles2 = find_number_of_moles1[1]
        #         steps += 1

        #     if (volume1 is None) and (find_volume1 := Volume(values, objects, "L", exceptions+["ideal gas"])):
        #         sol += find_volume1[0] + "$\n$"
        #         volume1 = find_volume1[1]
        #         steps += 1

        #     if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature1[0] + "$\n$"
        #         temperature1 = find_temperature1[1]
        #         steps += 1

        #     objects2 = objects[:-1]+[2]
        #     for value in values:
        #         if value.objects[-1] == 2 and objects2 != value.objects:
        #             objects2 = value.objects
        #             break

        #     pressure2 = findValue("Pressure", objects2, values)
        #     volume2 = findValue("Volume", objects2, values)
        #     temperature2 = findValue("Temperature", objects2, values)
        #     number_of_moles2 = findValue("Number of Moles", objects2, values)

        #     if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure2[0] + "$\n$"
        #         pressure2 = find_pressure2[1]
        #         steps += 1

        #     if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["ideal gas"])):
        #         sol += find_volume2[0] + "$\n$"
        #         volume2 = find_volume2[1]
        #         steps += 1

        #     if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature2[0] + "$\n$"
        #         temperature2 = find_temperature2[1]
        #         steps += 1

        #     if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles2[0] + "$\n$"
        #         number_of_moles2 = find_number_of_moles2[1]
        #         steps += 1

        #     if volume1 and temperature1 and pressure2 and volume2 and temperature2 and number_of_moles2:
        #         a,b,c,d,e,f = False,False,False,False,False, False
        #         if volume1.unit != volume2.unit:
        #             if c := (volume1.unit != "L"):
        #                 sol += "V_{1}$ $=$ $" + volume1.LaTeX() + "$ $=$ $" + (volume1 := volume1.in_another_unit("L")).LaTeX() + "$\n"

        #             if d := (volume2.unit != "L"):
        #                 if a or b or c: sol += "$"
        #                 sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

        #         if e := (temperature1.unit != "K"):
        #             if a or b or c or d: sol += "$"
        #             sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #         if f := (temperature2.unit != "K"):
        #             if a or b or c or d or e: sol += "$"
        #             sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #         if a or b or c or d or e or f: sol += "\n$"

        #         steps += 1

        #         result = Value("Pressure", toInt(round(1, 2)), pressure2.unit, objects)
        #         sol += ""

        #         if result.unit != unit:
        #             result.change_unit(unit)
        #             sol += "$\n$P_{1}$ $=$ $" + result.LaTeX()

        #         solutions.append((sol, result, steps))

        #     elif (type(objects[0]) == type(objects2[0]) == Substance) and temperature1 and temperature2 and pressure1:
        #         sol = ""
        #         steps = 0

        #         molar_mass1 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)
        #         molar_mass2 = Value("Molar Mass", objects2[0].molarMass, "g/mol", objects2)

        #         temperature1 = findValue("Temperature", objects, values)

        #         if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
        #             sol += find_temperature1[0] + "$\n$"
        #             temperature1 = find_temperature1[1]
        #             steps += 1

        #         temperature2 = findValue("Temperature", objects2, values)

        #         if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
        #             sol += find_temperature2[0] + "$\n$"
        #             temperature2 = find_temperature2[1]
        #             steps += 1

        #         pressure2 = findValue("Pressure", objects2, values)

        #         if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, unit, exceptions+["ideal gas"])):
        #             sol += find_pressure2[0] + "$\n$"
        #             pressure2 = find_pressure2[1]
        #             steps += 1

        #         if temperature1 and temperature2 and pressure2:
        #             if a := (temperature1.unit != "K"):
        #                 sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #             if b := (temperature2.unit != "K"):
        #                 if a: sol += "$"
        #                 sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #             if a or b: sol += "\n$"

        #             steps += 1

        #             result = Value("Pressure", toInt(round(1, 2)), pressure2.unit, objects)
        #             sol += ""

        #             if result.unit != unit:
        #                 result.change_unit(unit)
        #                 sol += "$\n$P_{1}$ $=$ $" + result.LaTeX()

        #             solutions.append((sol, result, steps))

        #else:
            volume = findValue("Volume", objects, values)
            number_of_moles = findValue("Number of Moles", objects, values)
            temperature = findValue("Temperature", objects, values)

            if (volume is None) and (find_volume := Volume(values, objects, "L", exceptions+["ideal gas"])):
                sol += find_volume[0] + "$\n$"
                volume = find_volume[1]
                steps += 1

            if (number_of_moles is None) and (find_number_of_moles := Number_of_Moles(values, objects, exceptions+["ideal gas"])):
                sol += find_number_of_moles[0] + "$\n$"
                number_of_moles = find_number_of_moles[1]
                steps += 1

            temperature = findValue("Temperature", objects, values)

            if (temperature is None) and (find_temperature := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                sol += find_temperature[0] + "$\n$"
                temperature = find_temperature[1]
                steps += 1

            if volume and number_of_moles and temperature:
                if a := (volume.unit != "L"):
                    sol += "V$ $=$ $" + volume.LaTeX() + "$ $=$ $" + (volume := volume.in_another_unit("L")).LaTeX() + "$\n"

                if b := (temperature.unit != "K"):
                    if a: sol += "$"
                    sol += "T$ $=$ $" + temperature.LaTeX() + "$ $=$ $" + (temperature := temperature.in_another_unit("K")).LaTeX() + "$\n"

                if a or b: sol += "\n$"

                steps += 1

                result = Value("Pressure", toInt(round((number_of_moles.value * 0.082 * temperature.value)/(volume.value), 2)), "atm", objects)
                sol += "PV$ $=$ $nRT$\n$P \\times " + volume.LaTeX() + "$ $=$ $" + number_of_moles.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature.LaTeX() + "$\n$P$ $=$ $\\frac{" + number_of_moles.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature.LaTeX() + "}{" + volume.LaTeX() + "$\n$P$ $=$ $" + result.LaTeX()

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$P$ $=$ $" + result.LaTeX()

            elif temperature is not None and type(objects[0]) == Substance:
                sol = ""
                steps = 0

                molar_mass = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)

                temperature = findValue("Temperature", objects, values)

                if (temperature is None) and (find_temperature := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                    sol += find_temperature[0] + "$\n$"
                    temperature = find_temperature[1]
                    steps += 1

                density = findValue("Denisty", objects, values)

                if (density is None) and (find_density := Density(values, objects, "g/L", exceptions+["ideal gas"])):
                    sol += find_density[0] + "$\n$"
                    density = find_density[1]
                    steps += 1

                if temperature and density:
                    if a := (density.unit != "g/L"):
                        sol += "ρ$ $=$ $" + density.LaTeX() + "$ $=$ $" + (density := density.in_another_unit("g/L")).LaTeX() + "$\n"

                    if b := (temperature.unit != "K"):
                        if a: sol += "$"
                        sol += "T$ $=$ $" + temperature.LaTeX() + "$ $=$ $" + (temperature := temperature.in_another_unit("K")).LaTeX() + "$\n"

                    if a or b: sol += "\n$"

                    steps += 1

                    result = Value("Pressure", toInt(round((density.value * 0.082 * temperature.value)/(molar_mass.value), 2)), "atm", objects)
                    sol += "PM$ $=$ $ρRT$\n$P \\times " + molar_mass.LaTeX() + "$ $=$ $" + density.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times" + temperature.LaTeX() + "$\n$P$ $=$ $\\frac{" + density.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times" + temperature.LaTeX() + "}{" + molar_mass.LaTeX() + "}$\n$P$ $=$ $" + result.LaTeX()

                    if unit != "atm":
                        result.change_unit(unit)
                        sol += "$\n$P$ $=$ $" + result.LaTeX()

    if "x=P/P" not in exceptions:
        if objects[-1] == "Partial":
            mole_fraction = findValue("Mole Fraction", objects, values)
            total_pressure = findValue("Number of Moles", [objects[1], "Total"], values)

            if (mole_fraction is None) and (find_mole_fraction := Mole_Fraction(values, objects, exceptions+["x=P/P"])):
                sol += find_mole_fraction[0] + "$\n$"
                mole_fraction = find_mole_fraction[1]
                steps += 1

            if (total_pressure is None) and (find_total_pressure := Pressure(values, [objects[1], "Total"], unit, exceptions+["x=P/P"])):
                sol += find_total_pressure[0] + "$\n$"
                total_pressure = find_total_pressure[1]
                steps += 1

            if mole_fraction and total_pressure:
                steps += 1

                result = Value("Pressure", toInt(round(mole_fraction.value * total_pressure.value, 2)), total_pressure.unit, objects)
                sol += "x_{element}$ $=\\frac{P_{element}}{P_{T}}$\n$" + mole_fraction.LaTeX() + "$ $=$ $\\frac{P_{" + objects[0] + "}}{" + total_pressure.LaTeX() + "}$\n$" + mole_fraction.LaTeX() + " \\times " + total_pressure.LaTeX() + "$ $=$ $P_{" + objects[0] + "}$\n$" + result.LaTeX() + "$ $=$ $P_{" + objects[0] + "}" 

                if result.unit != unit:
                    result.change_unit(unit)
                    sol += "$\n$" + result.LaTeX() + "$ $=$ $P_{" + objects[0] + "}"

                solutions.append((sol, result, steps))

        elif objects[-1] == "Total":
            partial_objects = None
            for value in values:
                if value.objects[-2:] == [objects[0], "Partial"]:
                    partial_objects = value.objects

            if partial_objects is not None:
                mole_fraction = findValue("Mole Fraction", partial_objects, values)
                partial_pressure = findValue("Number of Moles", partial_objects, values)

                if (mole_fraction is None) and (find_mole_fraction := Mole_Fraction(values, objects, exceptions+["x=P/P"])):
                    sol += find_mole_fraction[0] + "$\n$"
                    mole_fraction = find_mole_fraction[1]
                    steps += 1

                if (partial_pressure is None) and (find_partial_pressure := Pressure(values, [objects[1], "Total"], unit, exceptions+["x=P/P"])):
                    sol += find_partial_pressure[0] + "$\n$"
                    partial_pressure = find_partial_pressure[1]
                    steps += 1

                if mole_fraction and partial_pressure:
                    steps += 1

                    result = Value("Pressure", toInt(round(partial_pressure.value/mole_fraction.value, 2)), partial_pressure.unit, objects)
                    sol += "x_{element}$ $=\\frac{P_{element}}{P_{T}}$\n$" + mole_fraction.LaTeX() + "$ $=$ $\\frac{" + partial_pressure.LaTeX() + "}{P_{" + objects[0] + "}}$\n$P_{" + objects[0] + "}$ $=$ $\\frac{" + partial_pressure.LaTeX() + "}{" + mole_fraction.LaTeX() + "}$\n$P_{" + objects[0] + "}$ $=$ $" + result.LaTeX()

                    if result.unit != unit:
                        result.change_unit(unit)
                        sol += "$\n$P_{" + objects[0] + "}$ $=$ $" + result.LaTeX()

                    solutions.append((sol, result, steps))

    if len(solutions) == 0:
        return

    elif len(solutions) == 1:
        return solutions[0][:2]

    else:
        return min(solutions[::-1], key=lambda x: x[2])[:2]

def Density(values: list[Value], objects: list, unit: str, exceptions: list[str]=[]):
    solutions = []

    if "denisty" not in exceptions:
        sol = ""
        steps = 0

        mass = findValue("Mass", objects, values)
        volume = findValue("Volume", objects, values)

        if (mass is None) and (find_mass := Mass(values, objects, "g", exceptions+["density"])):
            sol += find_mass[0] + "$\n$"
            mass = find_mass[1]
            steps += 1

        if (volume is None) and (find_volume := Volume(values, objects, "L", exceptions+["density"])):
            sol += find_volume[0] + "$\n$"
            volume = find_volume[1]
            steps += 1

        if mass and volume:
            steps += 1

            result = Value("Density", toInt(round(mass.value / volume.value, 2)), f"{mass.unit}/{volume.unit}", objects)
            sol += "ρ$ $=$ $\\frac{m}{V}$\n$ρ$ $=$ $\\frac{" + mass.LaTeX() + "}{" + volume.LaTeX() + "}$\n$ρ$ $=$ $" + result.LaTeX()

            if result.unit != unit:
                result.change_unit(unit)
                sol += "$\n$ρ$ $=$ $" + result.LaTeX()

            solutions.append((sol, result, steps))

    if "ideal gas" not in exceptions:
            sol = ""
            steps = 0

        # if objects[-1] == 1:
        #     objects2 = None
        #     for value in values:
        #         if value.objects[-1] == 2:
        #             objects2 = value.objects

        #     if objects2 and (type(objects[0]) == type(objects2[0]) == Substance):
        #         molar_mass1 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)
        #         molar_mass2 = Value("Molar Mass", objects2[0].molarMass, "g/mol", objects)

        #         temperature1 = findValue("Temperature", objects, values)
        #         pressure1 = findValue("Pressure", objects, values)

        #         if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+['ideal gas'])):
        #             sol += find_temperature1[0] + "$\n$"
        #             temperature1 = find_temperature1[1]
        #             steps += 1

        #         if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+['ideal gas'])):
        #             sol += find_pressure1[0] + "$\n$"
        #             pressure1 = find_pressure1[1]
        #             steps += 1

        #         temperature2 = findValue("Temperature", objects2, values)
        #         pressure2 = findValue("Pressure", objects2, values)
        #         density2 = findValue("Density", objects2, values)

        #         if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+['ideal gas'])):
        #             sol += find_temperature2[0] + "$\n$"
        #             temperature2 = find_temperature2[1]
        #             steps += 1

        #         if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+['ideal gas'])):
        #             sol += find_pressure2[0] + "$\n$"
        #             pressure2 = find_pressure2[1]
        #             steps += 1

        #         if (density2 is None) and (find_density2 := Density(values, objects, unit, exceptions+["ideal gas"])):
        #             sol += find_density2[0] + "$\n$"
        #             density2 = find_density2[1]
        #             steps += 1

        #         if pressure1 and temperature1 and pressure2 and temperature2 and density2:
        #             a,b,c,d = False, False, False, False
        #             if pressure1.unit != pressure2.unit:
        #                 if a := (pressure1.unit != "atm"):
        #                     sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

        #                 if b := (pressure2.unit != "atm"):
        #                     if a: sol += "$"
        #                     sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

        #             if c := (temperature1.unit != "K"):
        #                 if a or b: sol += "$"
        #                 sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #             if d := (temperature2.unit != "K"):
        #                 if a or b or c: sol += "$"
        #                 sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #             if a or b or c or d: sol += "\n$"

        #             steps += 1

        #             result = Value("Density", toInt(round(1, 2)), density2.unit, objects)
        #             sol += ""

        #             if result.unit != unit:
        #                 result.change_unit(unit)
        #                 sol += "$\n$ρ_{1}$ $=$ $" + result.LaTeX()

        # elif objects[-1] == 2:
        #     objects1 = None
        #     for value in values:
        #         if value.objects[-1] == 1:
        #             objects1 = value.objects

        #     if objects1 and (type(objects[0]) == type(objects1[0]) == Substance):
        #         molar_mass2 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)
        #         molar_mass1 = Value("Molar Mass", objects1[0].molarMass, "g/mol", objects)

        #         temperature2 = findValue("Temperature", objects, values)
        #         pressure2 = findValue("Pressure", objects, values)

        #         if (temperature2 is None) and (find_temperature2 := Temperature(values, objects, "K", exceptions+['ideal gas'])):
        #             sol += find_temperature2[0] + "$\n$"
        #             temperature2 = find_temperature2[1]
        #             steps += 1

        #         if (pressure2 is None) and (find_pressure2 := Pressure(values, objects, "atm", exceptions+['ideal gas'])):
        #             sol += find_pressure2[0] + "$\n$"
        #             pressure2 = find_pressure2[1]
        #             steps += 1

        #         temperature1 = findValue("Temperature", objects1, values)
        #         pressure1 = findValue("Pressure", objects1, values)
        #         density1 = findValue("Density", objects1, values)

        #         if (temperature1 is None) and (find_temperature1 := Temperature(values, objects1, "K", exceptions+['ideal gas'])):
        #             sol += find_temperature1[0] + "$\n$"
        #             temperature1 = find_temperature1[1]
        #             steps += 1

        #         if (pressure1 is None) and (find_pressure1 := Pressure(values, objects1, "atm", exceptions+['ideal gas'])):
        #             sol += find_pressure1[0] + "$\n$"
        #             pressure1 = find_pressure1[1]
        #             steps += 1

        #         if (density1 is None) and (find_density1 := Density(values, objects1, unit, exceptions+["ideal gas"])):
        #             sol += find_density1[0] + "$\n$"
        #             density1 = find_density1[1]
        #             steps += 1

        #         if pressure1 and temperature1 and pressure2 and temperature2 and density1:
        #             a,b,c,d = False, False, False, False
        #             if pressure1.unit != pressure2.unit:
        #                 if a := (pressure1.unit != "atm"):
        #                     sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

        #                 if b := (pressure2.unit != "atm"):
        #                     if a: sol += "$"
        #                     sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

        #             if c := (temperature1.unit != "K"):
        #                 if a or b: sol += "$"
        #                 sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #             if d := (temperature2.unit != "K"):
        #                 if a or b or c: sol += "$"
        #                 sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #             if a or b or c or d: sol += "\n$"

        #             steps += 1

        #             result = Value("Density", toInt(round(1, 2)), density1.unit, objects)
        #             sol += ""

        #             if result.unit != unit:
        #                 result.change_unit(unit)
        #                 sol += "$\n$ρ_{1}$ $=$ $" + result.LaTeX()

        # else:
            if type(objects[0]) == Substance:
                molar_mass = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)

                pressure = findValue("Pressure", objects, values)

                if (pressure is None) and (find_pressure := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                    sol += find_pressure[0] + "$\n$"
                    pressure = find_pressure[1]
                    steps += 1

                temperature = findValue("Temperature", objects, values)

                if (temperature is None) and (find_temperature := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                    sol += find_temperature[0] + "$\n$"
                    temperature = find_temperature[1]
                    steps += 1

                if pressure and temperature:
                    if a := (pressure.unit != "atm"):
                        sol += "P$ $=$ $" + pressure.LaTeX() + "$ $=$ $" + (pressure.in_another_unit("atm")).LaTeX() + "$\n"

                    if b := (temperature.unit != "K"):
                        if a: sol += "$"
                        sol += "T$ $=$ $" + temperature.LaTeX() + "$ $=$ $" + (temperature := temperature.in_another_unit("K")).LaTeX() + "$\n"

                    if a or b: sol += "\n$"

                    steps += 1

                    result = Value("Density", toInt(round((pressure.value * molar_mass.value)/(0.082 * temperature.value), 2)), "g/L", objects)
                    sol = "PM$ $=$ $ρRT$\n$" + pressure.LaTeX() + " \\times " + molar_mass.LaTeX() + "$ $=$ $ρ \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature.LaTeX() + "$\n$\\frac{" + pressure.LaTeX() + " \\times " + molar_mass.LaTeX() + "}{0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature.LaTeX() + "}$ $=$ $ρ$\n$" + result.LaTeX() + "$ $=$ $ρ"

                    if unit != "g/L":
                        result.change_unit(unit)
                        sol += "$\n$" + result.LaTeX() + "$ $=$ $ρ"

                    solutions.append((sol, result, steps))

    # if "diffusion rate" not in exceptions:
    #     sol = ""
    #     steps = 0

    #     if objects[-1] == 1:
    #         objects2 = None
    #         for value in values:
    #             if value.objects[-1] == 2:
    #                 objects2 = value.objects

    #         if objects2:
    #             density2 = findValue("Density", objects2, values)

    #             if density2:
    #                 diffusion_rate1 = findValue("Diffusion Rate", objects, values)
    #                 diffusion_rate2 = findValue("Diffusion Rate", objects2, values)

    #                 if (diffusion_rate1 is None) and (find_diffusion_rate1 := Diffusion_Rate(values, objects, exceptions)):
    #                     sol += find_diffusion_rate1[0] + "$\n$"
    #                     diffusion_rate1 = find_diffusion_rate1[1]

    #                 if (diffusion_rate2 is None) and (find_diffusion_rate2 := Diffusion_Rate(values, objects2, exceptions)):
    #                     sol += find_diffusion_rate2[0] + "$\n$"
    #                     diffusion_rate2 = find_diffusion_rate2[1]

    #                 if diffusion_rate1 and diffusion_rate2:
    #                     result = Value("Density", toInt(round((1, 2)), unit, objects))
    #                     sol += ""
    #                     solutions.append((sol, result, steps))

    #                 else:
    #                     sol = ""
    #                     steps = 0

    #                     diffusion_time1 = findValue("Diffusion Time", objects, values)
    #                     diffusion_time2 = findValue("Diffusion Time", objects2, values)

    #                     if (diffusion_time1 is None) and (find_diffusion_time1 := Diffusion_Time(values, objects, exceptions)):
    #                         sol += find_diffusion_time1[0] + "$\n$"
    #                         diffusion_time1 = find_diffusion_time1[1]

    #                     if (diffusion_time2 is None) and (find_diffusion_time2 := Diffusion_Time(values, objects2, exceptions)):
    #                         sol += find_diffusion_time2[0] + "$\n$"
    #                         diffusion_time2 = find_diffusion_time2[1]

    #                     if diffusion_time1 and diffusion_time2:
    #                         result = Value("Density", toInt(round(1, 2)), unit, objects)
    #                         sol += ""
    #                         solutions.append((sol, result, steps))
                        
    #                     else:
    #                         sol = ""
    #                         steps = 0
                            
    #                         if type(objects[0]) == type(objects2[0]) == Substance:
    #                             molar_mass1 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)
    #                             molar_mass2 = Value("Molar Mass", objects2[0].molarMass, "g/mol", objects2)

    #                             if molar_mass1 and molar_mass2:
    #                                 result = Value("Density", toInt(round(1, 2)), unit, objects)
    #                                 sol += ""
    #                                 solutions.append((sol, result, steps))
                                
    #     elif objects[-1] == 2:
    #         objects2 = None
    #         for value in values:
    #             if value.objects[-1] == 2:
    #                 objects2 = value.objects

    #         if objects2:
    #             density2 = findValue("Density", objects2, values)

    #             if density2:
    #                 diffusion_rate1 = findValue("Diffusion Rate", objects, values)
    #                 diffusion_rate2 = findValue("Diffusion Rate", objects2, values)

    #                 if (diffusion_rate1 is None) and (find_diffusion_rate1 := Diffusion_Rate(values, objects, exceptions)):
    #                     sol += find_diffusion_rate1[0] + "$\n$"
    #                     diffusion_rate1 = find_diffusion_rate1[1]


    #                 if (diffusion_rate2 is None) and (find_diffusion_rate2 := Diffusion_Rate(values, objects2, exceptions)):
    #                     sol += find_diffusion_rate2[0] + "$\n$"
    #                     diffusion_rate2 = find_diffusion_rate2[1]

    #                 if diffusion_rate1 and diffusion_rate2:
    #                     result = Value("Density", toInt(round((1, 2)), unit, objects))
    #                     sol += ""
    #                     solutions.append((sol, result, steps))

    #                 else:
    #                     sol = ""
    #                     steps = 0

    #                     diffusion_time1 = findValue("Diffusion Time", objects, values)
    #                     diffusion_time2 = findValue("Diffusion Time", objects2, values)

    #                     if (diffusion_time1 is None) and (find_diffusion_time1 := Diffusion_Time(values, objects, exceptions)):
    #                         sol += find_diffusion_time1[0] + "$\n$"
    #                         diffusion_time1 = find_diffusion_time1[1]

    #                     if (diffusion_time2 is None) and (find_diffusion_time2 := Diffusion_Time(values, objects2, exceptions)):
    #                         sol += find_diffusion_time2[0] + "$\n$"
    #                         diffusion_time2 = find_diffusion_time2[1]

    #                     if diffusion_time1 and diffusion_time2:
    #                         result = Value("Density", toInt(round(1, 2)), unit, objects)
    #                         sol += ""
    #                         solutions.append((sol, result, steps))
                        
    #                     else:
    #                         sol = ""
    #                         steps = 0
                            
    #                         if type(objects[0]) == type(objects2[0]) == Substance:
    #                             molar_mass1 = Value("Molar Mass", objects[0].molarMass, "g/mol", objects)
    #                             molar_mass2 = Value("Molar Mass", objects2[0].molarMass, "g/mol", objects2)

    #                             if molar_mass1 and molar_mass2:
    #                                 result = Value("Density", toInt(round(1, 2)), unit, objects)
    #                                 sol += ""
    #                                 solutions.append((sol, result, steps))
                                
    if len(solutions) == 0:
        return
    
    elif len(solutions) == 1:
        return solutions[0][:2]
    
    else:
        return min(solutions, key=lambda x: x[2])[:2]

def Molar_Volume(values: list[Value], objects: list, exceptions: list[str]=[]):
    solutions = []

    if "molar volume" not in exceptions:
        sol = ""
        steps = 0

        volume = findValue("Volume", objects, values)

        if (not volume) and (find_volume := Volume(values, objects, "L")):
            sol += find_volume[0] + "$\n$"
            volume = find_volume[1]
            steps += 1

        if volume:
            number_of_moles = findValue("Number of Moles", objects, values)

            if (not number_of_moles) and (find_number_of_moles := Number_of_Moles(values, objects, exceptions+["molar volume"])):
                sol += find_number_of_moles[0] + "$\n$"
                number_of_moles = find_number_of_moles[1]
                steps += 1

            if number_of_moles:
                if volume.unit != "L":
                    sol += "V$ $=$ $" + volume.LaTeX() + "$ $=$ $" + (volume := volume.in_another_unit("L")).LaTeX() + "$\n\n$"

                steps += 1

                result = Value("Molar Volume", toInt(round(volume.value / number_of_moles.value, 2)), "L/mol", objects)
                sol += "V_{m}$ $=$ $\\frac{V}{n_{mole}}$\n$V_{m}$ $=$ $\\frac{" + volume.LaTeX() + "}{" + number_of_moles.LaTeX() + "}$\n$V_{m}$ $=$ $" + result.LaTeX()

                solutions.append((sol, result, steps))

    if "ideal gas" not in exceptions:
            sol = ""
            steps = 0

        # if objects[-1] == 1:
        #     pressure1 = findValue("Pressure", objects, values)
        #     temperature1 = findValue("Temperature", objects, values)

        #     if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure1[0] + "$\n$"
        #         pressure1 = find_pressure1[1]
        #         steps += 1

        #     if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature1[0] + "$\n$"
        #         temperature1 = find_temperature1[1]
        #         steps += 1

        #     objects2 = objects[:-1]+[2]
        #     for value in values:
        #         if value.objects[-1] == 2 and objects2 != value.objects:
        #             objects2 = value.objects
        #             break

        #     pressure2 = findValue("Pressure", objects2, values)
        #     volume2 = findValue("Volume", objects2, values)
        #     temperature2 = findValue("Temperature", objects2, values)
        #     number_of_moles2 = findValue("Number of Moles", objects2, values)

        #     if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure2[0] + "$\n$"
        #         pressure2 = find_pressure2[1]
        #         steps += 1

        #     if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["ideal gas"])):
        #         sol += find_volume2[0] + "$\n$"
        #         volume2 = find_volume2[1]
        #         steps += 1

        #     if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature2[0] + "$\n$"
        #         temperature2 = find_temperature2[1]
        #         steps += 1

        #     if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles2[0] + "$\n$"
        #         number_of_moles2 = find_number_of_moles2[1]
        #         steps += 1

        #     if pressure1 and temperature1 and pressure2 and volume2 and temperature2 and number_of_moles2:
        #         a,b,c,d,e,f = False,False,False,False,False, False
        #         if pressure1.unit != pressure2.unit:
        #             if a := (pressure1.unit != "atm"):
        #                 sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

        #             if b := (pressure2.unit != "atm"):
        #                 if a: sol += "$"
        #                 sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

        #         if d := (volume2.unit != "L"):
        #             if a or b or c: sol += "$"
        #             sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

        #         if e := (temperature1.unit != "K"):
        #             if a or b or c or d: sol += "$"
        #             sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #         if f := (temperature2.unit != "K"):
        #             if a or b or c or d or e: sol += "$"
        #             sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #         if a or b or c or d or e or f: sol += "\n$"

        #         steps += 1

        #         result = Value("Molar Volume", toInt(round((pressure2.value * volume2.value * temperature1.value)/(number_of_moles2.value * temperature2.value * pressure1.value), 2)), "L/mol", objects)
        #         sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $\\frac{PV}{nRT}$ $=$ $k$\n$\\therefore \\frac{P_{1}V_{1}}{n_{1}RT_{1}}$ $=$ $\\frac{P_{2}V_{2}}{n_{2}RT_{2}}$\n$V_{m_{1}} \\times \\frac{P_{1}}{RT_{1}}$ $=$ $\\frac{P_{2}V_{2}}{n_{2}RT_{2}}$\n$V_{m_{1}} \\times \\frac{" + pressure1.LaTeX() + "}{0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}$\n$V_{m_{1}}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + " \\times " + pressure1.LaTeX() + "}$\n$V_{m_{1}}$ $=$ $" + result.LaTeX()

        #         solutions.append((sol, result, steps))

        # elif objects[-1] == 2:
        #     pressure1 = findValue("Pressure", objects, values)
        #     temperature1 = findValue("Temperature", objects, values)

        #     if (pressure1 is None) and (find_pressure1 := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure1[0] + "$\n$"
        #         pressure1 = find_pressure1[1]
        #         steps += 1

        #     if (temperature1 is None) and (find_temperature1 := Temperature(values, objects, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature1[0] + "$\n$"
        #         temperature1 = find_temperature1[1]
        #         steps += 1

        #     objects2 = objects[:-1]+[2]
        #     for value in values:
        #         if value.objects[-1] == 2 and objects2 != value.objects:
        #             objects2 = value.objects
        #             break

        #     pressure2 = findValue("Pressure", objects2, values)
        #     volume2 = findValue("Volume", objects2, values)
        #     temperature2 = findValue("Temperature", objects2, values)
        #     number_of_moles2 = findValue("Number of Moles", objects2, values)

        #     if (pressure2 is None) and (find_pressure2 := Pressure(values, objects2, "atm", exceptions+["ideal gas"])):
        #         sol += find_pressure2[0] + "$\n$"
        #         pressure2 = find_pressure2[1]
        #         steps += 1

        #     if (volume2 is None) and (find_volume2 := Volume(values, objects2, "L", exceptions+["ideal gas"])):
        #         sol += find_volume2[0] + "$\n$"
        #         volume2 = find_volume2[1]
        #         steps += 1

        #     if (temperature2 is None) and (find_temperature2 := Temperature(values, objects2, "K", exceptions+["ideal gas"])):
        #         sol += find_temperature2[0] + "$\n$"
        #         temperature2 = find_temperature2[1]
        #         steps += 1

        #     if (number_of_moles2 is None) and (find_number_of_moles2 := Number_of_Moles(values, objects2, exceptions+["ideal gas"])):
        #         sol += find_number_of_moles2[0] + "$\n$"
        #         number_of_moles2 = find_number_of_moles2[1]
        #         steps += 1

        #     if pressure1 and temperature1 and pressure2 and volume2 and temperature2 and number_of_moles2:
        #         a,b,c,d,e,f = False,False,False,False,False, False
        #         if pressure1.unit != pressure2.unit:
        #             if a := (pressure1.unit != "atm"):
        #                 sol += "P_{1}$ $=$ $" + pressure1.LaTeX() + "$ $=$ $" + (pressure1 := pressure1.in_another_unit("atm")).LaTeX() + "$\n"

        #             if b := (pressure2.unit != "atm"):
        #                 if a: sol += "$"
        #                 sol += "P_{2}$ $=$ $" + pressure2.LaTeX() + "$ $=$ $" + (pressure2 := pressure2.in_another_unit("atm")).LaTeX() + "$\n"

        #         if d := (volume2.unit != "L"):
        #             if a or b or c: sol += "$"
        #             sol += "V_{2}$ $=$ $" + volume2.LaTeX() + "$ $=$ $" + (volume2 := volume2.in_another_unit("L")).LaTeX() + "$\n"

        #         if e := (temperature1.unit != "K"):
        #             if a or b or c or d: sol += "$"
        #             sol += "T_{1}$ $=$ $" + temperature1.LaTeX() + "$ $=$ $" + (temperature1 := temperature1.in_another_unit("K")).LaTeX() + "$\n"

        #         if f := (temperature2.unit != "K"):
        #             if a or b or c or d or e: sol += "$"
        #             sol += "T_{2}$ $=$ $" + temperature2.LaTeX() + "$ $=$ $" + (temperature2 := temperature2.in_another_unit("K")).LaTeX() + "$\n"

        #         if a or b or c or d or e or f: sol += "\n$"

        #         steps += 1

        #         result = Value("Molar Volume", toInt(round((pressure2.value * volume2.value * temperature1.value)/(number_of_moles2.value * temperature2.value * pressure1.value), 2)), "L/mol", objects)
        #         sol += "PV$ $=$ $nRT$ $\\Rightarrow$ $\\frac{PV}{nRT}$ $=$ $k$\n$\\therefore \\frac{P_{1}V_{1}}{n_{1}RT_{1}}$ $=$ $\\frac{P_{2}V_{2}}{n_{2}RT_{2}}$\n$V_{m_{1}} \\times \\frac{P_{1}}{RT_{1}}$ $=$ $\\frac{P_{2}V_{2}}{n_{2}RT_{2}}$\n$V_{m_{1}} \\times \\frac{" + pressure1.LaTeX() + "}{0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + "}{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + "}$\n$V_{m_{1}}$ $=$ $\\frac{" + pressure2.LaTeX() + " \\times " + volume2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature1.LaTeX() + "}{" + number_of_moles2.LaTeX() + " \\times 0.082\\frac{atm \\cdot L}{mol \\cdot K} \\times " + temperature2.LaTeX() + " \\times " + pressure1.LaTeX() + "}$\n$V_{m_{1}}$ $=$ $" + result.LaTeX()

        #         solutions.append((sol, result, steps))

        # else:
            temperature = findValue("Temperature", objects, values)

            if (not temperature) and (find_temperature := Temperature(values, objects, "K", exceptions+["ideal gas"])):
                sol += find_temperature[0] + "$\n$"
                temperature = find_temperature[1]
                steps += 1

            if temperature:
                pressure = findValue("Pressure", objects, values)

                if (not pressure) and (find_pressure := Pressure(values, objects, "atm", exceptions+["ideal gas"])):
                    sol += find_pressure[0] + "$\n$"
                    pressure = find_pressure[1]
                    steps += 1

                if pressure:
                    steps += 1

                    if temperature.unit != "K":
                        sol += "T$ $=$ $" + temperature.LaTeX() + "$ $=$ $" + (temperature := temperature.in_another_unit("K")).LaTeX()
                    
                    if pressure.unit != "atm":
                        sol += "P$ $=$ $" + pressure.LaTeX() + "$ $=$ $" + (pressure := pressure.in_another_unit("atm")).LaTeX()

                    result = Value("Molar Volume", toInt(round(0.082*temperature.value/pressure.value, 2)), "L/mol", objects)
                    sol += "PV$ $=$ $nRT$\n$\\frac{V}{n}$ $=$ $\\frac{RT}{P}$\n$V_{m}$ $=$ $\\frac{0.082\\frac{atm \\cdot L}{mol \\cdot K \\times " + temperature.LaTeX() + "}}{" + pressure.LaTeX() + "}$\n$V_{m}$ $=$ $" + result.LaTeX()

                    solutions.append((sol, result, steps))

    if len(solutions) == 0:
        return

    elif len(solutions) == 1:
        return solutions[0][:2]

    else:
        return min(solutions, key=lambda x: x[2])[:2]

def Mole_Fraction(values: list[Value], objects: list, exceptions: list[str]=[]):
    if len(objects) == 3:
        if "x=n/n" not in exceptions:
            sol = ""

            partial_number_of_moles = findValue("Number of Moles", objects, values)
            total_number_of_moles = findValue("Number of Moles", [objects[1], "Total"], values)

            if (partial_number_of_moles is None) and (find_partial_number_of_moles := Number_of_Moles(values, objects, exceptions+["x=n/n"])):
                sol += find_partial_number_of_moles[0] + "$\n$"
                partial_number_of_moles = find_partial_number_of_moles[1]

            if (total_number_of_moles is None) and (find_total_number_of_moles := Number_of_Moles(values, [objects[1], "Total"], exceptions+["x=n/n"])):
                sol += find_total_number_of_moles[0] + "$\n$"
                total_number_of_moles = find_total_number_of_moles[1]

            if partial_number_of_moles and total_number_of_moles:
                result = Value("Mole Fraction", toInt(round(partial_number_of_moles.value / total_number_of_moles.value, 2)), unit="", objects=objects)
                sol += "x_{" + objects[0] + "}$ $=$ $\\frac{n_{" + objects[0] + "}}{n_{T}}$ $=$ $\\frac{" + partial_number_of_moles.LaTeX() + "}{" + total_number_of_moles.LaTeX() + "}$ $=$ $" + result.LaTeX()
                return (sol, result)

        if "x=P/P" not in exceptions:
            sol = ""

            partial_pressure = findValue("Pressure", objects, values)
            total_pressure = findValue("Pressure", [objects[1], "Total"], values)

            if (partial_pressure is None) and (find_partial_pressure := Pressure(values, objects, "atm", exceptions+["x=P/P"])):
                sol += find_partial_pressure[0] + "$\n$"
                partial_pressure = find_partial_pressure[1]

            if (total_pressure is None) and (find_total_pressure := Pressure(values, [objects[1], "Partial"], "atm", exceptions+["x=P/P"])):
                sol += find_total_pressure[0] + "$\n$"
                total_pressure = find_total_pressure[1]

            if partial_pressure and total_pressure:
                result = Value("Mole Fraction", toInt(round(partial_pressure.value / total_pressure.value, 2)), unit="", objects=objects)
                sol += "x_{" + objects[0] + "}$ $=$ $\\frac{P_{" + objects[0] + "}}{P_{T}}$ $=$ $\\frac{" + partial_pressure.LaTeX() + "}{" + total_pressure.LaTeX() + "}$ $=$ $" + result.LaTeX()
                return (sol, result)

# def Diffusion_Rate(values: list[Value], objects: list, exceptions: list[str]=[]):
#     sol = ""

#     if objects[-1] == 1:
#         objects2 = None
#         for value in values:
#             if value.objects[-1] == 2:
#                 objects2 = value.objects

#         if objects2:
#             diffusion_rate2 = findValue("Diffusion Rate", objects2, values)

#             if diffusion_rate2:
#                 diffusion_time1 = findValue("Diffusion Time", objects, values)
#                 diffusion_time2 = findValue("Diffusion Time", objects2, values)

#                 if (diffusion_time1 is None) and (find_diffusion_time1 := Diffusion_Time(values, objects, exceptions)):
#                     sol += find_diffusion_time1[0] + "$\n$"
#                     diffusion_time1 = find_diffusion_time1[1]

#                 if (diffusion_time2 is None) and (find_diffusion_time2 := Diffusion_Time(values, objects2, exceptions)):
#                     sol += find_diffusion_time2[0] + "$\n$"
#                     diffusion_time2 = find_diffusion_time2[1]

#                 if diffusion_time1 and diffusion_time2:
#                     result = Value("Diffusion Rate", toInt(round(1, 2)), "mL/s", objects)
#                     sol += ""
#                     return (sol, result)
                
#                 sol = ""

#                 density1 = findValue("Density", objects, values)
#                 density2 = findValue("Density", objects2, values)

#                 if (density1 is None) and (find_density1 := Density(values, objects, exceptions)):
#                     sol += find_density1[0] + "$\n$"
#                     density1 = find_density1[1]

#                 if (density2 is None) and (find_density2 := Density(values, objects2, exceptions)):
#                     sol += find_density2[0] + "$\n$"
#                     density2 = find_density2[1]

#                 if density1 and density2:
#                     result = Value("Diffusion Rate", toInt(round(1, 2)), "mL/s", objects)
#                     sol += ""
#                     return (sol, result)
                
#                 sol = ""
                
#                 if type(objects[0]) == type(objects2[0]) == Substance:
#                     molar_mass1 = Value("Molar Mass", objects[0].molarMass, unit="g/mol", objects=[1])
#                     molar_mass2 = Value("Molar Mass", objects2[0].molarMass, unit="g/mol", objects=[2])

#                     if molar_mass1 and molar_mass2:
#                         result = Value("Diffusion Rate", toInt(round(1, 2)), "mL/s", objects)
#                         sol += ""
#                         return (sol, result)
#     elif objects[-1] == 2:
#         objects2 = None
#         for value in values:
#             if value.objects[-1] == 2:
#                 objects2 = value.objects

#         if objects2:
#             diffusion_time2 = findValue("Diffusion Time", objects2, values)

#             if diffusion_time2:
#                 diffusion_rate1 = findValue("Diffusion Rate", objects, values)
#                 diffusion_rate2 = findValue("Diffusion Rate", objects2, values)

#                 if (diffusion_rate1 is None) and (find_diffusion_rate1 := Diffusion_Rate(values, objects, exceptions)):
#                     sol += find_diffusion_rate1[0] + "$\n$"
#                     diffusion_rate1 = find_diffusion_rate1[1]


#                 if (diffusion_rate2 is None) and (find_diffusion_rate2 := Diffusion_Rate(values, objects2, exceptions)):
#                     sol += find_diffusion_rate2[0] + "$\n$"
#                     diffusion_rate2 = find_diffusion_rate2[1]

#                 if diffusion_rate1 and diffusion_rate2:
#                     result = Value("Diffusion Time", toInt(round((diffusion_time2.value * diffusion_rate2.value) / diffusion_rate1.value, 2)), "s", objects)
#                     sol += "\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{1}}}{\\sqrt{ρ_{2}}}$ $=$ $\\frac{\\sqrt{M_{1}}}{\\sqrt{M_{2}}}$\n$\\therefore\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$\n$\\frac{" + diffusion_rate1.LaTeX() + "}{" + diffusion_rate2.LaTeX() + "}$ $=$ $\\frac{" + diffusion_time2.LaTeX() +"}{t_{1}}$\n$t_{1}$ $=$ $\\frac{" + diffusion_time2.LaTeX() + " \\times " + diffusion_rate2.LaTeX() + "}{" + diffusion_rate1.LaTeX() + "}$\n$t_{1}$ $=$ $" + result.LaTeX()
#                     return (sol, result)
                
#                 sol = ""

#                 density1 = findValue("Density", objects, values)
#                 density2 = findValue("Density", objects2, values)

#                 if (density1 is None) and (find_density1 := Density(values, objects, exceptions)):
#                     sol += find_density1[0] + "$\n$"
#                     density1 = find_density1[1]

#                 if (density2 is None) and (find_density2 := Density(values, objects2, exceptions)):
#                     sol += find_density2[0] + "$\n$"
#                     density2 = find_density2[1]

#                 if density1 and density2:
#                     result = Value("Diffusion Time", toInt(round((diffusion_time2.value * math.sqrt(density1.value)) / math.sqrt(density2.value), 2)), "s", objects)
#                     sol += "\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{1}}}{\\sqrt{ρ_{2}}}$ $=$ $\\frac{\\sqrt{M_{1}}}{\\sqrt{M_{2}}}$\n$\\therefore\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{2}}}{\\sqrt{ρ_{1}}}$\n$\\frac{" + diffusion_time2.LaTeX() + "}{t_{1}}$ $=$ $\\frac{\\sqrt{" + density2.LaTeX() + "}}{\\sqrt{" + density1.LaTeX() +"}}$\n$\\frac{\\sqrt{" + density1.LaTeX() + "} \\times " + diffusion_time2.LaTeX() + "}{\\sqrt{" + density2.LaTeX() + "}}$ $=$ $t_{1}$\n$" + result.LaTeX() + "$ $=$ $t_{1}"
#                     return (sol, result)
                
#                 sol = ""
                
#                 if type(objects[0]) == type(objects2[0]) == Substance:
#                     molar_mass1 = Value("Molar Mass", objects[0].molarMass, unit="g/mol", objects=[1])
#                     molar_mass2 = Value("Molar Mass", objects2[0].molarMass, unit="g/mol", objects=[2])

#                     if molar_mass1 and molar_mass2:
#                         result = Value("Diffusion Time", toInt(round((diffusion_time2.value * math.sqrt(molar_mass1.value)) / math.sqrt(molar_mass2.value), 2)), "s", objects)
#                         sol += "\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{1}}}{\\sqrt{ρ_{2}}}$ $=$ $\\frac{\\sqrt{M_{1}}}{\\sqrt{M_{2}}}$\n$\\therefore\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{M_{2}}}{\\sqrt{M_{1}}}$\n$\\frac{" + diffusion_time2.LaTeX() + "}{t_{1}}$ $=$ $\\frac{\\sqrt{" + molar_mass2.LaTeX() + "}}{\\sqrt{" + molar_mass1.LaTeX() +"}}$\n$\\frac{\\sqrt{" + molar_mass1.LaTeX() + "} \\times " + diffusion_time2.LaTeX() + "}{\\sqrt{" + molar_mass2.LaTeX() + "}}$ $=$ $t_{1}$\n$" + result.LaTeX() + "$ $=$ $t_{1}"
#                         return (sol, result)

# def Diffusion_Time(values: list[Value], objects: list, exceptions: list[str]=[]):
#     sol = ""

#     if objects[-1] == 1:
#         objects2 = None
#         for value in values:
#             if value.objects[-1] == 2:
#                 objects2 = value.objects

#         if objects2:
#             diffusion_time2 = findValue("Diffusion Time", objects2, values)

#             if diffusion_time2:
#                 diffusion_rate1 = findValue("Diffusion Rate", objects, values)
#                 diffusion_rate2 = findValue("Diffusion Rate", objects2, values)

#                 if (diffusion_rate1 is None) and (find_diffusion_rate1 := Diffusion_Rate(values, objects, exceptions)):
#                     sol += find_diffusion_rate1[0] + "$\n$"
#                     diffusion_rate1 = find_diffusion_rate1[1]


#                 if (diffusion_rate2 is None) and (find_diffusion_rate2 := Diffusion_Rate(values, objects2, exceptions)):
#                     sol += find_diffusion_rate2[0] + "$\n$"
#                     diffusion_rate2 = find_diffusion_rate2[1]

#                 if diffusion_rate1 and diffusion_rate2:
#                     result = Value("Diffusion Time", toInt(round((diffusion_time2.value * diffusion_rate2.value) / diffusion_rate1.value, 2)), "s", objects)
#                     sol += "\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{1}}}{\\sqrt{ρ_{2}}}$ $=$ $\\frac{\\sqrt{M_{1}}}{\\sqrt{M_{2}}}$\n$\\therefore\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$\n$\\frac{" + diffusion_rate1.LaTeX() + "}{" + diffusion_rate2.LaTeX() + "}$ $=$ $\\frac{" + diffusion_time2.LaTeX() +"}{t_{1}}$\n$t_{1}$ $=$ $\\frac{" + diffusion_time2.LaTeX() + " \\times " + diffusion_rate2.LaTeX() + "}{" + diffusion_rate1.LaTeX() + "}$\n$t_{1}$ $=$ $" + result.LaTeX()
#                     return (sol, result)
                
#                 sol = ""

#                 density1 = findValue("Density", objects, values)
#                 density2 = findValue("Density", objects2, values)

#                 if (density1 is None) and (find_density1 := Density(values, objects, exceptions)):
#                     sol += find_density1[0] + "$\n$"
#                     density1 = find_density1[1]

#                 if (density2 is None) and (find_density2 := Density(values, objects2, exceptions)):
#                     sol += find_density2[0] + "$\n$"
#                     density2 = find_density2[1]

#                 if density1 and density2:
#                     result = Value("Diffusion Time", toInt(round((diffusion_time2.value * math.sqrt(density1.value)) / math.sqrt(density2.value), 2)), "s", objects)
#                     sol += "\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{1}}}{\\sqrt{ρ_{2}}}$ $=$ $\\frac{\\sqrt{M_{1}}}{\\sqrt{M_{2}}}$\n$\\therefore\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{2}}}{\\sqrt{ρ_{1}}}$\n$\\frac{" + diffusion_time2.LaTeX() + "}{t_{1}}$ $=$ $\\frac{\\sqrt{" + density2.LaTeX() + "}}{\\sqrt{" + density1.LaTeX() +"}}$\n$\\frac{\\sqrt{" + density1.LaTeX() + "} \\times " + diffusion_time2.LaTeX() + "}{\\sqrt{" + density2.LaTeX() + "}}$ $=$ $t_{1}$\n$" + result.LaTeX() + "$ $=$ $t_{1}"
#                     return (sol, result)
                
#                 sol = ""
                
#                 if type(objects[0]) == type(objects2[0]) == Substance:
#                     molar_mass1 = Value("Molar Mass", objects[0].molarMass, unit="g/mol", objects=[1])
#                     molar_mass2 = Value("Molar Mass", objects2[0].molarMass, unit="g/mol", objects=[2])

#                     if molar_mass1 and molar_mass2:
#                         result = Value("Diffusion Time", toInt(round((diffusion_time2.value * math.sqrt(molar_mass1.value)) / math.sqrt(molar_mass2.value), 2)), "s", objects)
#                         sol += "\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{1}}}{\\sqrt{ρ_{2}}}$ $=$ $\\frac{\\sqrt{M_{1}}}{\\sqrt{M_{2}}}$\n$\\therefore\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{M_{2}}}{\\sqrt{M_{1}}}$\n$\\frac{" + diffusion_time2.LaTeX() + "}{t_{1}}$ $=$ $\\frac{\\sqrt{" + molar_mass2.LaTeX() + "}}{\\sqrt{" + molar_mass1.LaTeX() +"}}$\n$\\frac{\\sqrt{" + molar_mass1.LaTeX() + "} \\times " + diffusion_time2.LaTeX() + "}{\\sqrt{" + molar_mass2.LaTeX() + "}}$ $=$ $t_{1}$\n$" + result.LaTeX() + "$ $=$ $t_{1}"
#                         return (sol, result)
#     elif objects[-1] == 2:
#         objects1 = None
#         for value in values:
#             if value.objects[-1] == 1:
#                 objects1 = value.objects

#         if objects1:
#             diffusion_time1 = findValue("Diffusion Time", objects1, values)

#             if diffusion_time1:
#                 diffusion_rate1 = findValue("Diffusion Rate", objects1, values)
#                 diffusion_rate2 = findValue("Diffusion Rate", objects, values)

#                 if (diffusion_rate1 is None) and (find_diffusion_rate1 := Diffusion_Rate(values, objects1, exceptions)):
#                     sol += find_diffusion_rate1[0] + "$\n$"
#                     diffusion_rate1 = find_diffusion_rate1[1]


#                 if (diffusion_rate2 is None) and (find_diffusion_rate2 := Diffusion_Rate(values, objects, exceptions)):
#                     sol += find_diffusion_rate2[0] + "$\n$"
#                     diffusion_rate2 = find_diffusion_rate2[1]

#                 if diffusion_rate1 and diffusion_rate2:
#                     result = Value("Diffusion Time", toInt(round((diffusion_time1.value * diffusion_rate1.value) / (diffusion_rate2.value), 2)), "s", objects)
#                     sol += "\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{1}}}{\\sqrt{ρ_{2}}}$ $=$ $\\frac{\\sqrt{M_{1}}}{\\sqrt{M_{2}}}$\n$\\therefore\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$\n$\\frac{" + diffusion_rate1.LaTeX() + "}{" + diffusion_rate2.LaTeX() + "}$ $=$ $\\frac{t_{2}}{" + diffusion_time1.LaTeX() +"}$\n$\\frac{" + diffusion_time1.LaTeX() + " \\times " + diffusion_rate1.LaTeX() + "}{" + diffusion_rate2.LaTeX() + "}$ $=$ $t_{2}$\n$" + result.LaTeX() + "$ $=$ $t_{2}"
#                     return (sol, result)
                
#                 sol = ""

#                 density1 = findValue("Density", objects, values)
#                 density2 = findValue("Density", objects2, values)

#                 if (density1 is None) and (find_density1 := Density(values, objects, exceptions)):
#                     sol += find_density1[0] + "$\n$"
#                     density1 = find_density1[1]

#                 if (density2 is None) and (find_density2 := Density(values, objects2, exceptions)):
#                     sol += find_density2[0] + "$\n$"
#                     density2 = find_density2[1]

#                 if density1 and density2:
#                     result = Value("Diffusion Time", toInt(round((diffusion_time2.value * math.sqrt(density1.value)) / math.sqrt(density2.value), 2)), "s", objects)
#                     sol += "\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{1}}}{\\sqrt{ρ_{2}}}$ $=$ $\\frac{\\sqrt{M_{1}}}{\\sqrt{M_{2}}}$\n$\\therefore\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{2}}}{\\sqrt{ρ_{1}}}$\n$\\frac{" + diffusion_time2.LaTeX() + "}{t_{1}}$ $=$ $\\frac{\\sqrt{" + density2.LaTeX() + "}}{\\sqrt{" + density1.LaTeX() +"}}$\n$\\frac{\\sqrt{" + density1.LaTeX() + "} \\times " + diffusion_time2.LaTeX() + "}{\\sqrt{" + density2.LaTeX() + "}}$ $=$ $t_{1}$\n$" + result.LaTeX() + "$ $=$ $t_{1}"
#                     return (sol, result)
                
#                 sol = ""
                
#                 if type(objects[0]) == type(objects2[0]) == Substance:
#                     molar_mass1 = Value("Molar Mass", objects[0].molarMass, unit="g/mol", objects=[1])
#                     molar_mass2 = Value("Molar Mass", objects2[0].molarMass, unit="g/mol", objects=[2])

#                     if molar_mass1 and molar_mass2:
#                         result = Value("Diffusion Time", toInt(round((diffusion_time2.value * math.sqrt(molar_mass1.value)) / math.sqrt(molar_mass2.value), 2)), "s", objects)
#                         sol += "\\frac{r_{1}}{r_{2}}$ $=$ $\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{ρ_{1}}}{\\sqrt{ρ_{2}}}$ $=$ $\\frac{\\sqrt{M_{1}}}{\\sqrt{M_{2}}}$\n$\\therefore\\frac{t_{2}}{t_{1}}$ $=$ $\\frac{\\sqrt{M_{2}}}{\\sqrt{M_{1}}}$\n$\\frac{" + diffusion_time2.LaTeX() + "}{t_{1}}$ $=$ $\\frac{\\sqrt{" + molar_mass2.LaTeX() + "}}{\\sqrt{" + molar_mass1.LaTeX() +"}}$\n$\\frac{\\sqrt{" + molar_mass1.LaTeX() + "} \\times " + diffusion_time2.LaTeX() + "}{\\sqrt{" + molar_mass2.LaTeX() + "}}$ $=$ $t_{1}$\n$" + result.LaTeX() + "$ $=$ $t_{1}"
#                         return (sol, result)
