from customtkinter import *
from PIL import ImageTk, Image
import os 
import threading
from tkinter import Text , Label, Frame
import tkinter.font as fonts
import Elementer
import matplotlib
from Equations import getFigure
from CTkMessagebox import *
from solution import getSolution
import matplotlib.pyplot as plt
import json

abtUs = '''Al Thura Secondary School for Distinguished Students
4th Prepatory Grade Students

Supervised by: Yassir Alsokhni

Programming Team:
Hussein Alaa Mustafa
Ridha Hassan Hadi

Researching Team:
Sajjad Ali Abduljabber
Ahmed Nazar Jabbar
Haider Mohammed Abdulzahraa

Designers:
Ahmed Yassir Abd
Hussein Maher Abdulsahib'''

# # Original Version (in arabic)
# abtUs = '''ثانوية الذرى للمتميزين 
# طلاب الرابع علمي

# بإشراف: الأستاذ ياسر الصخني

# Programming Team:
# حسين علاء مصطفى
# رضا حسن هادي

# Researching Team:
# سجاد علي عبدالحسين
# أحمد نزار جبار
# حيدر محمد عبدالزهرة

# Designers:
# أحمد ياسر عبد
# حسين ماهر عبدالصاحب'''

quantities_units = {
    "Mass": ["g", "kg", "mg"],
    "Number of Moles": ["mol"],
    "Number of Particles": ["None"], 
    "Equivalent Mass": ["g"],
    "Valance": ["None"],
    "Volume": ["L", "mL", "m³", "cm³"],
    "Temperature": ["K", "°C"],
    "Pressure": ["atm", "Torr", "mmHg", "cmHg", "Pa"],
    "Density": ["g/L", "g/mL", "g/m³", "g/cm³", "kg/L", "kg/mL", "kg/m³", "kg/cm³", "mg/L", "mg/mL", "mg/m³", "mg/cm³", "ppm"],
    "Molar Volume": ["L/mol"],
    "Mole Fraction": ["None"],
    "Diffusion Rate": ["mL/s"],
    "Diffusion Time": ["s"]
}

quantities = ["Volume", "Mass", "Density", "Number of Moles", "Number of Particles", "Pressure", "Temperature", "Valance", "Equivalent Mass" , "Molar Volume", "Mole Fraction"]#, "Diffusion Time", "Diffusion Rate"]

correct_color = '#33FF57'
error_color = '#FF3333'

def quit_root(): threading.Thread(target=root.quit()).start

def NewFrame(): return CTkFrame(root, height=800, width=500)

def view3DModule(element: str): os.system(f'"{path}/DataBase/3D Elements/{element}.glb"')

def validate_input(text):
    if text.count('.') > 1 or any(c not in '0123456789.' for c in text): return False
    return True

def on_entry_click(event):valuesEntery.configure(validate="key", validatecommand=validate_cmd)

def changeFrame(newFrame: CTkFrame):
    frames: list[CTkFrame] = [AboutFrame, HomeFrame, SymbolFrame,AtomicFrame,NameFrame,EquationFrame, problemsFrame]
    frames.remove(newFrame)
    newFrame.place(relx=0.239, rely=0.03, relwidth=0.4 * 1.8, relheight=(0.3999*3) - 0.2688)
    for frame in frames: frame.place_forget()

