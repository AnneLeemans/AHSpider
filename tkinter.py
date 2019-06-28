

class firstClass:

    def __init__(self):
        self.root = Tk()
        self.root.lift()
        self.root.wm_title('AH Scraper')
        self.root.geometry('400x150+470+350')

        self.topFrame = Frame(self.root)
        self.topFrame.pack(side = TOP)

        self.bottomFrame = Frame(self.root)
        self.bottomFrame.pack(side = BOTTOM)

        self.dropdownTitle = StringVar(self.root)       
        self.dropdownTitle.set('AH Category')
        
        self.dropDown = OptionMenu(self.bottomFrame, self.dropdownTitle, 'agf',
                                                'kant_klaar',
                                                'protein',
                                                'kaas_vlees',
                                                'zuivel',
                                                'bakkerij',
                                                'ontbijt',
                                                'frisdrank',
                                                'wijn',
                                                'bier',
                                                'pasta_rijst',
                                                'conserve',
                                                'snoep_chips',
                                                'diepvries',
                                                'drogist',
                                                'bewuste_voeding',
                                                'huishouden',
                                                'non_food')
        self.dropDown.config(font=("Verdana", 11))
        self.dropDown.grid(row=10,column=0,sticky='nsew',)                                        
        self.dropDown.pack(side = LEFT)
        self.dropDown.focus_set()

        self.showDropdown = Label(self.topFrame, text= 'Albert Heijn scraper choose your category\n', 
            font = ('Veranda', 14))
        self.showDropdown.pack(side = TOP)

        self.printButton = Button(self.bottomFrame, text = '\nStart Scraper\n', command = self.printMessage,\
            font = ('Veranda', 11), bg = 'ivory')
        self.printButton.pack(fill = Y, side = LEFT)


    def printMessage(self):
        self.outputMessage = self.dropdownTitle.get()
        self.root.destroy()

    def waitForInput(self):
        self.root.mainloop()

    def getString(self):
        return self.outputMessage

    def quitApplication(self):
        self.outputMessage = 'Application quit without results'
        self.root.destroy()
    

def getDropdownValue():
    output = firstClass()
    output.waitForInput()
    return output.getString()

getDropdownValue()
