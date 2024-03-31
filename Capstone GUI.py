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
import threading
import time
import queue

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
        self.side=MainPage(self)
        self.title.grid(row=0,column=0, columnspan=5)
        self.side.grid(row=1, rowspan=2, column=0)
class SerialManager:
    def __init__(self, port, app_instance):
        self.serial_port = port
        self.ser = serial.Serial(port, 9600, timeout=1)
        self.app_instance = app_instance
        self.thread_read = threading.Thread(target=self.read_data_thread, daemon=True)
        self.thread_read.start()

    def send_data(self, data):
        self.ser.write(data.encode())

    def read_data_thread(self):
        while True:
            if self.ser.in_waiting > 0:
                received_data = self.ser.readline().decode().strip()
                self.app_instance.update_serial_text(received_data)  # Update the GUI text box
                self.app_instance.queue.put(received_data)
    def close(self):
        self.ser.close()        
       
class MainPage(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        
        self.clicked = StringVar()
        self.clicked.set("")
        self.ports=self.listPorts()
        self.COM=Label(self,text="COM Port")
        self.COMlist=OptionMenu(self,self.clicked,*self.ports)
        self.buttonCOM=Button(self,text="Connect",command=self.connectCOM)

        self.dec=StringVar()
        self.dec.set("6588")
        self.entLab=Label(self,text="Decay Half-life (s)")
        self.ent=Entry(self,textvariable=self.dec)
        self.queue=queue.Queue(0)
        
        self.buttonOpenSphere=Button(self,text="Open Sphere File",command=lambda:self.openFile(self.selFileSphere,"sph"))
        self.selFileSphere=Label(self,text="No File Selected")
        self.buttonLoadCurveSphere=Button(self,text="Load Sphere Curve",state="disabled",command=lambda:self.loadCurve("sph"))
        
        self.buttonOpenKidney=Button(self,text="Open Kidney File",command=lambda:self.openFile(self.selFileKidney,"kid"))
        self.selFileKidney=Label(self,text="No File Selected")
        self.buttonLoadCurveKidney=Button(self,text="Load Kidney Curve",state="disabled",command=lambda:self.loadCurve("kid"))

        self.buttonCali=Button(self,text="Calibrate",state="disabled",command=self.calibrate)
        self.buttonRun=Button(self,text="Run Test",state="disabled",command=self.startTest)
        self.buttonStop=Button(self,text="Stop Test",state="disabled",command=self.stopTest)
        self.buttonFlush=Button(self,text="Flush System",state="disabled",command=self.flush)
        
        self.serialMonitor=Text(self,height=25,width=50)

        self.activitycheck=simpledialog.askstring("Title
        self.fig=Figure(figsize=(5,5),dpi=100)
        self.axSph=self.fig.add_subplot(221)
        self.axSpher=self.fig.add_subplot(222)
        self.axKid=self.fig.add_subplot(223)
        self.axKider=self.fig.add_subplot(224)
        self.lineSph,=self.axSph.plot([],[],lw=2)
        self.lineSpher,=self.axSpher.plot([],[],lw=2)
        self.lineKid,=self.axKid.plot([],[],lw=2)
        self.lineKider,=self.axKider.plot([],[],lw=2)
        self.canvas=FigureCanvasTkAgg(self.fig,master=self)
        self.toolbarFrame=Frame(self)
        self.toolbarFrame.grid(row=8,column=4,columnspan=2,padx=5,pady=5)
        self.toolbar = NavigationToolbar2Tk(self.canvas,self.toolbarFrame)
        max_points = 50
        anim = animation.FuncAnimation(self.fig, (lambda i, port=(arduino if COMconnected else ""):self.animate(i,port)),  frames=200, interval=20,blit=False)
        plt.show()
        
        self.canvas.get_tk_widget().grid(row=0, rowspan=8,column=4,columnspan=2,padx=5,pady=5)
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
        self.serialMonitor.grid(row=7,column=0,columnspan=3,padx=5,pady=5)
        self.grid(padx=25,pady=25)
    def animate(self,i):
        if testOn==False:
            self.lineSph.set_data([0,0])
            self.lineSpher.set_data([0,0])
            self.lineKid.set_data([0,0])
            self.lineKider.set_data([0,0])
        else:
            row = self.queue.get()
            t=float(row[0])
            concSph=float(row[1])*math.exp(-t/float(self.dec.get()))
            concKid=float(row[2])*math.exp(-t/float(self.dec.get()))
            tindsph=(np.abs(timeconcspht - t)).argmin()
            spher=(-timeconcsphy[tind]+concSph)/timeconcsphy[tind]
            tindkid=(np.abs(timeconckidt - t)).argmin()
            kider=(-timeconckidy[tind]+concKid)/timeconckidy[tind]# I assume this 

            old_line1y = self.lineSph.get_ydata()  # grab current data
            new_line1y = np.r_[old_line1y[1:], concSph]  # stick new data on end of old data
            self.lineSph.set_ydata(new_line1y)        # set the new ydata
            old_line1t = self.lineSph.get_xdata()  # grab current data
            new_line1t = np.r_[old_line1t[1:], t]  # stick new data on end of old data
            self.lineSph.set_xdata(new_line1t)        # set the new ydata
            
            old_line2y = self.lineKid.get_ydata()  # grab current data
            new_line2y = np.r_[old_line2y[1:], concKid]  # stick new data on end of old data
            self.lineKid.set_ydata(new_line2y)        # set the new ydata
            old_line2t = self.lineKid.get_xdata()  # grab current data
            new_line2t = np.r_[old_line1t[2:], t]  # stick new data on end of old data
            self.lineKid.set_xdata(new_line2t)        # set the new ydata
            
            old_line1ery = self.lineSpher.get_ydata()  # grab current data
            new_line1ery = np.r_[old_line1ery[1:], spher]  # stick new data on end of old data
            self.lineSpher.set_ydata(new_line1ery)        # set the new ydata
            old_line1ert = self.lineSpher.get_xdata()  # grab current data
            new_line1ert = np.r_[old_line1ert[1:], t]  # stick new data on end of old data
            self.lineSpher.set_xdata(new_line1ert)        # set the new ydata
            
            old_line2ery = self.lineKider.get_ydata()  # grab current data
            new_line2ery = np.r_[old_line2ery[1:], kider]  # stick new data on end of old data
            self.lineKider.set_ydata(new_line2ery)        # set the new ydata
            old_line2ert = self.lineKider.get_xdata()  # grab current data
            new_line2ert = np.r_[old_line2ert[1:], t]  # stick new data on end of old data
            self.lineKider.set_xdata(new_line2ert)        # set the new ydata
    def send_data(self,data_to_send):
        if not hasattr(self, 'serial_manager'):
            print("Not connected to serial port")
            return

 #       data_to_send = self.send_text.get("1.0", "end-1c") + '\n'
        self.serial_manager.send_data(data_to_send)
        #print("Data sent to Arduino")

    def update_serial_text(self, received_data):
        self.serialMonitor.insert(END, received_data + "\n")
        self.serialMonitor.see(END)  # Scroll to the bottom of the text box
    def startTest(self):
        global testOn
        self.send_data("1")
        self.buttonStop.config(state=NORMAL)
        testOn=True
    def calibrate(self):
        self.send_data("2")
    def flush(self):
        self.send_data("3")
    def loadCurve(self,cham):
        if cham=="sph":
            self.send_data("4")
            self.send_data(str(self.filesizesph))
            for x in self.timeconcDecsph:
                self.send_data(str(x[0]))
                self.send_data(str(x[1]))
        else:
            self.send_data("4")
            self.send_data(str(self.filesizekid))
            for x in self.timeconcDeckid:
                self.send_data(str(x[0]))
                self.send_data(str(x[1]))

        self.buttonRun.config(state=NORMAL)

    def stopTest(self):
        self.send_data("5")
        
    def openFile(self,selected_file_label,cham):
        file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("CSV", "*.csv")])
        if file_path:
            selected_file_label.config(text=f"Selected File: {os.path.basename(file_path)}")
            self.process_file(file_path,selected_file_label,cham)
    def process_file(self,file_path,selected_file_label,cham):
        # Implement your file processing logic here
        # For demonstration, let's just display the contents of the selected file


            try:
                with open(file_path, 'r') as file:
                    global kidfileOpened, sphfileOpened
                    if cham=="sph":
                        self.timeconcDecsph=[]
                        self.timeconcspht=[]
                        self.timeconcsphy=[]
                        self.filesizesph=0
                        self.timeconcsph=[]
                        file_contents = csv.reader(file,delimiter=',')
                        for row in file_contents:
                            self.timeconcsph.append(row)
                            self.timeconcspht.append(float(row[0]))
                            self.timeconcsphy.append(float(row[1]))
                            self.filesizesph+=1
                            self.timeconcDecsph.append([float(row[0]),float(row[1])*math.exp(float(row[0])/float(self.dec.get()))])
                        self.axSph.plot(self.timeconcspht,self.timeconcsphy)    
                        self.canvas.draw()
                        if COMconnected==True:
                            self.buttonLoadCurveSphere.config(state=NORMAL)
                        sphfileOpened=True

                    if cham=="kid":
                        self.timeconcDeckid=[]
                        self.timeconckidt=[]
                        self.timeconckidy=[]
                        self.filesizekid=0
                        self.timeconckid=[]
                        file_contents = csv.reader(file,delimiter=',')
                        for row in file_contents:
                            self.timeconckid.append(row)
                            self.timeconckidt.append(float(row[0]))
                            self.timeconckidy.append(float(row[1]))
                            self.filesizekid+=1
                            self.timeconcDeckid.append([float(row[0]),float(row[1])*math.exp(float(row[0])/float(self.dec.get()))])
                        self.axKid.plot(self.timeconckidt,self.timeconckidy)
                        self.canvas.draw()
                        if COMconnected==True:
                            self.buttonLoadCurveKidney.config(state=NORMAL)
                        kidfileOpened=True
            except Exception as e:
                selected_file_label.config(text=f"Error: {str(e)}")
    def listPorts(self):
        L=[""]
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            print("{}: {} ".format(port, desc))
            L.append("{}: {}".format(port, desc))
        return L
    def connectCOM(self):
        global COMconnected
        port=self.clicked.get()
        try:
            p=parse.parse("{}: {}",port)
            self.serial_manager=SerialManager(p[0],self)
            self.buttonCali.config(state=NORMAL)
            self.buttonFlush.config(state=NORMAL)
            if kidfileOpened==True:
                self.buttonRun.config(state=NORMAL)
                self.buttonLoadCurveKidney.config(state=NORMAL)
            if sphfileOpened==True:
                self.buttonRun.config(state=NORMAL)
                self.buttonLoadCurveSphere.config(state=NORMAL)
            COMconnected=True
        except serial.SerialException:
            print("Failed to connect")
            
COMconnected=False
kidfileOpened=False
sphfileOpened=False
testOn=False

root=Tk()
gui=GUI(root)
root.mainloop()
