from tkinter import *
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk)
from matplotlib import animation
import serial.tools.list_ports
import serial
import csv
import parse
import numpy as np
 
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
        self.plot=Plot(self)
        self.title.grid(row=0,column=0, columnspan=5)
        self.side.grid(row=1, rowspan=2, column=0)
        self.plot.grid(row=1,rowspan=2, column=1, columnspan=4)
class Plot(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        fig=Figure(figsize=(5,5),dpi=100)
        ax=fig.add_subplot(111)
        line,=ax.plot([],[],lw=2)
        canvas=FigureCanvasTkAgg(fig,master=self)
        
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas,self)
        max_points = 50
        # fill initial artist with nans (so nothing draws)
        line, = ax.plot(np.arange(max_points), 
                        np.ones(max_points, dtype=float)*np.nan, 
                        lw=2)
        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20,        blit=False)

        plt.show()
def init():
    return line,

def animate(i):
    y = arduino.readline()  # I assume this 
    old_y = line.get_ydata()  # grab current data
    new_y = np.r_[old_y[1:], y]  # stick new data on end of old data
    line.set_ydata(new_y)        # set the new ydata
    return line,
        
class Sidebar(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        self.COM=Label(self,text="COM Port")
        clicked = StringVar()  
        clicked.set( "" )
        self.COMlist=OptionMenu(self,clicked,*ports)
        self.selFile=Label(self,text="No File Selected")
        self.buttonOpen=Button(self,text="Open File",command=lambda:openFile(self.selFile))    
        self.buttonCali=Button(self,text="Calibrate")
        self.buttonRun=Button(self,text="Run Test")
        dec=StringVar()
        self.entLab=Label(self,text="Decay Constant")
        self.ent=Entry(self,textvariable=dec)
        self.COMbut=Button(self,text="Connect",command=lambda:connectCOM(clicked))
        self.buttonOpen.grid(row=2,column=0)
        self.selFile.grid(row=3,column=0)
        self.buttonCali.grid(row=4,column=0)
        self.buttonRun.grid(row=5,column=0)
        self.COM.grid(row=0,column=0)
        self.COMlist.grid(row=1,column=0)
        self.entLab.grid(row=6,column=0)
        self.ent.grid(row=6,column=1)
        self.COMbut.grid(row=1,column=1)
        self.grid(padx=50,pady=25)
def openFile(selected_file_label):
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("CSV", "*.csv")])
    if file_path:
        selected_file_label.config(text=f"Selected File: {file_path}")
        process_file(file_path,selected_file_label)
def process_file(file_path,selected_file_label):
    # Implement your file processing logic here
    # For demonstration, let's just display the contents of the selected file
        try:
            with open(file_path, 'r') as file:
                global timeconc,filesize
                timeconc=[]
                filesize=0
                file_contents = csv.reader(file,delimiter=',')
                for row in file_contents:
                    timeconc.append(row)
                    filesize+=1
                    print(row)
                print(filesize)
        except Exception as e:
            selected_file_label.config(text=f"Error: {str(e)}")
def listPorts():
    L=[]
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} ".format(port, desc))
        L.append("{}: {}".format(port, desc))
    print(L)
    return L
global ports
def connectCOM(port):
    global arduino
    p=parse.parse("{}: {}",port.get())
    arduino=serial.Serial(p[0],9600)

ports=listPorts()
root=Tk()
gui=GUI(root)
root.mainloop()