def FindByName():
    elementrRoot = Elementer.GetElement()
    notFoundImage = elementrRoot._getNotImage()
    elementColor = CTkImage(notFoundImage, size=notFoundImage.size)

    try:
        elname = elementrRoot.getElementByName(element=str(Element.get())).capitalize()

        name.configure(text=f'{elementrRoot.getElementBySymbol(elname)} {elementrRoot.getElementByName(str(Element.get()))}', text_color=correct_color, font=Desired6_font)
        name.place(relx=0.024, rely=0.3004)

        Explan1.place(relx=0.024, rely=0.4244, relheight=.57575, relwidth=0.97575)
        Explan1.configure(state=NORMAL)
        Explan1.delete("1.0", "end")
        Explan1.insert(END, elementrRoot.getElementInfo(element=str(Element.get()).capitalize()) + '\n\n' + elementrRoot.getElementElectroneConfiguration(element=str(Element.get()).lower()))
        Explan1.configure(state=DISABLED)

        elementImageBohr = elementrRoot.getElementImage(Element.get().capitalize())
        elementColor = CTkImage(elementImageBohr, size=elementImageBohr.size)

        elementButtonLabel.configure(image=elementColor)
        elementButtonLabel.place(relx=.5, rely=0.2844, relheight=.77575, relwidth=.57575)

        elementButton.configure(command=lambda: view3DModule(elementrRoot.getElementBySymbol(elname).lower()), state=elementrRoot._get_state())
        elementButton.place(relx=.63, rely=0.7844)

        Explan1.place(relx=0.024, rely=0.4244, relheight=.57575, relwidth=0.47575)
        elementLabel.place_forget()

    except:
        name.configure(text='Error, please Enter the element correctly!', text_color=error_color, font=Desired5_font)
        name.place(relx=0.024, rely=0.3004, )
        Explan1.place_forget()
        elementLabel.configure(image=elementColor)
        elementLabel.place(relx=.05, rely=0.39, relheight=.77575, relwidth=.57575)
        elementButtonLabel.place_forget()
        elementButton.place_forget()

def FindByAtom():
    elementrRoot = Elementer.GetElement()
    AtomicName.configure(text=" ")
    notFoundImage = elementrRoot._getNotImage()
    elementColor = CTkImage(notFoundImage, size=notFoundImage.size)

    try:
        Elementname = elementrRoot.getElementByAtomicNumber(atomic_number=int(AtiomicElement.get()))

        AtomicName.configure(text=f'{Elementname.capitalize()} {elementrRoot.getElementSymbolByName(Elementname.capitalize())}', text_color=correct_color, font=Desired6_font)
        AtomicName.place(relx=0.024, rely=0.3004, )

        Explan2.place(relx=0.024, rely=0.4244, relheight=.57575, relwidth=0.97575)
        Explan2.configure(state=NORMAL)
        Explan2.delete("1.0", "end")
        Explan2.insert(END, elementrRoot.getElementInfo(element=Elementname.lower()) + '\n\n' + elementrRoot.getElementElectroneConfiguration(element=Elementname.lower()))
        Explan2.configure(state=DISABLED)

        elementImageBohr = elementrRoot.getElementImage(Elementname)
        elementColor = CTkImage(elementImageBohr, size=elementImageBohr.size)

        Explan2.place(relx=0.024, rely=0.4244, relheight=.57575, relwidth=0.47575)

        AtomicButtonLabel.configure(image=elementColor)
        AtomicButtonLabel.place(relx=.5, rely=0.2844, relheight=.77575, relwidth=.57575)

        AtomicButton.configure(command=lambda: view3DModule(Elementname.lower()), state=elementrRoot._get_state())
        AtomicButton.place(relx=.63, rely=0.7844)

        AtomicLabel.place_forget()

    except:
        AtomicName.configure(text='Error, please enter the atomic number correctly!', text_color=error_color, font=Desired5_font)

        AtomicName.place(relx=0.024, rely=0.3004)

        AtomicLabel.configure(image=elementColor)
        AtomicLabel.place(relx=.05, rely=0.39, relheight=.77575, relwidth=.57575)

        Explan2.place_forget()
        AtomicButtonLabel.place_forget()
        AtomicButton.place_forget()

