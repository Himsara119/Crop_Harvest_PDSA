import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

try:
    from tkcalendar import Calendar, DateEntry
except Exception:
    messagebox.showerror("Missing Dependency")
    raise

from features.crops.models import Crop
from features.crops.repo import load_crops, save_crops, _export_to_csv
from features.settings.repo import load_settings, save_settings
from features.scheduling.scheduler import HarvestScheduler
from features.weather.provider import OpenMeteoProvider, OfflineHeuristicProvider
from ds.queue import Queue

APP_TITLE = "Crop Harvest Prediction Calendar"
ROOT = os.path.dirname(os.path.dirname(__file__))
EXPORTS_DIR = os.path.join(ROOT, "exports")

def run():
    app = HarvestApp()
    app.mainloop()

from ui.dialogs import AddCropDialog

class HarvestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x700")

        #State
        self.crops = load_crops()
        self.settings = load_settings()
        self.scheduler = HarvestScheduler(self.crops, self.settings.get("weather_delay_days", 0))
        self.process_queue : Queue[str] = Queue()

        #Grid Root
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        #Left: Calendar
        cal_frame = ttk.LabelFrame(self, text="Calendar")
        cal_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        cal_frame.rowconfigure(0, weight=1)
        cal_frame.columnconfigure(0, weight=1)

        self.calendar = Calendar(cal_frame, selectmode="day")
        self.calendar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.calendar.tag_config("urgent", background="red", foreground="white")
        self.calendar.tag_config("soon", background="orange", foreground="black")
        self.calendar.tag_config("normal", background="lightgreen", foreground="black")

        #Right 
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        #controls row 1
        controls = ttk.Frame(right)
        controls.grid(row=0, column=0, sticky="ew", pady=(0,8))
        controls.columnconfigure(11, weight=1)

        ttk.Button(controls, text="Add Crop", command=self.open_add_dialog).grid(row=0, column=0, padx=5)
        ttk.Button(controls, text="Delete Selected", command=self.delete_selected).grid(row=0, column=1, padx=5)
        ttk.Button(controls, text="Mark as Harvested", command=self.mark_harvested).grid(row=0, column=2, padx=5)
        ttk.Button(controls, text="Export CSV", command=self.export_csv).grid(row=0, column=3, padx=5)

        ttk.Label(controls, text="Weather Delay (days):").grid(row=0, column=4, padx=(20,5))
        self.delay_var = tk.IntVar(value=int(self.settings.get("weather_delay_days", 0)))
        delay_spin = ttk.Spinbox(controls, from_=0, to=60, textvariable=self.delay_var, width=5, command=self.on_delay_change)
        delay_spin.grid(row=0, column=5)
        ttk.Button(controls, text="Apply", command=self.on_delay_change).grid(row=0, column=6, padx=5)

        self.next_label = ttk.Label(controls, text="Next to Harvest: -")
        self.next_label.grid(row=0, column=11, sticky="e")

        #controls row 2
        controls2 = ttk.Frame(right)
        controls2.grid(row=1, column=0, sticky="ew", pady=(0,8))
        controls2.columnconfigure(10, weight=1)

        #Auto Weather
        self.auto_weather = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls2, text="Auto Weather", variable=self.auto_weather).grid(row=0, column=0, padx=5, sticky="w")
        ttk.Label(controls2, text="Lat:").grid(row=0, column=1, padx=(12,4), sticky="e")
        self.lat_var = tk.DoubleVar(value=6.9271)
        ttk.Entry(controls2, textvariable=self.lat_var, width=8).grid(row=0, column=2, sticky="w")
        ttk.Label(controls2, text="Lon:").grid(row=0, column=3, padx=(12,4), sticky="e")
        self.lon_var = tk.DoubleVar(value=79.8612)
        ttk.Entry(controls2, textvariable=self.lon_var, width=8).grid(row=0, column=4, sticky="w")
        ttk.Button(controls2, text="Sync Weather", command=self.sync_weather).grid(row=0, column=5, padx=8)
        self.weather_note = ttk.Label(controls2, text="Auto weather off.")
        self.weather_note.grid(row=0, column=6, padx=8, sticky="w")

        #Queue controls
        ttk.Button(controls2, text="Send to Queue", command=self.send_to_queue).grid(row=0, column=7, padx=(20,5))
        ttk.Button(controls2, text="Process Next", command=self.process_next).grid(row=0, column=8, padx=5)
        self.queue_len_label = ttk.Label(controls2, text="Queue: 0 item(s)")
        self.queue_len_label.grid(row=0, column=9, padx=10, sticky="w")

        #Table
        table_frame = ttk.LabelFrame(right, text="Crops")
        table_frame.grid(row=3, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        cols = ("name","planting","expected","adjusted","days_left","status","id")
        self.tree = ttk.Treeview(table_frame, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")

        help_txt =  ("Legend: Red=Urgent (≤3 days), Orange=Soon (≤7), Green=Normal. "
                    "Use Auto Weather or manual delay to shift priorities.")
        
        ttk.Label(right, text=help_txt, foreground="#555").grid(row4, column=0, pady=(6,0), sticky="w")

        self._update_queue_label()
        self.refresh_ui()

        self._update_queue_label()
        self.refresh_ui()


    #Handlers
    def on_delay_change(self):
        days = int(self.delay_var.get())
        self.settings["weather_delay_days"] = days
        save_settings(self.settings)
        self.scheduler.set_weather_delay(days)
        self.refresh_ui()

        def sync_weather(self):
            if self.auto_weather.get():
                lat, lon = float(self.lat_var.get()), float(self.lon_var.get())
                provider = OpenMeteoProvider(lat, lon)
            else:
                provider = OfflineHeuristicProvider()

            result = provider.computer_delay()
            self.settings["weather_delay_days"] = int(result.delay_days)
            save_settings(self.settings)
            self.delay_var.set(int(result.delay_days))
            self.scheduler.set_weather_delay(int(result.delay_days))
            self.refresh_ui()
            self.weather_note.config(text=f"Weather delay: {result.delay_days} day(s) [{result.reason}]")
            messagebox.showinfo("Weather synced", f"Applied delay: {result.delay_days} day(s)\nReason: {result.reason}")

        def export_csv(self):
            csv_path = os.path.join(EXPORTS_DIR, "harvest_report.csv")
            try:
                export_to_csv(self.crops, csv_path)
                messagebox.showinfo("Exported", f"CSV exported to:\n{csv_path}")
            except Exception as e:
                messagebox.showerror("Export error", str(e))

        def open_add_dialog(self):
            dlg = AddCropDialog(self)
            self.wait_window(dlg)
            if dlg.result:
                crop = dlg.result
                self.crops.append(crop)
                save_crops(self.crops)
                self.scheduler.add_crop(crop)
                self.refresh_ui()
                messagebox.showinfo("Added", f"Added: {crop.name}")

        def delete_selected(self):
            item = self.tree.selection()
            if not item:
                messagebox.showwarning("No Selection", "Please select a row to delete")
                return
            cid = self.tree.item(item[0], "values")[6]
            self.crops = [c for c in self.crops if c.id != cid]
            save_crops(self.crops)
            self.scheduler.remove_crop(cid)
            self.refresh_ui()

        def mark_harvested(self):
            item = self.tree.selection()
            if not item:
                messagebox.showwarning("No Selection", "Please select a row to mark as harvested")
                return
            cid = self.tree.item(item[0], "values")[6]
            for c in self.crops:
                if c.id == cid:
                    c.status = "Harvested"
                    break
            save_crops(self.crops)
            self.scheduler.remove_crop(cid)
            self.refresh_ui()

        def send_to_queue(self):
            item = self.tree.selection()
            if not item:
                messagebox.showwarning("No Selection", "Please select a crop")
                return
            cid = self.tree.item(item[0], "values")[6]
            self.process_queue.enqueue(cid)
            self._update_queue_label()
            messagebox.showinfo("Queued", "Crop sent to processing queue")

        def process_next(self):
            item = self.tree.selection()
            if not item:
                messagebox.showwarning("No Selection", "Please select a row to mark as harvested")
                return
            cid = self.tree.item(item[0], "values")[6]
            for c in self.crops:
                if c.id == cid:
                    c.status = "Harvested"
                    break
            save_crops(self.crops)
            self.scheduler.remove_crop(cid)
            self._update_queue_label()
            self.refresh_ui()
            messagebox.showinfo("Processed", "Processed one queued crop and marked as harvested")

            # --- UI refresh ---
        def refresh_ui(self):
            nxt = self.scheduler.next_to_harvest()
            if nxt:
                adj = nxt.expected_harvest_date + timedelta(days=self.settings.get("weather_delay_days", 0))
                dleft = (adj - date.today()).days
                self.next_label.config(text=f"Next to harvest: {nxt.name} in {dleft} day(s)")
            else:
                self.next_label.config(text="Next to harvest: —")

            for row in self.tree.get_children():
                self.tree.delete(row)
            self.calendar.calevent_remove("all")

            delay = int(self.settings.get("weather_delay_days", 0))
            ordered = self.scheduler.list_ordered()
            today = date.today()

            for c in ordered:
                adj = c.expected_harvest_date + timedelta(days=delay)
                dleft = (adj - today).days
                tag = "normal"
                if dleft <= 3:
                    tag = "urgent"
                elif dleft <= 7:
                    tag = "soon"

                self.calendar.calevent_create(adj, f"{c.name} harvest", tag)
                self.tree.insert("", "end", values=(
                    c.name,
                    c.planting_date.isoformat() if c.planting_date else "",
                    c.expected_harvest_date.isoformat(),
                    adj.isoformat(),
                    dleft,
                    c.status,
                    c.id
                ))
            self.calendar.selection_set(date.today())

        def _update_queue_label(self):
            self.queue_len_label.config(text=f"Queue: {len(self.process_queue)} item(s)")

        def run():
            app = HarvestApp()
            app.mainloop()