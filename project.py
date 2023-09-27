import tkinter as tk
import ADC0832  # Import the ADC0832 module
import time

class RoomGUI:
    def __init__(self, master):
        self.master = master
        master.title("Room Status")
        self.alarm_status = False

        # Light status label
        self.light_label = tk.Label(master, text="Light: Unknown")
        self.light_label.pack()

        # Temperature label
        self.temp_label = tk.Label(master, text="Temperature: Unknown")
        self.temp_label.pack()

        # Temperature threshold entry
        self.temp_entry_label = tk.Label(master, text="Temperature Threshold:")
        self.temp_entry_label.pack()
        self.temp_entry = tk.Entry(master)
        self.temp_entry.pack()

        # Alarm status label
        self.alarm_label = tk.Label(master, text="Alarm: Off", fg="red")
        self.alarm_label.pack()

        # Alarm button
        self.alarm_button = tk.Button(master, text="Turn On Alarm", command=self.toggle_alarm)
        self.alarm_button.pack()

        # Submit button
        self.submit_button = tk.Button(master, text="Submit", command=self.submit)
        self.submit_button.pack()

    def submit(self):
        # Get temperature threshold from entry widget
        temp_threshold = self.temp_entry.get()

        # Get current temperature
        res = ADC0832.getADC(0)
        Vr = 3.3 * float(res) / 255
        Rt = 10000 * Vr / (3.3 - Vr)
        Cel = Rt / 100 + 16.5
        Fah = Cel * 1.8 + 32

        # Update light status label accordingly
        if Cel > float(temp_threshold):
            self.light_label.config(text=f"Light: Off, Temperature Threshold: {temp_threshold}")
        else:
            self.light_label.config(text=f"Light: On, Temperature Threshold: {temp_threshold}")

        # Update temperature label
        self.temp_label.config(text=f"Temperature: {Cel:.2f} C / {Fah:.2f} F")

    def toggle_alarm(self):
        if not self.alarm_status:
            self.alarm_label.config(text="Alarm: On", fg="green")
            self.alarm_button.config(text="Turn Off Alarm")
            self.alarm_status = True
        else:
            self.alarm_label.config(text="Alarm: Off", fg="red")
            self.alarm_button.config(text="Turn On Alarm")
            self.alarm_status = False

def main():
    ADC0832.setup()  # Initialize the ADC0832
    root = tk.Tk()
    room_gui = RoomGUI(root)
    root.mainloop()
    ADC0832.destroy()
    res = ADC0832.getADC(0)
    Vr = 3.3 * float(res) / 255
    Rt = 10000 * Vr / (3.3 - Vr)
    Cel = Rt / 100 + 16.5
    Fah = Cel * 1.8 + 32

    print(f"Temperature: {Cel:.2f} C / {Fah:.2f} F")
    

if __name__ == "__main__":
    main()