def FindBySymbol():
    elementrRoot = Elementer.GetElement()
    SYMBOLName.configure(text=" ")
    notFoundImage = elementrRoot._getNotImage()
    elementColor = CTkImage(notFoundImage, size=notFoundImage.size)

    try:
        SYMBOL_name = elementrRoot.getElementBySymbol(symbol=SYMBOLElement.get())

        SYMBOLName.configure(text=f'{SYMBOL_name} {SYMBOLElement.get()}', text_color=correct_color, font=Desired6_font)
        SYMBOLName.place(relx=0.024, rely=0.3004, )

        Explan3.place(relx=0.024, rely=0.4244, relheight=.57575, relwidth=0.97575)
        Explan3.configure(state=NORMAL)
        Explan3.delete("1.0", "end")
        Explan3.insert(END, elementrRoot.getElementInfo(element=SYMBOL_name.lower()) + '\n\n' + elementrRoot.getElementElectroneConfiguration(element=SYMBOL_name.lower()))
        Explan3.configure(state=DISABLED)

        image = elementrRoot.getElementImage(SYMBOL_name)
        elementColor = CTkImage(image, size=image.size)
        SYMBOLButtonLabel.configure(image=elementColor)
        SYMBOLButtonLabel.place(relx=.5, rely=0.2844, relheight=.77575, relwidth=.57575)

        Explan3.place(relx=0.024, rely=0.4244, relheight=.57575, relwidth=0.47575)

        SYMBOLButton.configure(command=lambda: view3DModule(SYMBOL_name.lower()), state=elementrRoot._get_state())
        SYMBOLButton.place(relx=.63, rely=0.7844)

        SYMBOLLabel.place_forget()

    except:
        SYMBOLName.configure(text="Error, please enter the element's symbol correctly!", text_color=error_color, font=Desired5_font)
        SYMBOLName.place(relx=0.024, rely=0.3004, )

        SYMBOLLabel.configure(image=elementColor)
        SYMBOLLabel.place(relx=.05, rely=0.39, relheight=.77575, relwidth=.57575)

        Explan2.place_forget()
        SYMBOLButtonLabel.place_forget()
        SYMBOLButton.place_forget()
        
def showEquation():
    global EquationOutput
    if "EquationOutput" in globals(): EquationOutput.destroy()

    if figure := getFigure(ElementsInput.get()):
        EquationOutput = Label(EquationFrame, background="#2b2b2b")
        EquationOutput.place(relx=0.024, rely=0.3004,)

        canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(figure, master=EquationOutput)
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        canvas._tkcanvas.pack(fill="both", expand=True, side="top")

    else:
        EquationOutput = CTkLabel(EquationFrame, text='Sorry, Something Was Wrong!\nMake Sure You Entered The Elements Correctly.', text_color=error_color, font=Desired_font)
        EquationOutput.place(relx=0.19, rely=0.3004)

def toInt(number):
    if number == int(number): number = int(number)
    return number

def get_sol():
    with open(path+"\\DataBase\\values.json",'r+',encoding="utf8") as file:
        file.truncate(0)
        data = {
            "order":[],
            "count":0,
            "count_required":0
        }
        json.dump(data,file,indent=4)

    widgets = givenValuesFrame.winfo_children()
    values = []

    for i in widgets:
        for w in i.winfo_children():
            if w.cget('text') != "X":
                values.append(w.cget('text').split(':'))

    for index, value in enumerate(values):
        quan = value[0]
        val = value[1].split('in')[1].split()[0]
        unit = value[1].split('in')[1].split()[1].replace("None", "")
        obj = value[2]

        with open(path+"\\DataBase\\values.json",'r+',encoding="utf8") as file:
                JSON_FILE = json.load(file)
                count = int(JSON_FILE["count"]) + 1

                data = {f"value{count}": {"Quantity":quan, "Value":val, "Unit":unit, "Object":obj}}

                JSON_FILE.update(data)
                JSON_FILE["count"] = count
                JSON_FILE["order"].append(f'value{count}')

                file.seek(0)
                json.dump(JSON_FILE,file,indent=4)

        values[index] = [quan, toInt(float(val)), unit, obj]
            
    widgets2 = requiredValuesFrameBar.winfo_children()
    requireds = []

    for i in widgets2:
        for w in i.winfo_children():
            if w.cget('text') != "X":
                requireds.append(w.cget('text').split(':'))

    for index, require in enumerate(requireds):
        quan2 = require[0]
        unit2 = require[1].replace(" in ", "").replace("None", "")
        obj2 = require[2]

        with open(path+"\\DataBase\\values.json",'r+',encoding="utf8") as file:
            JSON_FILE = json.load(file)
            count2 = int(JSON_FILE["count_required"]) + 1

            data = {f"required{count2}": {"Quantity":quan2, "Unit":unit2, "Object":obj2}}

            JSON_FILE.update(data)
            JSON_FILE["count_required"] = count2
            JSON_FILE["order"].append(f'required{count2}')

            file.seek(0)
            json.dump(JSON_FILE,file,indent=4)

        requireds[index] = [quan2, unit2, obj2]

    figure = plt.figure()
    ax = figure.add_subplot(111)

    ax.text(0, 0, f"${getSolution(values, requireds)}$", fontsize=36)

    figure.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    plt.show()

