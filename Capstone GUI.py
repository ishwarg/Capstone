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
import math
 
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
        global axSph,axKid, canvas
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
##        lineSph, = axSph.plot(np.arange(max_points), 
##                        np.ones(max_points, dtype=float)*np.nan, 
##                        lw=2)
##        lineSpher, = axSpher.plot(np.arange(max_points), 
##                        np.ones(max_points, dtype=float)*np.nan, 
##                        lw=2)
##        lineKid, = axKid.plot(np.arange(max_points), 
##                        np.ones(max_points, dtype=float)*np.nan, 
##                        lw=2)
##        lineKider, = axKider.plot(np.arange(max_points), 
##                        np.ones(max_points, dtype=float)*np.nan, 
##                        lw=2)
        anim = animation.FuncAnimation(fig, (lambda i, port=(arduino if COMconnected else ""),line1=lineSph,line1er=lineSpher,line2=lineKid,line2er=lineKider:self.animate(port,i,line1,line1er,line2,line2er)),  frames=200, interval=20,blit=False)
        plt.show()

    def animate(self,port,i,line1,line1er,line2,line2er):
        if testOn==False:
            line1.set_data([0,0])
            line1er.set_data([0,0])
            line2.set_data([0,0])
            line2er.set_data([0,0])
        else:
            row = port.readline()
            t=float(row[0])
            concSph=float(row[1])*math.exp(-t/float(dec))
            concKid=float(row[2])*math.exp(-t/float(dec))
            tindsph=(np.abs(timeconcspht - t)).argmin()
            spher=(-timeconcsphy[tind]+concSph)/timeconcsphy[tind]
            tindkid=(np.abs(timeconckidt - t)).argmin()
            kider=(-timeconckidy[tind]+concKid)/timeconckidy[tind]# I assume this 
            old_line1y = line1.get_ydata()  # grab current data
            new_line1y = np.r_[old_line1y[1:], concSph]  # stick new data on end of old data
            line1.set_ydata(new_line1y)        # set the new ydata
            old_line1t = line1.get_xdata()  # grab current data
            new_line1t = np.r_[old_line1t[1:], t]  # stick new data on end of old data
            line1.set_xdata(new_line1t)        # set the new ydata
            
            old_line2y = line2.get_ydata()  # grab current data
            new_line2y = np.r_[old_line2y[1:], concKid]  # stick new data on end of old data
            line2.set_ydata(new_line2y)        # set the new ydata
            old_line2t = line2.get_xdata()  # grab current data
            new_line2t = np.r_[old_line1t[2:], t]  # stick new data on end of old data
            line2.set_xdata(new_line2t)        # set the new ydata
            
            old_line1ery = line1er.get_ydata()  # grab current data
            new_line1ery = np.r_[old_line1ery[1:], spher]  # stick new data on end of old data
            line1er.set_ydata(new_line1ery)        # set the new ydata
            old_line1ert = line1er.get_xdata()  # grab current data
            new_line1ert = np.r_[old_line1ert[1:], t]  # stick new data on end of old data
            line1er.set_xdata(new_line1ert)        # set the new ydata
            
            old_line2ery = line2er.get_ydata()  # grab current data
            new_line2ery = np.r_[old_line2ery[1:], kider]  # stick new data on end of old data
            line2er.set_ydata(new_line2ery)        # set the new ydata
            old_line2ert = line2er.get_xdata()  # grab current data
            new_line2ert = np.r_[old_line2ert[1:], t]  # stick new data on end of old data
            line2er.set_xdata(new_line2ert)        # set the new ydata
        
