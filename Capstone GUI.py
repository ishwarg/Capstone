from tkinter import *
from tkinter import filedialog
import matplotlib.pyplot as plt
import serial.tools.list_ports
import serial
import csv
 
class GUI(Frame):
    def __init__(self, master):
        Frame.__init__(self)
        self.master=master
        self.width=150
        self.height=150
        self.grid(padx=50,pady=25)
        self.createwidgets()
    def createwidgets(self):
        self.title=Label(self,text="Dynamic Phantom GUI")
        self.side=Sidebar(self)
        self.plot=Frame(self)
        self.title.grid(row=0,column=0, columnspan=5)
        self.side.grid(row=1, rowspan=2, column=0)
        self.plot.grid(row=1,rowspan=2, column=1, columnspan=4)

class Sidebar(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        self.COM=Label(self,text="COM Port")
        clicked = StringVar()  
        clicked.set( "" )
        self.COMlist=OptionMenu(self,clicked,ports)
        self.selFile=Label(self,text="No File Selected")
        self.buttonOpen=Button(self,text="Open File",command=lambda:openFile(self.selFile))    
        self.buttonCali=Button(self,text="Calibrate")
        self.buttonRun=Button(self,text="Run Test")
        self.buttonOpen.grid(row=2,column=0)
        self.selFile.grid(row=3,column=0)
        self.buttonCali.grid(row=4,column=0)
        self.buttonRun.grid(row=5,column=0)
        self.COM.grid(row=0,column=0)
        self.COMlist.grid(row=1,column=0)
        self.grid(padx=50,pady=25)
def openFile(selected_file_label):
    serial.write(
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("CSV", "*.csv")])
    if file_path:
        selected_file_label.config(text=f"Selected File: {file_path}")
        process_file(file_path,selected_file_label)
def process_file(file_path,selected_file_label):
    # Implement your file processing logic here
    # For demonstration, let's just display the contents of the selected file
        try:
            with open(file_path, 'r') as file:
                global time,concentration
                time,concentration=[]
                file_contents = csv.reader(file_path)
                for row in file_contents:
                    time.append(row[0])
                    concentration.append(row[1])
        except Exception as e:
            selected_file_label.config(text=f"Error: {str(e)}")
def listPorts():
    L=[]
    ports = serial.tools.list_ports.comports()
    
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        L.append("{}: {} [{}]".format(port, desc, hwid))
    return L
global ports

ports=listPorts()
root=Tk()
gui=GUI(root)
root.mainloop()
