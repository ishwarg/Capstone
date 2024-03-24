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
import struct
import os
 
class GUI(Frame):
    def __init__(self, master):
        Frame.__init__(self)
        self.master=master
        self.width=150
        self.height=150
        self.grid(padx=50,pady=25)
        self.createwidgets()
    def createwidgets(self):
        self.title=Label(self,text="Dynamic Phantom GUI", font=("Arial",30))
        self.side=Sidebar(self)
        self.plot=Plot(self)
        self.title.grid(row=0,column=0, columnspan=5)
        self.side.grid(row=1, rowspan=2, column=0)
        self.plot.grid(row=1,rowspan=2, column=1, columnspan=4)
class Plot(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        fig=Figure(figsize=(5,5),dpi=100)
        axSph=fig.add_subplot(221)
        axSpher=fig.add_subplot(222)
        axKid=fig.add_subplot(223)
        axKider=fig.add_subplot(224)
        lineSph,=axSph.plot([],[],lw=2)
        lineSpher,=axSpher.plot([],[],lw=2)
        lineKid,=axKid.plot([],[],lw=2)
        lineKider,=axKider.plot([],[],lw=2)
        canvas=FigureCanvasTkAgg(fig,master=self)
        
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas,self)
        max_points = 50
        # fill initial artist with nans (so nothing draws)
        lineSph, = axSph.plot(np.arange(max_points), 
                        np.ones(max_points, dtype=float)*np.nan, 
                        lw=2)
        lineSpher, = axSpher.plot(np.arange(max_points), 
                        np.ones(max_points, dtype=float)*np.nan, 
                        lw=2)
        lineKid, = axKid.plot(np.arange(max_points), 
                        np.ones(max_points, dtype=float)*np.nan, 
                        lw=2)
        lineKider, = axKider.plot(np.arange(max_points), 
                        np.ones(max_points, dtype=float)*np.nan, 
                        lw=2)
        global anim1,anim2,anim3,anim4
        anim1 = animation.FuncAnimation(fig, (lambda i, port=(arduino if COMconnected else ""):self.animateSph(port,i)),  frames=200, interval=20,blit=False)
        anim2 = animation.FuncAnimation(fig, (lambda i, port=(arduino if COMconnected else ""):self.animateSpher(port,i)),  frames=200, interval=20,blit=False)
        anim3 = animation.FuncAnimation(fig, (lambda i, port=(arduino if COMconnected else ""):self.animateKid(port,i)),  frames=200, interval=20,blit=False)
        anim4 = animation.FuncAnimation(fig, (lambda i, port=(arduino if COMconnected else ""):self.animateKider(port,i)),  frames=200, interval=20,blit=False)

        plt.show()

    def animateSph(self,port,i):
        if port=="":
            lineSph.set_ydata(0)
            return lineSph,
        else:
            y = port.readline()  # I assume this 
            old_y = lineSph.get_ydata()  # grab current data
            new_y = np.r_[old_y[1:], y]  # stick new data on end of old data
            lineSph.set_ydata(new_y)        # set the new ydata
            return lineSph,
    def animateSpher(self,port,i):
        if port=="":
            lineSpher.set_ydata(0)
            return lineSpher,
        else:
            y = port.readline()  # I assume this 
            old_y = lineSpher.get_ydata()  # grab current data
            new_y = np.r_[old_y[1:], y]  # stick new data on end of old data
            lineSpher.set_ydata(new_y)        # set the new ydata
            return lineSpher,
    def animateKid(self,port,i):
        if port=="":
            lineKid.set_ydata(0)
            return lineKid,
        else:
            y = port.readline()  # I assume this 
            old_y = lineKid.get_ydata()  # grab current data
            new_y = np.r_[old_y[1:], y]  # stick new data on end of old data
            lineKid.set_ydata(new_y)        # set the new ydata
            return lineKid,
    def animateKider(self,port,i):
        if port=="":
            lineKider.set_ydata(0)
            return lineKider,
        else:
            y = port.readline()  # I assume this 
            old_y = lineKider.get_ydata()  # grab current data
            new_y = np.r_[old_y[1:], y]  # stick new data on end of old data
            lineKider.set_ydata(new_y)        # set the new ydata
            return lineKider,
        