def addValues():
    if quantityMenuButton.get() == "Quantity" or not valuesEntery.get() or   unitsMenuButton.get() == "Unit" or not objectsEntery.get():CTkMessagebox(title="Error", message='Please enter a useful value!',icon='cancel', font=Desired2_font)
    else:frame = CTkFrame(givenValuesFrame,width=300,height=65);frame.pack(padx=5,pady=10, fill=X);CTkLabel(frame,text=f'{quantityMenuButton.get()}: in {valuesEntery.get()} {unitsMenuButton.get()}: {objectsEntery.get()}',font=Desired2_font).pack(side=LEFT,padx=10,pady=5);CTkButton(frame,fg_color=error_color,hover_color='#eb4034',text="X",font=Desired2_font,width=50,command=lambda: frame.destroy()).pack(side=RIGHT, padx=10,pady=5)

def addValues2():
    if quantityMenuButton2.get() == "Quantity"  or   unitsMenuButton2.get() == "Unit" or not objectsEntery2.get():CTkMessagebox(title="Error", message='Please enter a useful value!',icon='cancel', font=Desired2_font)
    else:frame = CTkFrame(requiredValuesFrameBar,width=300,height=65);frame.pack(padx=5,pady=10, fill=X);CTkLabel(frame,text=f'{quantityMenuButton2.get()}: in {unitsMenuButton2.get()}: {objectsEntery2.get()}',font=Desired2_font).pack(side=LEFT,padx=10,pady=5);CTkButton(frame,fg_color=error_color,hover_color='#eb4034',text="X",font=Desired2_font,width=50,command=lambda: frame.destroy()).pack(side=RIGHT, padx=10,pady=5)

def unit_quant(choice):
    units = quantities_units[choice]
    unitsMenuButton.configure(state=ACTIVE, values=units)
    unitsMenuButton.set(units[0])

def unit_quant2(choice):
    units = quantities_units[choice]
    unitsMenuButton2.configure(state=ACTIVE, values=units)
    unitsMenuButton2.set(units[0])

path = os.path.dirname(__file__)
root = CTk()
root.title('Arduichemistry 002')
root.protocol("WM_DELETE_WINDOW", quit_root)
root.geometry('1100x600+150+50')
root.minsize(width=1050, height=600)

validate_cmd = (root.register(validate_input), '%P')

img = ImageTk.PhotoImage(Image.open(path+'\\DataBase\\widgets images\\Chmicon.ico'))
root.after(200, lambda: root.iconphoto(False,img))