class Sidebar(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        
        clicked = StringVar()
        clicked.set("")
        
        self.COM=Label(self,text="COM Port")
        self.COMlist=OptionMenu(self,clicked,*ports)
        self.buttonCOM=Button(self,text="Connect",command=lambda:connectCOM(clicked,self.buttonCali,self.buttonRun,self.buttonFlush,self.buttonLoadCurveSphere,self.buttonLoadCurveKidney))

        dec=StringVar()
        dec.set("6588")
        self.entLab=Label(self,text="Decay Half-life (s)")
        self.ent=Entry(self,textvariable=dec)

        self.buttonOpenSphere=Button(self,text="Open Sphere File",command=lambda:openFile(self.selFileSphere,self.buttonLoadCurveSphere,dec,"sph"))
        self.selFileSphere=Label(self,text="No File Selected")
        self.buttonLoadCurveSphere=Button(self,text="Load Sphere Curve",state="disabled",command=lambda:loadCurve(arduino,filesizesph,timeconcsph,self.buttonRun,"sph"))
        
        self.buttonOpenKidney=Button(self,text="Open Kidney File",command=lambda:openFile(self.selFileKidney,self.buttonLoadCurveKidney,dec,"kid"))
        self.selFileKidney=Label(self,text="No File Selected")
        self.buttonLoadCurveKidney=Button(self,text="Load Kidney Curve",state="disabled",command=lambda:loadCurve(arduino,filesizekid,timeconckid,self.buttonRun,"kid"))

        self.buttonCali=Button(self,text="Calibrate",state="disabled",command=lambda:calibrate(arduino))
        self.buttonRun=Button(self,text="Run Test",state="disabled",command=lambda:startTest(self.buttonStop,arduino))
        self.buttonStop=Button(self,text="Stop Test",state="disabled",command=lambda:stopTest(arduino))
        self.buttonFlush=Button(self,text="Flush System",state="disabled",command=lambda:flush(arduino))
        

        self.COM.grid(row=0,column=0,padx=5,pady=5)
        self.COMlist.grid(row=0,column=1,padx=5,pady=5)
        self.buttonCOM.grid(row=0,column=2,padx=5,pady=5)
        self.entLab.grid(row=1,column=0,padx=5,pady=5)
        self.ent.grid(row=1,column=1,padx=5,pady=5)
        self.selFileSphere.grid(row=2,column=0,padx=5,pady=5)
        self.buttonOpenSphere.grid(row=2,column=1,padx=5,pady=5)
        self.buttonLoadCurveSphere.grid(row=2,column=2,padx=5,pady=5)
        self.selFileKidney.grid(row=3,column=0,padx=5,pady=5)
        self.buttonOpenKidney.grid(row=3,column=1,padx=5,pady=5)
        self.buttonLoadCurveKidney.grid(row=3,column=2,padx=5,pady=5)
        self.buttonCali.grid(row=4,column=1,padx=5,pady=5)
        self.buttonRun.grid(row=5,column=0,padx=5,pady=5)
        self.buttonStop.grid(row=5,column=1,padx=5,pady=5)
        self.buttonFlush.grid(row=6,column=1,padx=5,pady=5)
        self.grid(padx=25,pady=25)
        
def startTest(stopBut,port):
    global testOn
    port.write((1).to_bytes(1,"big"))
    stopBut["state"]="normal"
    testOn=True
def calibrate(port):
    port.write((2).to_bytes(1,"big"))
def flush(port):
    port.write((3).to_bytes(1,"big"))
def loadCurve(port,filesize,curve,runBut,cham):
    if cham=="sph":
        port.write((4).to_bytes(1,"big"))
        
    else:
        port.write((4).to_bytes(1,"big"))
    port.write(filesize.to_bytes(2,"big"))
    for x in curve:
        port.write(bytes(x[0], 'utf-8'))
        port.write(bytes(x[1], 'utf-8'))
        runBut["state"]="normal"

def stopTest(port):
    port.write((5).to_bytes(1,"big"))
    
def openFile(selected_file_label,loadBut,decay,cham):
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("CSV", "*.csv")])
    if file_path:
        selected_file_label.config(text=f"Selected File: {os.path.basename(file_path)}")
        process_file(file_path,selected_file_label,loadBut,decay,cham)
def process_file(file_path,selected_file_label,loadBut,decay,cham):
    # Implement your file processing logic here
    # For demonstration, let's just display the contents of the selected file
        try:
            with open(file_path, 'r') as file:
                global timeconckid,timeconckidt,timeconckidy,timeconcDeckid,timeconcsph,timeconcspht,timeconcsphy,timeconcDecsph, filesizekid,filesizesph, kidfileOpened, sphfileOpened
                if cham=="sph":
                    timeconcDecsph=[]
                    timeconcspht=[]
                    timeconcsphy=[]
                    filesizesph=0
                    file_contents = csv.reader(file,delimiter=',')
                    timeconcsph=file_contents
                    for row in file_contents:
                        timeconcspht.append(float(row[0]))
                        timeconcsphy.append(float(row[1]))
                        filesizesph+=1
                        timeconcDecsph.append([float(row[0]),float(row[1])*math.exp(float(row[0])/float(decay.get()))])
                    axSph.plot(timeconcspht,timeconcsphy)    
                    canvas.draw()
                    if COMconnected==True:
                        loadBut["state"]="normal"
                    sphfileOpened=True

                if cham=="kid":
                    timeconcDeckid=[]
                    timeconckidt=[]
                    timeconckidy=[]
                    filesizekid=0
                    file_contents = csv.reader(file,delimiter=',')
                    timeconckid=file_contents
                    for row in file_contents:
                        timeconckidt.append(float(row[0]))
                        timeconckidy.append(float(row[1]))
                        filesizekid+=1
                        timeconcDeckid.append([float(row[0]),float(row[1])*math.exp(float(row[0])/float(decay.get()))])
                    axKid.plot(timeconckidt,timeconckidy)
                    canvas.draw()
                    if COMconnected==True:
                        loadBut["state"]="normal"
                    kidfileOpened=True
        except Exception as e:
            selected_file_label.config(text=f"Error: {str(e)}")
def listPorts():
    L=[""]
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} ".format(port, desc))
        L.append("{}: {}".format(port, desc))
    return L
def connectCOM(port,calBut,runBut,flushBut,loadBut1,loadBut2):
    global arduino, COMconnected
    p=parse.parse("{}: {}",port.get())
    arduino=serial.Serial(p[0],9600)
    calBut["state"]="normal"
    flushBut["state"]="normal"
    if kidfileOpened==True:
        runBut["state"]="normal"
        loadBut2["state"]="normal"
    if sphfileOpened==True:
        runBut["state"]="normal"
        loadBut1["state"]="normal"
    COMconnected=True
    
global ports
COMconnected=False
kidfileOpened=False
sphfileOpened=False
testOn=False
ports=listPorts()
root=Tk()
gui=GUI(root)
root.mainloop()
