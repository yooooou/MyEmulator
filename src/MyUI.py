from Tkinter import*
from tkFileDialog import*
import MyEngine

class SPICE(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.msg = '>>Running status:'
        self.master.title('MySpice')
        self.grid()
        self.createWidgets()
        self.mainloop()

    def createWidgets(self):
        self.label = Label(self, text = 'Welcome to my simple spice!')
        self.label.grid(row=0, columnspan=4)
        self.label.grid(row=0)
        self.openButton = Button(self, text = 'Open', width=10, command=self.open)
        self.openButton.grid(row=1, column=0,columnspan=2)
        self.simButton = Button(self, text='Simulate', width=10, state=DISABLED, command=self.simulate)
        self.simButton.grid(row=1, column=2,columnspan=2)
        self.scrollbar1 = Scrollbar(self)
        self.scrollbar2 = Scrollbar(self)

        self.text_readin = Text(self)
        self.text_readin.grid(row=2,column=0)
        self.scrollbar1.grid(row=2,column=1,sticky='ns')
        self.text_readin.config(yscrollcommand = self.scrollbar1.set)
        self.scrollbar1.config(command=self.text_readin.yview)

        self.text_output = Text(self)
        self.text_output.grid(row=2,column=2)
        self.scrollbar2.grid(row=2,column=3,sticky='ns')
        self.text_output.config(yscrollcommand = self.scrollbar2.set)
        self.scrollbar2.config(command=self.text_output.yview)


    def simulate(self):
        self.text_output.delete(0.0, END)
        MyEngine.engine(self.filename,self.text_output)

    def open(self):
        self.filename = askopenfilename()
        if self.filename:
            self.simButton['state'] = ACTIVE
            self.label['text'] = 'Design:  '+self.filename
            self.text_readin.delete(0.0, END)
            file_handle = open(self.filename,"r")
            self.text_readin.insert(END,file_handle.read())
            file_handle.close()
    

SPICE()