class Sidebar(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        
        clicked = StringVar()
        clicked.set=""
        
        self.COM=Label(self,text="COM Port")
        self.COMlist=OptionMenu(self,clicked,*ports)
        self.buttonCOM=Button(self,text="Connect",command=lambda:connectCOM(clicked,self.buttonCali,self.buttonRun,self.buttonFlush))

        self.buttonOpenSphere=Button(self,text="Open Sphere File",command=lambda:openFile(self.selFileSphere,self.buttonLoadCurveSphere))
        self.selFileSphere=Label(self,text="No File Selected")
        self.buttonLoadCurveSphere=Button(self,text="Load Sphere Curve",state="disabled",command=lambda:loadCurve(arduino,filesize,timeconc,self.buttonRun))
        
        self.buttonOpenKidney=Button(self,text="Open Kidney File",command=lambda:openFile(self.selFileKidney,self.buttonLoadCurveKidney))
        self.selFileKidney=Label(self,text="No File Selected")
        self.buttonLoadCurveKidney=Button(self,text="Load Kidney Curve",state="disabled",command=lambda:loadCurve(arduino,filesize,timeconc,self.buttonRun))

        self.buttonCali=Button(self,text="Calibrate",state="disabled",command=lambda:calibrate(arduino))
        self.buttonRun=Button(self,text="Run Test",state="disabled",command=lambda:startTest(self.buttonPause,self.buttonStop,arduino))
        self.buttonStop=Button(self,text="Stop Test",state="disabled",command=lambda:stopTest(arduino))
        self.buttonPause=Button(self,text="Pause",state="disabled",command=lambda:pause(arduino))
        self.buttonFlush=Button(self,text="Flush System",state="disabled",command=lambda:flush(arduino))
        
        dec=StringVar()
        self.entLab=Label(self,text="Decay Constant")
        self.ent=Entry(self,textvariable=dec)

        self.COM.grid(row=0,column=0,padx=5,pady=5)
        self.COMlist.grid(row=0,column=1,padx=5,pady=5)
        self.buttonCOM.grid(row=0,column=2,padx=5,pady=5)
        self.selFileSphere.grid(row=1,column=0,padx=5,pady=5)
        self.buttonOpenSphere.grid(row=1,column=1,padx=5,pady=5)
        self.buttonLoadCurveSphere.grid(row=1,column=2,padx=5,pady=5)
        self.selFileKidney.grid(row=2,column=0,padx=5,pady=5)
        self.buttonOpenKidney.grid(row=2,column=1,padx=5,pady=5)
        self.buttonLoadCurveKidney.grid(row=2,column=2,padx=5,pady=5)
        self.buttonCali.grid(row=3,column=1,padx=5,pady=5)
        self.buttonRun.grid(row=4,column=0,padx=5,pady=5)
        self.buttonStop.grid(row=4,column=1,padx=5,pady=5)
        self.buttonPause.grid(row=4,column=2,padx=5,pady=5)
        self.buttonFlush.grid(row=5,column=1,padx=5,pady=5)
        self.grid(padx=25,pady=25)
        
def startTest(pauBut,stopBut,port):
    port.write((1).to_bytes(1,"big"))
    pauBut["state"]="normal"
    stopBut["state"]="normal"
def calibrate(port):
    port.write((2).to_bytes(1,"big"))
def flush(port):
    port.write((3).to_bytes(1,"big"))
def loadCurveSphere(port,filesize,curve,runBut):
    port.write((4).to_bytes(1,"big"))
    port.write(filesize.to_bytes(2,"big"))
    for x in curve:
        port.write(bytes(x[0], 'utf-8'))
        port.write(bytes(x[1], 'utf-8'))
        runBut["state"]="normal"
def loadCurveKidney(port,filesize,curve,runBut):
    port.write((4).to_bytes(1,"big"))
    port.write(filesize.to_bytes(2,"big"))
    for x in curve:
        port.write(bytes(x[0], 'utf-8'))
        port.write(bytes(x[1], 'utf-8'))
        runBut["state"]="normal"
def pause(port):
    port.write((5).to_bytes(1,"big"))
def stopTest(port):
    port.write((6).to_bytes(1,"big"))
    
def openFile(selected_file_label,loadBut):
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("CSV", "*.csv")])
    if file_path:
        selected_file_label.config(text=f"Selected File: {os.path.basename(file_path)}")
        process_file(file_path,selected_file_label,loadBut)
def process_file(file_path,selected_file_label,loadBut):
    # Implement your file processing logic here
    # For demonstration, let's just display the contents of the selected file
        try:
            with open(file_path, 'r') as file:
                global timeconc,filesize, fileOpened
                timeconc=[]
                filesize=0
                file_contents = csv.reader(file,delimiter=',')
                for row in file_contents:
                    timeconc.append(row)
                    filesize+=1

                if COMconnected==True:
                    loadBut["state"]="normal"
                fileOpened=True
        except Exception as e:
            selected_file_label.config(text=f"Error: {str(e)}")
def listPorts():
    L=[""]
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} ".format(port, desc))
        L.append("{}: {}".format(port, desc))
    return L
global ports
def connectCOM(port,calBut,runBut,flushBut):
    global arduino, COMconnected
    p=parse.parse("{}: {}",port.get())
    arduino=serial.Serial(p[0],9600)
    calBut["state"]="normal"
    flushBut["state"]="normal"
    if fileOpened==True:
        runBut["state"]="normal"
    COMconnected=True

COMconnected=False
fileOpened=False
ports=listPorts()
root=Tk()
gui=GUI(root)
root.mainloop()