Desired_font = CTkFont(family="Comic Sans MS", size=30,)
Desired2_font = CTkFont(family="Comic Sans MS", size=20,)
Desired3_font = CTkFont(family="Comic Sans MS", size=50,)
Desired4_font = CTkFont(family="Comic Sans MS", size=50,)
Desired5_font = CTkFont(family="Comic Sans MS", size=35,)
Desired6_font = CTkFont(family="Comic Sans MS", size=40,)

HomeFrame = CTkFrame(root, height=800, width=500)
HomeFrame.place(relx=0.239, rely=0.03, relwidth=0.4 * 1.8, relheight=(0.3999*3) - 0.2688)

MenuFrame = CTkFrame(root, corner_radius=4, height=3000, width=100)
MenuFrame.place(relx=.0, rely=.0, relwidth=.2001)

AboutFrame = CTkFrame(root, height=800, width=500)

HomesButton = CTkButton(MenuFrame, corner_radius=7, text='Find Element', font=Desired2_font, height=40, width=140, command=lambda: changeFrame(HomeFrame))
HomesButton.place(relx=0.06666, rely=0.011, relheight=.017, relwidth=.87575)

AboutButton = CTkButton(MenuFrame, corner_radius=7, text='About Us', font=Desired2_font, height=60, width=140, command=lambda: changeFrame(AboutFrame))
AboutButton.place(relx=0.06666, rely=0.061+0.025, relheight=.017, relwidth=.87575)

AButton = CTkButton(MenuFrame, corner_radius=7, text='Chemical Problems', font=CTkFont(family="Comic Sans MS", size=20,), height=40, width=140, command=lambda: changeFrame(problemsFrame))
AButton.place(relx=0.06666, rely=0.061, relheight=.017, relwidth=.87575)

CEQButton = CTkButton(MenuFrame, corner_radius=7, text='Chemical Equations', font=Desired2_font, height=40, width=140, command=lambda: changeFrame(EquationFrame))
CEQButton.place(relx=0.06666, rely=0.036, relheight=.017, relwidth=.87575)

_f = fonts.Font(family="Courier", size=40, weight='bold')
AbtUsText = Text(AboutFrame, height=10,font=_f,  width=50, foreground='silver',  background='#2b2b2b', bd=0, border=0, borderwidth=0)

AbtUsText.place(relx=0.024, rely=0.0244, relheight=.97575, relwidth=0.99575)
AbtUsText.delete("1.0", "end")
AbtUsText.insert(END,abtUs)
AbtUsText.configure(state=DISABLED)

NameFrame = CTkFrame(root, height=800, width=500)

Element = CTkEntry(NameFrame, font=Desired2_font, height=50, width=5000, placeholder_text="Element Name")
Element.place(relx=0.05, rely=.0474, relwidth=0.887575)

name = CTkLabel(NameFrame, text=' '*30, text_color="silver")

Explan1 = Text(NameFrame, font=fonts.Font(family="Comic Sans MS", size=20, ), height=10, width=50, foreground='silver',  background='#2b2b2b', bd=0, border=0, borderwidth=0)

elementLabel = CTkLabel(NameFrame, text='', bg_color='#2b2b2b')

elementButtonLabel = CTkLabel(NameFrame, text='', bg_color='#2b2b2b')
elementButton = CTkButton(NameFrame, text='View 3D Model', font=Desired_font, width=300)

NFB = CTkButton(NameFrame,  corner_radius=7, text='Find', font=Desired_font, height=40, width=5000, command=FindByName)
NFB.place(relx=0.05004, rely=0.159, relheight=.117, relwidth=.887575)

AtomicFrame = CTkFrame(root, height=800, width=500)
AtiomicElement = CTkEntry(AtomicFrame, font=Desired2_font, height=50, width=5000, placeholder_text="Element's Atomic Number")
AtiomicElement.place(relx=0.05, rely=.0474, relwidth=0.887575)

