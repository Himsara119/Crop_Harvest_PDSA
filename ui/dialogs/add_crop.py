import uuid
import tkinter as tk
from tkinter import ttk, messagebox

#External dependency: tkinter

try:
    from tkcalendar import DateEntry
except Exception:
    messagebox.showerror("Missing Dependency")
    raise

from features.crops.models import Crop

class AddCropDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Add Crop")
        self.resizable(False, False)
        self.result = None

        ttk.Label(self, text="Crop Name:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(self, textvariable=self.name_var, width=30)
        name_entry.grid(row=0, column=1, padx=8, pady=8)
        name_entry.focus_set()

        ttk.Label(self, text="planting Date:").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        self.plant_entry = DataEntry(self, date_pattern="yyyy-mm-dd")
        self.plant_entry.grid(row=1, column=1, padx=8, pady=8, sticky="w")

        ttk.Label(self, text="Expected Harvest Date:").grid(row=2, column=0, padx=8, pady=8, sticky="e")
        self.harvest_entry = DateEntry(self, date_pattern="yyyy-mm-dd")
        self.harvest_entry.grid(row=2, column=1, padx=8, pady=8, sticky="w")

        btns = ttk.Frame(self)
        btns.grid(row=3, column=0, columnspan=2, pady=(4,10))
        ttk.Button(btns, text="Cancel", command=self.on.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Add", command=self.on_add).pack(side="right")

        self.transient(master)
        self.grab_set()
        self.lift()
        self.update_idletasks()
        self._center_on(master)

def _center_on(self, master):
        try:
             mw, mh = master.winfo_width(), master.winfo_height()
             mx, my = master.winfo_rootx(), master.winfo_rooty()
             w, h = self.winfo_reqwidth(), self.winfo_reqheight()
             x = mx + (mw - w) // 2
             y = my + (mh - h) // 3
             self.geomatry(f"+{x}+{y}")
        except Exception:
             pass
        
        def on_add(self):
             name = self.name_var.get().strip()
             if not name:
                  messagebox.showerror("Validation", "Enter Crop Name")
                  return
             pd = self.plant_entry.get_date()
             hd = self.harvest_entry.get_date()
             if hd <= pd:
                  messagebox.showwarning("Validation", "Harvest date must be after planting date")
                  return
             self.result = Crop(
                 id=str(uuid.uuid4()),
                 name=name,
                 planting_date=pd,
                 expected_harvest_date=hd,
                 status="Planted"
            )
             self.destroy()