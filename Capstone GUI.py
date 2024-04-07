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
from datetime import datetime   
import pytz

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
        self.ser = serial.Serial(port,115200, timeout=1)
        self.app_instance = app_instance
        self.thread_read = threading.Thread(target=self.read_data_thread, daemon=True)
        self.thread_read.start()
        
    def send_data(self, data):
        time.sleep(0.010)
        self.ser.write(data.encode())

    def read_data_thread(self):
        while True:
            if self.ser.in_waiting > 0:
                if self.app_instance.testOn==False:
                    received_data = self.ser.readline().decode().strip()
                    self.app_instance.update_serial_text(received_data)# Update the GUI text box
                if self.app_instance.testOn==True:
                    received_data = self.ser.readline().decode().strip()
                    self.app_instance.update_serial_text(received_data)
                    if received_data=="Finished... Stopping...":
                        self.app_instance.testEnd()
                    if self.app_instance.sphfileLoaded==True and self.app_instance.kidfileLoaded==True:
                        row=parse.parse("{} {} {}",received_data)
                    else:
                        row=parse.parse("{} {} {}",received_data)
                    if not isinstance(row, type(None)):
                        try:
                            if self.app_instance.sphfileLoaded==True and self.app_instance.kidfileLoaded==True:
                                self.app_instance.t.append(float(row[0]))
                                self.app_instance.rawSph.append(float(row[1]))
                                self.app_instance.rawKid.append(float(row[2]))
                                self.app_instance.concSph.append(float(row[1])*math.exp(-float(row[0])*float(self.app_instance.dec.get())))
                                self.app_instance.concKid.append(float(row[2])*math.exp(-float(row[0])*float(self.app_instance.dec.get())))
                                if not self.app_instance.timeconcsphy[(np.abs(np.array(self.app_instance.timeconcspht) - float(row[0]))).argmin()]==0:
                                    self.app_instance.erSph.append((float(row[1])*math.exp(-float(row[0])*float(self.app_instance.dec.get()))-self.app_instance.timeconcsphy[(np.abs(np.array(self.app_instance.timeconcspht) - float(row[0]))).argmin()])/self.app_instance.timeconcsphy[(np.abs(np.array(self.app_instance.timeconcspht) - float(row[0]))).argmin()])
                                else:
                                    self.app_instance.erSph.append(0)
                                if not self.app_instance.timeconckidy[(np.abs(np.array(self.app_instance.timeconckidt) - float(row[0]))).argmin()]==0:
                                    self.app_instance.erKid.append((float(row[2])*math.exp(-float(row[0])*float(self.app_instance.dec.get()))-self.app_instance.timeconckidy[(np.abs(np.array(self.app_instance.timeconckidt) - float(row[0]))).argmin()])/self.app_instance.timeconckidy[(np.abs(np.array(self.app_instance.timeconckidt) - float(row[0]))).argmin()])
                                else:
                                    self.app_instance.erKid.append(0)
                                self.app_instance.i+=1
                            if self.app_instance.sphfileLoaded==True and self.app_instance.kidfileLoaded==False:
                                self.app_instance.t.append(float(row[0]))
                                self.app_instance.rawSph.append(float(row[1]))
                                self.app_instance.concSph.append(float(row[1])*math.exp(-float(row[0])*float(self.app_instance.dec.get())))
                                
                                if not self.app_instance.timeconcsphy[(np.abs(np.array(self.app_instance.timeconcspht) - float(row[0]))).argmin()]==0:
                                    self.app_instance.erSph.append((float(row[1])*math.exp(-float(row[0])*float(self.app_instance.dec.get()))-self.app_instance.timeconcsphy[(np.abs(np.array(self.app_instance.timeconcspht) - float(row[0]))).argmin()])/self.app_instance.timeconcsphy[(np.abs(np.array(self.app_instance.timeconcspht) - float(row[0]))).argmin()])
                                else:
                                    self.app_instance.erSph.append(0)

                                self.app_instance.i+=1
                            if self.app_instance.sphfileLoaded==False and self.app_instance.kidfileLoaded==True:
                                self.app_instance.t.append(float(row[0]))
                                self.app_instance.rawKid.append(float(row[1]))
                                self.app_instance.concKid.append(float(row[1])*math.exp(-float(row[0])*float(self.app_instance.dec.get())))
                                if not self.app_instance.timeconckidy[(np.abs(np.array(self.app_instance.timeconckidt) - float(row[0]))).argmin()]==0:
                                    self.app_instance.erKid.append((float(row[1])*math.exp(-float(row[0])*float(self.app_instance.dec.get()))-self.app_instance.timeconckidy[(np.abs(np.array(self.app_instance.timeconckidt) - float(row[0]))).argmin()])/self.app_instance.timeconckidy[(np.abs(np.array(self.app_instance.timeconckidt) - float(row[0]))).argmin()])
                                else:
                                    self.app_instance.erKid.append(0)
                                self.app_instance.i+=1
                                
                        except:
                            print("Read Error")
                            continue
                

    def close(self):
        self.app_instance.buttonCOM.config(text="Connect",command=self.app_instance.connectCOM)
        self.COMconnected=False
        self.ser.close()
       