Explan2 = Text(AtomicFrame, font=fonts.Font(family="Comic Sans MS", size=20, ), height=10, width=50, foreground='silver',  background='#2b2b2b', bd=0, border=0, borderwidth=0)
AtomicName = CTkLabel(AtomicFrame, text_color="silver", font=Desired3_font)
AtomicLabel = CTkLabel(AtomicFrame, text='', bg_color='#2b2b2b')
AtomicButtonLabel = CTkLabel(AtomicFrame, text='', bg_color='#2b2b2b')
AtomicButton = CTkButton(AtomicFrame, text='View 3D Model', font=Desired_font, width=300)

AFB = CTkButton(AtomicFrame,  corner_radius=7, text='Find', font=Desired_font, height=40, width=5000, command=FindByAtom)
AFB.place(relx=0.05004, rely=0.159, relheight=.117, relwidth=.887575)

SymbolFrame = CTkFrame(root, height=800, width=500)

SYMBOLElement = CTkEntry(SymbolFrame, font=Desired2_font, height=50, width=5000, placeholder_text="Element Symbol")
SYMBOLElement.place(relx=0.05, rely=.0474, relwidth=0.887575)

SYMBOLName = CTkLabel(SymbolFrame, text_color="silver", font=Desired3_font)

Explan3 = Text(SymbolFrame, font=fonts.Font(family="Comic Sans MS", size=20, ), height=10, width=50, foreground='silver',  background='#2b2b2b', bd=0, border=0, borderwidth=0)

SYMBOLLabel = CTkLabel(SymbolFrame, text='', bg_color='#2b2b2b')
SYMBOLButtonLabel = CTkLabel(SymbolFrame, text='', bg_color='#2b2b2b')
SYMBOLButton = CTkButton(SymbolFrame, text='View 3D Model', font=Desired_font, width=300)

SFB = CTkButton(SymbolFrame,  corner_radius=7, text='Find', font=Desired_font, height=40, width=5000, command=FindBySymbol)
SFB.place(relx=0.05004, rely=0.159, relheight=.117, relwidth=.887575)

byName = CTkButton(HomeFrame,  corner_radius=7, text='Find Element by its Name ', font=Desired_font, height=40, width=5000, command=lambda: changeFrame(NameFrame))
byName.place(relx=0.02334, rely=0.039, relheight=.117, relwidth=.887575)

byAtomicNumber = CTkButton(HomeFrame,  corner_radius=7, text="Find Element by its Atomic Number", font=Desired_font, height=40, width=5000, command=lambda: changeFrame(AtomicFrame))
byAtomicNumber.place(relx=0.02334, rely=0.039 + 0.18, relheight=0.117, relwidth=.887575)

bySymbol = CTkButton(HomeFrame,  corner_radius=7, text="Find Element by its Symbol", font=Desired_font, height=40, width=5000, command=lambda: changeFrame(SymbolFrame))
bySymbol.place(relx=0.02334, rely=0.039+0.18*2, relheight=0.117, relwidth=.887575)

EquationFrame = CTkFrame(root, height=800, width=500)

CEQButton = CTkButton(MenuFrame, corner_radius=7, text='Chemical Equations', font=Desired2_font, height=40, width=140, command=lambda: changeFrame(EquationFrame))
CEQButton.place(relx=0.06666, rely=0.036, relheight=.017, relwidth=.87575)

ElementsInput = CTkEntry(EquationFrame, font=Desired2_font, height=50, width=5000, placeholder_text="Reactants, such as: Na + Cl2")
ElementsInput.place(relx=0.05, rely=.0474, relwidth=0.887575)

EQFB = CTkButton(EquationFrame,  corner_radius=7, text='Find', font=Desired_font, height=40, width=5000, command=showEquation)
EQFB.place(relx=0.05004, rely=0.159, relheight=.117, relwidth=.887575)

problemsFrame = CTkFrame(root, height=800, width=500, fg_color='#2b2b2b')

valuesFrame = CTkFrame(problemsFrame,width=300,height=50,fg_color='#242424')
valuesFrame.place(relx=0.05004, rely=0.01, relheight=.117, relwidth=.887575)

