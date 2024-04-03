import tkinter as tk
from tkinter import filedialog
from serial.tools import list_ports
import serial
import csv
import threading
import struct
import time

class SerialManager:
    def __init__(self, port, app_instance):
        self.serial_port = port
        self.ser = serial.Serial(port, 115200, timeout=1)
        self.app_instance = app_instance
        self.thread_read = threading.Thread(target=self.read_data_thread, daemon=True)
        self.thread_read.start()

    def send_data(self, data):
        self.ser.write(data.encode())

    def send_calibration_data(self, num_rows, data_points):
        self.ser.write(struct.pack('<I', num_rows))  # Send the number of rows as unsigned integer
        for row in data_points:
            for val in row:
                self.ser.write(struct.pack('<d', val))  # Send each data point as double

    def send_curve_data(self, num_rows, data_points):
        
        #self.ser.write(struct.pack('<I', num_rows))  # Send the number of rows as unsigned integer
        numRowsToSend = str(num_rows)
        numRowsToSend+='\x00'
        self.ser.write(numRowsToSend.encode())

        for row in data_points:
            for val in row:
                # print(struct.pack('<d', val))
                # self.ser.write(struct.pack('<d', val))
                bin = str(val)
                bin+='\x00'
                print(bin)
                       
                self.ser.write(bin.encode())
                bytes_required = len(bin.encode())
                print("Number of bytes:", bytes_required)
                
    def read_data_thread(self):
        while True:
            if self.ser.in_waiting > 0:
                received_data = self.ser.readline().decode().strip()
                self.app_instance.update_serial_text(received_data)  # Update the GUI text box

    def close(self):
        self.ser.close()

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Serial Communication")

        self.serial_ports = self.get_serial_ports()

        # Dropdown menu to select available com ports
        self.port_var = tk.StringVar(master)
        self.port_var.set(self.serial_ports[0])  # default value
        self.port_menu = tk.OptionMenu(master, self.port_var, *self.serial_ports)
        self.port_menu.pack()

        # Button to connect to the selected COM port
        self.connect_button = tk.Button(master, text="Connect", command=self.connect)
        self.connect_button.pack()

        # Button to disconnect from the COM port
        self.disconnect_button = tk.Button(master, text="Disconnect", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_button.pack()

        # Text box to display serial data from Arduino
        self.serial_text = tk.Text(master, height=10, width=50)
        self.serial_text.pack()

        # Text box to send data as characters
        self.send_text = tk.Text(master, height=1, width=50)
        self.send_text.pack()

        # Button to send data
        self.send_button = tk.Button(master, text="Send", command=self.send_data)
        self.send_button.pack()

        # Button to select a CSV file
        self.select_csv_button = tk.Button(master, text="Select CSV", command=self.select_csv)
        self.select_csv_button.pack()

        # Button to parse the selected CSV file
        self.parse_csv_button = tk.Button(master, text="Parse CSV", command=self.parse_csv)
        self.parse_csv_button.pack()

        # Button to send curve data to Arduino
        self.send_curve_button = tk.Button(master, text="Send Curve", command=self.send_curve_data, state=tk.DISABLED)
        self.send_curve_button.pack()

        # Store CSV data
        self.initial_concentration = []
        self.decay_constant = []
        self.num_rows = 0
        self.data_points = []

    def get_serial_ports(self):
        ports = [port.device for port in list_ports.comports()]
        return ports

    def connect(self):
        port = self.port_var.get()
        try:
            self.serial_manager = SerialManager(port, self)
            print(f"Connected to {port}")
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.send_curve_button.config(state=tk.NORMAL)  # Enable send curve button after connection
        except serial.SerialException:
            print("Failed to connect")

    def disconnect(self):
        if hasattr(self, 'serial_manager'):
            self.serial_manager.close()
            print("Disconnected from serial port")
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.send_curve_button.config(state=tk.DISABLED)  # Disable send curve button after disconnection

    def select_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.csv_file_path = file_path
            print("CSV file selected")

    def parse_csv(self):
        if hasattr(self, 'csv_file_path'):
            with open(self.csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
                csv_reader = csv.reader(csvfile)
                self.data_points.clear()
                for i, row in enumerate(csv_reader):
                    if i == 0:
                        self.initial_concentration = [float(val) for val in row if val.strip()]
                    elif i == 1:
                        self.decay_constant = [float(val) for val in row if val.strip()]
                    elif i == 2:
                        self.num_rows = int(row[0])
                    else:
                        self.data_points.append([float(val) for val in row if val.strip()])
            print("CSV file parsed successfully")
            print(self.data_points)
        else:
            print("No CSV file selected")

    def send_data(self):
        if not hasattr(self, 'serial_manager'):
            print("Not connected to serial port")
            return

        data_to_send = self.send_text.get("1.0", "end-1c") + '\n'
        self.serial_manager.send_data(data_to_send)
        print("Data sent to Arduino")

    def send_curve_data(self):
        if not hasattr(self, 'serial_manager'):
            print("Not connected to serial port")
            return

        if not self.num_rows or not self.data_points:
            print("No curve data available")
            return
        
        print("Sending curve data:", self.data_points)  # Print data_points to verify its contents

        self.serial_manager.send_data("4")
        self.serial_manager.send_curve_data(self.num_rows, self.data_points)
        print("Curve data sent to Arduino")

    def update_serial_text(self, received_data):
        self.serial_text.insert(tk.END, received_data + "\n")
        self.serial_text.see(tk.END)  # Scroll to the bottom of the text box

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