class MainPage(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        self.COMconnected=False
        self.kidfileOpened=False
        self.sphfileOpened=False
        self.testOn=False
        self.sphfileLoaded=False
        self.kidfileLoaded=False
        self.clicked = StringVar()
        self.clicked.set("")
        self.ports=self.listPorts()
        self.COM=Label(self,text="COM Port")
        self.COMlist=OptionMenu(self,self.clicked,*self.ports)
        self.buttonCOM=Button(self,text="Connect",command=self.connectCOM)

        self.dec=StringVar()
        self.dec.set("0.0001518")
        self.filewritename=StringVar()
        self.activity=StringVar()
        self.activity.set("50")
        self.activityTime=StringVar()
        self.activityTime.set("1970-01-01 00:00:00")
        self.entLab=Label(self,text="Decay Constant(Hz)")
        self.ent=Entry(self,textvariable=self.dec)
        self.entLabfile=Label(self,text="Created File Name")
        self.entfile=Entry(self,textvariable=self.filewritename)
        self.entLabActivity=Label(self,text="Activity Measurement (MBq/mL)")
        self.entActivity=Entry(self,textvariable=self.activity)
        self.entLabActivityTime=Label(self,text="Measurement Time (YY-MM-DD HH:MM:SS)")
        self.entActivityTime=Entry(self,textvariable=self.activityTime)
        
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
        
        self.serialMonitor=Text(self,height=9,width=50)

        self.t=[0]
        self.rawSph=[0]
        self.rawKid=[0]
        self.concSph=[0]
        self.concKid=[0]
        self.erSph=[0]
        self.erKid=[0]
        self.i=0
        
        self.fig=Figure(figsize=(5,5),dpi=100)
        self.axSph=self.fig.add_subplot(221)
        self.axSpher=self.fig.add_subplot(222)
        self.axKid=self.fig.add_subplot(223)
        self.axKider=self.fig.add_subplot(224)

        self.canvas=FigureCanvasTkAgg(self.fig,master=self)
        self.toolbarFrame=Frame(self)
        self.toolbarFrame.grid(row=12,column=4,columnspan=2,padx=5,pady=5)
        self.toolbar = NavigationToolbar2Tk(self.canvas,self.toolbarFrame)
       
        self.animate()
        
        self.canvas.get_tk_widget().grid(row=0, rowspan=11,column=4,columnspan=2,padx=5,pady=5)
        self.COM.grid(row=0,column=0,padx=5,pady=5)
        self.COMlist.grid(row=0,column=1,padx=5,pady=5)
        self.buttonCOM.grid(row=0,column=2,padx=5,pady=5)
        self.entLab.grid(row=1,column=0,padx=5,pady=5)
        self.ent.grid(row=1,column=1,padx=5,pady=5)
        self.entLabfile.grid(row=2,column=0,padx=5,pady=5)
        self.entfile.grid(row=2,column=1,padx=5,pady=5)
        self.entLabActivity.grid(row=3,column=0,padx=5,pady=5)
        self.entActivity.grid(row=3,column=1,padx=5,pady=5)
        self.entLabActivityTime.grid(row=4,column=0,padx=5,pady=5)
        self.entActivityTime.grid(row=4,column=1,padx=5,pady=5)
        self.selFileSphere.grid(row=5,column=0,padx=5,pady=5)
        self.buttonOpenSphere.grid(row=5,column=1,padx=5,pady=5)
        self.buttonLoadCurveSphere.grid(row=5,column=2,padx=5,pady=5)
        self.selFileKidney.grid(row=6,column=0,padx=5,pady=5)
        self.buttonOpenKidney.grid(row=6,column=1,padx=5,pady=5)
        self.buttonLoadCurveKidney.grid(row=6,column=2,padx=5,pady=5)
        self.buttonCali.grid(row=7,column=1,padx=5,pady=5)
        self.buttonRun.grid(row=8,column=0,padx=5,pady=5)
        self.buttonStop.grid(row=8,column=1,padx=5,pady=5)
        self.buttonFlush.grid(row=9,column=1,padx=5,pady=5)
        self.serialMonitor.grid(row=10,column=0,columnspan=3,padx=5,pady=5)
        self.grid(padx=25,pady=25)

    def send_data(self,data_to_send):
        if not hasattr(self, 'serial_manager'):
            print("Not connected to serial port")
            return
        self.serial_manager.send_data(data_to_send)

    def update_serial_text(self, received_data):
        self.serialMonitor.insert(END, received_data + "\n")
        self.serialMonitor.see(END)  # Scroll to the bottom of the text box
        
    def startTest(self):
        try:
            self.actTime = datetime.strptime(self.activityTime.get(), "%Y-%m-%d %H:%M:%S").timestamp()
        except:
            self.update_serial_text("Activity Time has incorrect format")
            return
        self.startTime=time.time()
        if int(self.startTime)-int(self.actTime)>60*60*48:
            self.update_serial_text("Tracer too old")
            return
        if int(self.startTime)-int(self.actTime)<0:
            self.update_serial_text("Measurement time is in future")
            return
            
        try:
            self.trueActivity=float(self.activity.get())*math.exp(-float(self.dec.get())*(int(self.startTime)-int(self.actTime)))
        except:
            self.update_serial_text("Activity has incorrect format")
            return
        
        self.send_data("1\n")
        self.buttonStop.config(state=NORMAL)
        self.send_data(str(self.trueActivity)+"\n")
        self.testOn=True
        self.buttonRun.config(state=DISABLED)
        self.buttonCali.config(state=DISABLED)
        self.buttonFlush.config(state=DISABLED)
        
    def animate(self):
        if self.testOn==True:
            if self.sphfileLoaded==True:
                self.axSph.clear()
                self.axSpher.clear()
                self.axSph.plot(self.timeconcspht,self.timeconcsphy)
                self.axSph.plot(self.t[0:self.i-1],self.concSph[0:self.i-1])
                self.axSpher.plot(self.t[0:self.i-1],self.erSph[0:self.i-1])
                
            if self.kidfileLoaded==True:
                self.axKid.clear()
                self.axKider.clear()
                self.axKid.plot(self.timeconckidt,self.timeconckidy)
                self.axKid.plot(self.t[0:self.i-1],self.concKid[0:self.i-1])
                self.axKider.plot(self.t[0:self.i-1],self.erKid[0:self.i-1])
            
            self.fig.canvas.draw()


        self.after(10, self.animate)
        
    def calibrate(self):
        self.send_data("2\n")
    def flush(self):
        self.send_data("3\n")
    def loadCurve(self,cham):
        if cham=="sph":
            self.send_data("4\n")
            self.send_data(str(self.filesizesph)+"\n")
            for x in self.timeconcDecsph:
                self.send_data(str('{0:.3f}'.format(x[0]))+"\n")
                self.send_data(str('{0:.3f}'.format(x[1]))+"\n")
            self.sphfileLoaded=True
        else:
            self.send_data("4\n")
            self.send_data(str(self.filesizekid)+"\n")
            for x in self.timeconcDeckid:
                self.send_data(str('{0:.3f}'.format(x[0]))+"\n")
                self.send_data(str('{0:.3f}'.format(x[1]))+"\n")
            self.kidfileLoaded=True
        self.buttonRun.config(state=NORMAL)

        
    def testEnd(self):
        if not self.filewritename.get()=="":
            try:
                self.filewrite=open(self.filewritename.get()+".csv","x")
                if self.sphfileLoaded==True and self.kidfileLoaded==True:
                    self.filewrite.write("Time (s),Sphere Concentration,Sphere Activity,Kidney Concentration,Kidney Activity\n")
                elif self.sphfileLoaded==False and self.kidfileLoaded==True:
                    self.filewrite.write("Time (s),Kidney Concentration,Kidney Activity\n")
                elif self.sphfileLoaded==True and self.kidfileLoaded==False:
                    self.filewrite.write("Time (s),Sphere Concentration,Sphere Activity\n")
                        
                self.filewrite.close()
                self.filewrite=open(self.filewritename.get()+".csv","a")
                for i in range(0,len(self.t)-1):
                    if self.sphfileLoaded==True and self.kidfileLoaded==True:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawSph[i])+","+str(self.rawKid[i])+","+str(self.concSph[i])+","+str(self.concKid[i])+"\n")
                    elif self.sphfileLoaded==False and self.kidfileLoaded==True:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawKid[i])+","+str(self.concKid[i])+"\n")
                    elif self.sphfileLoaded==True and self.kidfileLoaded==False:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawSph[i])+","+str(self.concSph[i])+"\n")
                        
                self.filewrite.close()
            except Exception as e:
                self.update_serial_text(f"Specified write file already exists, file saved as {self.filewritename.get()}(1).csv")
                self.filewrite=open(self.filewritename.get()+"(1)"+".csv","x")
                if self.sphfileLoaded==True and self.kidfileLoaded==True:
                    self.filewrite.write("Time (s),Sphere Concentration,Sphere Activity,Kidney Concentration,Kidney Activity\n")
                elif self.sphfileLoaded==False and self.kidfileLoaded==True:
                    self.filewrite.write("Time (s),Kidney Concentration,Kidney Activity\n")
                elif self.sphfileLoaded==True and self.kidfileLoaded==False:
                    self.filewrite.write("Time (s),Sphere Concentration,Sphere Activity\n")
                        
                self.filewrite.close()
                self.filewrite=open(self.filewritename.get()+".csv","a")
                for i in range(0,len(self.t)-1):
                    if self.sphfileLoaded==True and self.kidfileLoaded==True:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawSph[i])+","+str(self.rawKid[i])+","+str(self.concSph[i])+","+str(self.concKid[i])+"\n")
                    elif self.sphfileLoaded==False and self.kidfileLoaded==True:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawKid[i])+","+str(self.concKid[i])+"\n")
                    elif self.sphfileLoaded==True and self.kidfileLoaded==False:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawSph[i])+","+str(self.concSph[i])+"\n")
                        
                self.filewrite.close()
        
        self.buttonStop.config(state=DISABLED)
        self.buttonRun.config(state=NORMAL)
        self.buttonCali.config(state=NORMAL)
        self.buttonFlush.config(state=NORMAL)
        self.testOn=False
        
    def stopTest(self):
        self.send_data("5\n")
        if not self.filewritename.get()=="":
            try:
                self.filewrite=open(self.filewritename.get()+".csv","x")
                if self.sphfileLoaded==True and self.kidfileLoaded==True:
                    self.filewrite.write("Time (s),Sphere Concentration,Sphere Activity,Kidney Concentration,Kidney Activity\n")
                elif self.sphfileLoaded==False and self.kidfileLoaded==True:
                    self.filewrite.write("Time (s),Kidney Concentration,Kidney Activity\n")
                elif self.sphfileLoaded==True and self.kidfileLoaded==False:
                    self.filewrite.write("Time (s),Sphere Concentration,Sphere Activity\n")
                        
                self.filewrite.close()
                self.filewrite=open(self.filewritename.get()+".csv","a")
                for i in range(0,len(self.t)-1):
                    if self.sphfileLoaded==True and self.kidfileLoaded==True:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawSph[i])+","+str(self.rawKid[i])+","+str(self.concSph[i])+","+str(self.concKid[i])+"\n")
                    elif self.sphfileLoaded==False and self.kidfileLoaded==True:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawKid[i])+","+str(self.concKid[i])+"\n")
                    elif self.sphfileLoaded==True and self.kidfileLoaded==False:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawSph[i])+","+str(self.concSph[i])+"\n")
                        
                self.filewrite.close()
            except Exception as e:
                self.update_serial_text(f"Specified write file already exists, file saved as {self.filewritename.get()}(1).csv")
                self.filewrite=open(self.filewritename.get()+"(1)"+".csv","x")
                if self.sphfileLoaded==True and self.kidfileLoaded==True:
                    self.filewrite.write("Time (s),Sphere Concentration,Sphere Activity,Kidney Concentration,Kidney Activity\n")
                elif self.sphfileLoaded==False and self.kidfileLoaded==True:
                    self.filewrite.write("Time (s),Kidney Concentration,Kidney Activity\n")
                elif self.sphfileLoaded==True and self.kidfileLoaded==False:
                    self.filewrite.write("Time (s),Sphere Concentration,Sphere Activity\n")
                        
                self.filewrite.close()
                self.filewrite=open(self.filewritename.get()+".csv","a")
                for i in range(0,len(self.t)-1):
                    if self.sphfileLoaded==True and self.kidfileLoaded==True:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawSph[i])+","+str(self.rawKid[i])+","+str(self.concSph[i])+","+str(self.concKid[i])+"\n")
                    elif self.sphfileLoaded==False and self.kidfileLoaded==True:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawKid[i])+","+str(self.concKid[i])+"\n")
                    elif self.sphfileLoaded==True and self.kidfileLoaded==False:
                        self.filewrite.write(str(self.t[i])+","+str(self.rawSph[i])+","+str(self.concSph[i])+"\n")
                        
                self.filewrite.close()
                
        self.buttonStop.config(state=DISABLED)
        self.buttonRun.config(state=NORMAL)
        self.buttonCali.config(state=NORMAL)
        self.buttonFlush.config(state=NORMAL)
        self.testOn=False
        
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
                            self.timeconcDecsph.append([float(row[0]),float(row[1])*math.exp(float(row[0])*float(self.dec.get()))])
                        self.axSph.plot(self.timeconcspht,self.timeconcsphy)    
                        self.canvas.draw()
                        if self.COMconnected==True:
                            self.buttonLoadCurveSphere.config(state=NORMAL)
                        self.sphfileOpened=True

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
                            self.timeconcDeckid.append([float(row[0]),float(row[1])*math.exp(float(row[0])*float(self.dec.get()))])
                        self.axKid.plot(self.timeconckidt,self.timeconckidy)
                        self.canvas.draw()
                        if self.COMconnected==True:
                            self.buttonLoadCurveKidney.config(state=NORMAL)
                        self.kidfileOpened=True
            except Exception as e:
                selected_file_label.config(text="File Format Error")
                self.update_serial_text(f"Error: {str(e)}")
    
    def listPorts(self):
        L=[""]
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            L.append("{}: {}".format(port, desc))
        return L
    def connectCOM(self):
        port=self.clicked.get()
        try:
            p=parse.parse("{}: {}",port)
            self.serial_manager=SerialManager(p[0],self)
            self.serial_manager.ser.flushInput()
            self.serial_manager.ser.flushOutput()
            self.buttonCali.config(state=NORMAL)
            self.buttonFlush.config(state=NORMAL)
            if self.kidfileOpened==True:
                self.buttonLoadCurveKidney.config(state=NORMAL)
            if self.sphfileOpened==True:
                self.buttonLoadCurveSphere.config(state=NORMAL)
            self.COMconnected=True
            self.update_serial_text("Connected to serial port")
            self.buttonCOM.config(text="Disconnect",command=self.disconnect)
        except serial.SerialException:
            self.update_serial_text("Failed to Connect")
    def disconnect(self):
        if hasattr(self, 'serial_manager'):
            self.serial_manager.close()
            self.update_serial_text("Disconnected from serial port")
            self.buttonCali.config(state=DISABLED)
            self.buttonFlush.config(state=DISABLED)
            self.buttonLoadCurveKidney.config(state=DISABLED)
            self.buttonRun.config(state=DISABLED)
            self.buttonStop.config(state=DISABLED)
            self.buttonLoadCurveSphere.config(state=DISABLED)
            self.testOn=False
            self.sphfileLoaded=False
            self.kidfileLoaded=False
     
            

root=Tk()
gui=GUI(root)
root.mainloop()