CTkLabel(valuesFrame, text="Given Values", font=Desired2_font).pack(side=LEFT,padx=12,pady=5)
quantityMenuButton = CTkOptionMenu(valuesFrame,values=quantities,height=50,width=0, font=Desired2_font, button_color='#2b2b2b', fg_color='#2b2b2b', button_hover_color='#363434',command=unit_quant)
quantityMenuButton.pack(side=LEFT,padx = 10 , pady= 5)
quantityMenuButton.set("Quantity")

valuesEntery = CTkEntry(valuesFrame,width=70,height=50, fg_color='#2b2b2b',border_color='#2b2b2b', font=Desired2_font,placeholder_text="Value")
valuesEntery.pack(side=LEFT,padx = 10 , pady= 5)
valuesEntery.bind("<FocusIn>", on_entry_click)

unitsMenuButton = CTkOptionMenu(valuesFrame,height=50,width=0, font=Desired2_font, button_color='#2b2b2b', fg_color='#2b2b2b', button_hover_color='#363434',state=DISABLED)
unitsMenuButton.pack(side=LEFT,padx = 10 , pady= 5)
unitsMenuButton.set("Unit")

objectsEntery = CTkEntry(valuesFrame,width=100,height=50, fg_color='#2b2b2b',border_color='#2b2b2b', font=Desired2_font,placeholder_text="Objects")
objectsEntery.pack(side=LEFT,padx = 10 , pady= 5)

addValueButton = CTkButton(valuesFrame,text='+',font=Desired3_font,command=addValues)
addValueButton.pack(side=LEFT,padx=10,pady=5)

givenValuesFrame = CTkScrollableFrame(problemsFrame,width=300,height=50,fg_color='#242424')
givenValuesFrame.place(relx=0.05004, rely=0.134, relwidth=.887575)

requiredValuesFrame = CTkFrame(problemsFrame,width=300,height=50,fg_color='#242424')
requiredValuesFrame.place(relx=0.05004, rely=0.5, relheight=.117, relwidth=.887575)

CTkLabel(requiredValuesFrame, text="Required Values", font=Desired2_font).pack(side=LEFT,padx=10,pady=5)
quantityMenuButton2 = CTkOptionMenu(requiredValuesFrame,values=quantities,height=40,width=0, font=Desired2_font, button_color='#2b2b2b', fg_color='#2b2b2b', button_hover_color='#363434',command=unit_quant2)
quantityMenuButton2.pack(side=LEFT,padx = 10 , pady= 5)
quantityMenuButton2.set("Quantity")

unitsMenuButton2 = CTkOptionMenu(requiredValuesFrame,height=40,width=0, font=Desired2_font, button_color='#2b2b2b', fg_color='#2b2b2b', button_hover_color='#363434',state=DISABLED)
unitsMenuButton2.pack(side=LEFT,padx = 10 , pady= 5)
unitsMenuButton2.set("Unit")

objectsEntery2 = CTkEntry(requiredValuesFrame,width=100,height=40, fg_color='#2b2b2b',border_color='#2b2b2b', font=Desired2_font,placeholder_text="Objects")
objectsEntery2.pack(side=LEFT,padx = 10 , pady= 5)

addValueButton2 = CTkButton(requiredValuesFrame,text='+',font=Desired3_font,command=addValues2)
addValueButton2.pack(side=LEFT,padx=10,pady=5)

requiredValuesFrameBar = CTkScrollableFrame(problemsFrame,width=300,height=40,fg_color='#242424')
requiredValuesFrameBar.place(relx=0.05004, rely=0.62, relwidth=.887575)

solButton = CTkButton(problemsFrame,text="Get Solutions", font=Desired2_font, height=40, command=get_sol)
solButton.place(relx=0.05004, rely=0.92, relwidth=.887575)
root.mainloop()