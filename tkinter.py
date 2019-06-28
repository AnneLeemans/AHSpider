from tkinter import *

# def firstClick(event):
#     print('awsome it worked')

# root = Tk()
# topFrame = Frame(root)
# topFrame.pack(side = TOP)
# bottomFrame = Frame(root)
# bottomFrame.pack(side = BOTTOM)
# button1 = Button(root, text = 'Start', fg = 'red')
# button1.bind('<Button-1>', firstClick)
# button2 = Button(topFrame, text = 'Wait', fg = 'green')
# button3 = Button(root, text = 'Stop', fg = 'purple')

# button1.pack(side = LEFT)
# button2.pack(side = LEFT)
# button3.pack(side = LEFT)

# labelOne = Label(root, text = 'Hello', bg = 'white', fg = 'blue')
# labelOne.pack(fill=X, side = TOP)

# labelTwo = Label(root, text = 'Hello', bg = 'black', fg = 'yellow')
# labelTwo.pack(fill=Y, side = RIGHT)


# root.mainloop()


class firstClass:

    def __init__(self, master, msg):          
        topFrame = Frame(master)
        topFrame.pack(side = TOP)

        bottomFrame = Frame(master)
        bottomFrame.pack(side = BOTTOM)

        self.printButton = Button(topFrame, text = 'Print something', command = self.printMessage(msg), bg = 'black', fg = 'yellow')
        self.printButton.pack(fill = Y, side = LEFT)

        self.quitButtton = Button(topFrame, text = 'Quit apllications', command = exit(), bg = 'yellow', fg = 'black')
        self.quitButtton.pack(fill = Y, side = LEFT)

    def printMessage(self, msg):
        print(msg)
    
    def takeInput(self, inputMessage):
        print('lala')
        
    


def run_firstClass():
      root = Tk()
      b = firstClass(root, 'Awsome it works!')
      root.lift()
      root.wm_title("Albert Heijn Spider")
      root.geometry('620x180+470+350')
      root.mainloop()

      

run_firstClass()