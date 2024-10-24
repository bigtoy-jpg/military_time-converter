from typing import Tuple, Union
from dataclasses import dataclass
from functools import wraps
import logging
import re
from datetime import datetime, timedelta
import pytz
import tkinter as tk
from tkinter import ttk, messagebox

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
HOURS_IN_DAY = 24
HOURS_IN_HALF_DAY = 12
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60

# Custom Exception
class TimeFormatError(ValueError):
    """Custom exception for time format errors."""
    pass

@dataclass
class Time:
    hours: int
    minutes: int
    seconds: int
    timezone: str = 'UTC'  # Default timezone is UTC

def validate_time(func):
    """Decorator to validate time format and log function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            logging.info(f"Successfully executed {func.__name__}")
            return result
        except TimeFormatError as e:
            logging.error(f"Time format error in {func.__name__}: {str(e)}")
            messagebox.showerror("Time Format Error", str(e))
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {str(e)}")
            messagebox.showerror("Unexpected Error", str(e))
    return wrapper

@validate_time
def parse_time(time_str: str) -> Time:
    """Parse time string into a Time object, supporting both HH:MM and HH:MM:SS formats."""
    time_parts = time_str.split(':')
    if len(time_parts) == 2:
        hours, minutes = map(int, time_parts)
        seconds = 0
    elif len(time_parts) == 3:
        hours, minutes, seconds = map(int, time_parts)
    else:
        raise TimeFormatError("Invalid time format. Please use HH:MM or HH:MM:SS.")
    
    if not (0 <= hours < HOURS_IN_DAY and 0 <= minutes < MINUTES_IN_HOUR and 0 <= seconds < SECONDS_IN_MINUTE):
        raise TimeFormatError("Time values out of valid range.")
    
    return Time(hours, minutes, seconds)

@validate_time
def military_to_standard_time(military_time: str, use_24h: bool = False) -> str:
    """Convert military (24-hour) time to standard (12-hour) time."""
    time = parse_time(military_time)

    if use_24h:
        return f"{time.hours:02d}:{time.minutes:02d}:{time.seconds:02d}"

    period = "AM" if time.hours < HOURS_IN_HALF_DAY else "PM"
    
    if time.hours == 0:
        standard_hours = HOURS_IN_HALF_DAY
    elif time.hours > HOURS_IN_HALF_DAY:
        standard_hours = time.hours - HOURS_IN_HALF_DAY
    else:
        standard_hours = time.hours

    return f"{standard_hours}:{time.minutes:02d}:{time.seconds:02d} {period}"

@validate_time
def standard_to_military_time(standard_time: str) -> str:
    """Convert standard (12-hour) time to military (24-hour) time."""
    standard_time_pattern = re.compile(r'^(1[0-2]|0?[1-9]):([0-5][0-9]):?([0-5]?[0-9])? ?(AM|PM)$', re.IGNORECASE)
    match = standard_time_pattern.match(standard_time)
    
    if not match:
        raise TimeFormatError("Invalid standard time format. Use HH:MM:SS AM/PM.")
    
    hours, minutes, seconds, period = match.groups()
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds) if seconds else 0
    
    if period.upper() == 'PM' and hours != HOURS_IN_HALF_DAY:
        hours += HOURS_IN_HALF_DAY
    elif period.upper() == 'AM' and hours == HOURS_IN_HALF_DAY:
        hours = 0

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@validate_time
def add_time(time_str: str, hours: int = 0, minutes: int = 0, seconds: int = 0) -> str:
    """Add hours, minutes, and seconds to a given time."""
    time = parse_time(time_str)
    dt = datetime(2000, 1, 1, time.hours, time.minutes, time.seconds)
    dt += timedelta(hours=hours, minutes=minutes, seconds=seconds)
    return f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

@validate_time
def subtract_time(time_str: str, hours: int = 0, minutes: int = 0, seconds: int = 0) -> str:
    """Subtract hours, minutes, and seconds from a given time."""
    time = parse_time(time_str)
    dt = datetime(2000, 1, 1, time.hours, time.minutes, time.seconds)
    dt -= timedelta(hours=hours, minutes=minutes, seconds=seconds)
    return f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

@validate_time
def time_difference(time1: str, time2: str) -> str:
    """Calculate the difference between two times."""
    t1 = parse_time(time1)
    t2 = parse_time(time2)
    dt1 = datetime(2000, 1, 1, t1.hours, t1.minutes, t1.seconds)
    dt2 = datetime(2000, 1, 1, t2.hours, t2.minutes, t2.seconds)
    diff = abs(dt2 - dt1)
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@validate_time
def convert_timezone(time_str: str, from_tz: str, to_tz: str) -> str:
    """Convert time between two timezones."""
    time = parse_time(time_str)
    from_zone = pytz.timezone(from_tz)
    to_zone = pytz.timezone(to_tz)

    dt = datetime.now(from_zone).replace(hour=time.hours, minute=time.minutes, second=time.seconds, microsecond=0)
    converted_time = dt.astimezone(to_zone)
    
    return f"{converted_time.strftime('%H:%M:%S')} {to_tz}"

@validate_time
def format_time(time_str: str, output_format: str) -> str:
    """Format time according to the specified output format."""
    time = parse_time(time_str)
    dt = datetime(2000, 1, 1, time.hours, time.minutes, time.seconds)
    return dt.strftime(output_format)

@validate_time
def calculate_duration(start_time: str, end_time: str) -> str:
    """Calculate the duration between two times."""
    start = parse_time(start_time)
    end = parse_time(end_time)
    start_dt = datetime(2000, 1, 1, start.hours, start.minutes, start.seconds)
    end_dt = datetime(2000, 1, 1, end.hours, end.minutes, end.seconds)
    
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    
    duration = end_dt - start_dt
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def display_timezones():
    """Display available timezones for the user to select."""
    print("\n--- Timezones ---")
    print(", ".join(pytz.all_timezones[:20]))  # Display first 20 for brevity
    print("And many more... Visit https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for full list.")

def get_user_choice() -> str:
    """Display menu and get user choice."""
    print("\nTime Converter Menu:")
    print("1. Convert Military to Standard Time")
    print("2. Convert Military to 24-hour Time")
    print("3. Convert Standard to Military Time")
    print("4. Add Time")
    print("5. Subtract Time")
    print("6. Calculate Time Difference")
    print("7. Convert Time Between Timezones")
    print("8. Format Time")
    print("9. Calculate Duration")
    print("q. Quit")
    return input("Enter your choice: ").lower()

class TimeConverterGUI:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Time Converter")
        master.geometry("400x500")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_tabs()

    def create_tabs(self):
        """Create all tabs for the GUI."""
        self.create_military_to_standard_tab()
        self.create_standard_to_military_tab()
        self.create_add_subtract_time_tab()
        self.create_time_difference_tab()
        self.create_timezone_converter_tab()

    def create_military_to_standard_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Military to Standard")

        ttk.Label(tab, text="Enter Military Time (HH:MM or HH:MM:SS):").pack(pady=5)
        self.military_time_entry = ttk.Entry(tab)
        self.military_time_entry.pack(pady=5)

        ttk.Button(tab, text="Convert", command=self.convert_military_to_standard).pack(pady=5)

        self.military_result_label = ttk.Label(tab, text="")
        self.military_result_label.pack(pady=5)

    def create_standard_to_military_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Standard to Military")

        ttk.Label(tab, text="Enter Standard Time (HH:MM:SS AM/PM):").pack(pady=5)
        self.standard_time_entry = ttk.Entry(tab)
        self.standard_time_entry.pack(pady=5)

        ttk.Button(tab, text="Convert", command=self.convert_standard_to_military).pack(pady=5)

        self.standard_result_label = ttk.Label(tab, text="")
        self.standard_result_label.pack(pady=5)

    def create_add_subtract_time_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Add/Subtract Time")

        ttk.Label(tab, text="Enter Time (HH:MM or HH:MM:SS):").pack(pady=5)
        self.base_time_entry = ttk.Entry(tab)
        self.base_time_entry.pack(pady=5)

        ttk.Label(tab, text="Hours:").pack(pady=5)
        self.hours_entry = ttk.Entry(tab)
        self.hours_entry.pack(pady=5)

        ttk.Label(tab, text="Minutes:").pack(pady=5)
        self.minutes_entry = ttk.Entry(tab)
        self.minutes_entry.pack(pady=5)

        ttk.Label(tab, text="Seconds:").pack(pady=5)
        self.seconds_entry = ttk.Entry(tab)
        self.seconds_entry.pack(pady=5)

        ttk.Button(tab, text="Add Time", command=self.add_time).pack(pady=5)
        ttk.Button(tab, text="Subtract Time", command=self.subtract_time).pack(pady=5)

        self.add_subtract_result_label = ttk.Label(tab, text="")
        self.add_subtract_result_label.pack(pady=5)

    def create_time_difference_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Time Difference")

        ttk.Label(tab, text="Enter First Time (HH:MM or HH:MM:SS):").pack(pady=5)
        self.time1_entry = ttk.Entry(tab)
        self.time1_entry.pack(pady=5)

        ttk.Label(tab, text="Enter Second Time (HH:MM or HH:MM:SS):").pack(pady=5)
        self.time2_entry = ttk.Entry(tab)
        self.time2_entry.pack(pady=5)

        ttk.Button(tab, text="Calculate Difference", command=self.calculate_time_difference).pack(pady=5)

        self.time_difference_result_label = ttk.Label(tab, text="")
        self.time_difference_result_label.pack(pady=5)

    def create_timezone_converter_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Timezone Converter")

        ttk.Label(tab, text="Enter Time (HH:MM or HH:MM:SS):").pack(pady=5)
        self.tz_time_entry = ttk.Entry(tab)
        self.tz_time_entry.pack(pady=5)

        ttk.Label(tab, text="From Timezone:").pack(pady=5)
        self.from_tz_entry = ttk.Entry(tab)
        self.from_tz_entry.pack(pady=5)

        ttk.Label(tab, text="To Timezone:").pack(pady=5)
        self.to_tz_entry = ttk.Entry(tab)
        self.to_tz_entry.pack(pady=5)

        ttk.Button(tab, text="Convert", command=self.convert_timezone_gui).pack(pady=5)

        self.timezone_result_label = ttk.Label(tab, text="")
        self.timezone_result_label.pack(pady=5)

    def convert_military_to_standard(self):
        try:
            military_time = self.military_time_entry.get()
            result = military_to_standard_time(military_time)
            self.military_result_label.config(text=f"Standard time: {result}")
            logging.info(f"Converted military time {military_time} to standard time {result}")
        except Exception as e:
            logging.error(f"Error converting military to standard time: {str(e)}")
            messagebox.showerror("Error", str(e))

    def convert_standard_to_military(self):
        try:
            standard_time = self.standard_time_entry.get()
            result = standard_to_military_time(standard_time)
            self.standard_result_label.config(text=f"Military time: {result}")
            logging.info(f"Converted standard time {standard_time} to military time {result}")
        except Exception as e:
            logging.error(f"Error converting standard to military time: {str(e)}")
            messagebox.showerror("Error", str(e))

    def add_time(self):
        try:
            base_time = self.base_time_entry.get()
            hours = int(self.hours_entry.get() or 0)
            minutes = int(self.minutes_entry.get() or 0)
            seconds = int(self.seconds_entry.get() or 0)
            result = add_time(base_time, hours, minutes, seconds)
            self.add_subtract_result_label.config(text=f"Result: {result}")
            logging.info(f"Added {hours}h {minutes}m {seconds}s to {base_time}, result: {result}")
        except Exception as e:
            logging.error(f"Error adding time: {str(e)}")
            messagebox.showerror("Error", str(e))

    def subtract_time(self):
        try:
            base_time = self.base_time_entry.get()
            hours = int(self.hours_entry.get() or 0)
            minutes = int(self.minutes_entry.get() or 0)
            seconds = int(self.seconds_entry.get() or 0)
            result = subtract_time(base_time, hours, minutes, seconds)
            self.add_subtract_result_label.config(text=f"Result: {result}")
            logging.info(f"Subtracted {hours}h {minutes}m {seconds}s from {base_time}, result: {result}")
        except Exception as e:
            logging.error(f"Error subtracting time: {str(e)}")
            messagebox.showerror("Error", str(e))

    def calculate_time_difference(self):
        try:
            time1 = self.time1_entry.get()
            time2 = self.time2_entry.get()
            result = time_difference(time1, time2)
            self.time_difference_result_label.config(text=f"Time difference: {result}")
            logging.info(f"Calculated time difference between {time1} and {time2}, result: {result}")
        except Exception as e:
            logging.error(f"Error calculating time difference: {str(e)}")
            messagebox.showerror("Error", str(e))

    def convert_timezone_gui(self):
        try:
            time_str = self.tz_time_entry.get()
            from_tz = self.from_tz_entry.get()
            to_tz = self.to_tz_entry.get()
            result = convert_timezone(time_str, from_tz, to_tz)
            self.timezone_result_label.config(text=f"Converted time: {result}")
            logging.info(f"Converted time {time_str} from {from_tz} to {to_tz}, result: {result}")
        except Exception as e:
            logging.error(f"Error converting timezone: {str(e)}")
            messagebox.showerror("Error", str(e))

def main_gui():
    root = tk.Tk()
    app = TimeConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main_gui()
