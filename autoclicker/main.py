import customtkinter as ctk
import tkinter as tk
import threading
import time
import sys
import os
import ctypes
from PIL import Image, ImageTk
from clicker import clicker
from settings import settings
from pynput import keyboard

# Configuration
APP_NAME = "tungtungtungsahursimgaligmaNGaClicker OP v.67676767"
ACCENT_COLOR = "#2CC985"
BG_COLOR = "#0F0F0F"
FRAME_BG = "#161616"
INPUT_BG = "#1F1F1F"
TEXT_COLOR = "#E0E0E0"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("dark")

TOOLTIPS = {
    "Clicks Per": "Legt die Anzahl der Klicks pro Zeitintervall fest.",
    "Hotkey": "Taste zum Starten/Stoppen des Autoclickers.",
    "Mode": "Toggle: Ein-/Ausschalten. Hold: Aktiv solange Taste gedrückt.",
    "Mouse Button": "Wählt die Maustaste für die Klicks aus.",
    "Duty Cycle": "Bestimmt, wie lange die Maustaste pro Klick gedrückt bleibt (in % des Klick-Intervalls).",
    "Speed Variation": "Fügt zufällige Verzögerungen hinzu, um menschlicher zu wirken (in %).",
    "Double Click": "Führt bei jedem Klick einen Doppelklick aus.",
    "Click Limit": "Stoppt den Autoclicker nach einer bestimmten Anzahl von Klicks.",
    "Time Limit": "Stoppt den Autoclicker nach einer bestimmten Zeit in Sekunden.",
    "Corner Stop": "Stoppt den Autoclicker, wenn die Maus in die obere linke Ecke bewegt wird.",
    "Edge Stop": "Stoppt den Autoclicker, wenn die Maus an den Bildschirmrand bewegt wird.",
    "Position": "Klickt an einer festen Bildschirmposition anstatt an der aktuellen Mausposition."
}

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide_tooltip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.show_tooltip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show_tooltip(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#1F1F1F", foreground="#E0E0E0",
                         relief="solid", borderwidth=1,
                         font=("Arial", 10, "normal"), padx=5, pady=3)
        label.pack()
        
    def hide_tooltip(self):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

class StyledFrame(ctk.CTkFrame):
    def __init__(self, master, title=None, **kwargs):
        super().__init__(master, fg_color=FRAME_BG, corner_radius=8, border_width=1, border_color="#2A2A2A", **kwargs)
        if title:
            self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_COLOR)
            self.title_label.pack(anchor="w", padx=15, pady=(12, 8))
            if title in TOOLTIPS:
                ToolTip(self.title_label, TOOLTIPS[title])

class SegmentedButton(ctk.CTkFrame):
    def __init__(self, master, values, command=None, **kwargs):
        super().__init__(master, fg_color=INPUT_BG, corner_radius=6, height=32, **kwargs)
        self.values = values
        self.command = command
        self.buttons = {}
        self.current_value = values[0]
        
        for i, val in enumerate(values):
            btn = ctk.CTkButton(self, text=val, width=40, height=24, corner_radius=4,
                               fg_color="transparent", hover_color="#2A2A2A",
                               text_color="#888888", font=ctk.CTkFont(size=12, weight="bold"),
                               command=lambda v=val: self._on_click(v))
            btn.pack(side="left", padx=2, pady=2)
            self.buttons[val] = btn
        
        self._update_styles()

    def _on_click(self, value):
        self.current_value = value
        self._update_styles()
        if self.command:
            self.command(value)

    def _update_styles(self):
        for val, btn in self.buttons.items():
            if val == self.current_value:
                btn.configure(fg_color="#333333", text_color=TEXT_COLOR)
            else:
                btn.configure(fg_color="transparent", text_color="#888888")

    def get(self): return self.current_value
    def set(self, val):
        self.current_value = val
        self._update_styles()

class AutoClickerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("850x650")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_NAME)
        except Exception:
            pass
        icon_path = resource_path("assets/Baddie.png")
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.iconphoto(True, photo)
                self._icon_photo = photo
            except Exception:
                pass
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.hotkey_listener = None
        self.current_hotkey = "f6"
        self._hotkey_pressed_keys = set()
        
        self.setup_ui()
        self.load_settings()
        self.start_hotkey_listener()
        self.repack_panels()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=20, pady=(10, 0))
        
        title_label = ctk.CTkLabel(header, text=APP_NAME, font=ctk.CTkFont(size=20, weight="bold"), text_color=ACCENT_COLOR)
        title_label.pack(side="left")
        
        # Tabs
        self.tabview = ctk.CTkTabview(self, fg_color="transparent", segmented_button_selected_color="#333333", segmented_button_selected_hover_color="#444444")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tab_clicker = self.tabview.add("Clicker")
        self.tab_settings = self.tabview.add("Einstellungen")

        # --- CLICKER TAB ---
        self.tab_clicker.grid_columnconfigure((0, 1), weight=1)
        
        self.left_col = ctk.CTkFrame(self.tab_clicker, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.right_col = ctk.CTkFrame(self.tab_clicker, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # 1. Click Settings (Always visible)
        self.click_frame = StyledFrame(self.left_col)
        self.click_frame.pack(fill="x", pady=(0, 15))
        
        row1 = ctk.CTkFrame(self.click_frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(15, 10))
        
        lbl_cps = ctk.CTkLabel(row1, text="Clicks Per", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_cps.pack(side="left")
        ToolTip(lbl_cps, TOOLTIPS["Clicks Per"])
        
        self.cps_entry = ctk.CTkEntry(row1, width=60, height=32, fg_color=INPUT_BG, border_width=0, font=ctk.CTkFont(weight="bold"))
        self.cps_entry.pack(side="left", padx=10)
        self.cps_entry.insert(0, "20")
        
        self.unit_selector = SegmentedButton(row1, values=["s", "m", "h", "d"], command=self.on_unit_change)
        self.unit_selector.pack(side="left")
        
        row2 = ctk.CTkFrame(self.click_frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=10)
        
        lbl_hotkey = ctk.CTkLabel(row2, text="Hotkey", font=ctk.CTkFont(size=14))
        lbl_hotkey.pack(side="left")
        ToolTip(lbl_hotkey, TOOLTIPS["Hotkey"])
        
        self.hotkey_btn = ctk.CTkButton(row2, text="F6", width=100, height=32, fg_color=INPUT_BG, hover_color="#2A2A2A", 
                                       text_color=TEXT_COLOR, font=ctk.CTkFont(weight="bold"), command=self.start_hotkey_recording)
        self.hotkey_btn.pack(side="left", padx=10)
        
        self.mode_selector = SegmentedButton(row2, values=["Toggle", "Hold"], command=self.on_mode_change)
        self.mode_selector.pack(side="left")
        
        lbl_mode = ctk.CTkLabel(row2, text="?", font=ctk.CTkFont(size=12), text_color="#888888")
        lbl_mode.pack(side="left", padx=(5, 0))
        ToolTip(lbl_mode, TOOLTIPS["Mode"])
        
        row3 = ctk.CTkFrame(self.click_frame, fg_color="transparent")
        row3.pack(fill="x", padx=15, pady=(10, 15))
        
        lbl_button = ctk.CTkLabel(row3, text="Mouse Button", font=ctk.CTkFont(size=14))
        lbl_button.pack(side="left")
        ToolTip(lbl_button, TOOLTIPS["Mouse Button"])
        
        self.button_selector = SegmentedButton(row3, values=["Left", "Middle", "Right"], command=self.on_button_change)
        self.button_selector.pack(side="left", padx=10)

        # Create panels without packing them yet
        # Left Column Panels
        self.duty_frame = self.create_feature_row(self.left_col, "Duty Cycle", "45", "%", self.on_duty_change)
        self.speed_frame = self.create_feature_row(self.left_col, "Speed Variation", "35", "%", self.on_speed_variation_change)
        self.double_click_frame = self.create_feature_row(self.left_col, "Double Click", None, None, self.on_double_click_toggle)

        # Right Column Panels
        self.click_limit_frame = self.create_feature_row(self.right_col, "Click Limit", "1000", "", self.on_click_limit_change)
        self.time_limit_frame = self.create_feature_row(self.right_col, "Time Limit", "60", "s", self.on_time_limit_change)
        self.corner_stop_frame = self.create_feature_row(self.right_col, "Corner Stop", "25", "px", self.on_corner_stop_change)
        self.edge_stop_frame = self.create_feature_row(self.right_col, "Edge Stop", "40", "px", self.on_edge_stop_change)
        self.pos_frame = self.create_feature_row(self.right_col, "Position", "Pick", "", self.on_position_change)

        # Bottom Status
        self.status_bar = ctk.CTkFrame(self, fg_color=FRAME_BG, height=40)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="STATUS: OFF", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FF5555")
        self.status_label.pack(side="left", padx=20)
        
        self.counter_label = ctk.CTkLabel(self.status_bar, text="CLICKS: 0", font=ctk.CTkFont(size=12, weight="bold"))
        self.counter_label.pack(side="right", padx=20)
        
        # --- SETTINGS TAB ---
        self.build_settings_tab()

    def build_settings_tab(self):
        settings_frame = ctk.CTkScrollableFrame(self.tab_settings, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(settings_frame, text="Sichtbare Panels konfigurieren", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(10, 10), padx=5)

        panels = [
            ("Duty Cycle", "duty_cycle"),
            ("Speed Variation", "speed_variation"),
            ("Double Click", "double_click"),
            ("Click Limit", "click_limit"),
            ("Time Limit", "time_limit"),
            ("Corner Stop", "corner_stop"),
            ("Edge Stop", "edge_stop"),
            ("Position", "position")
        ]

        self.panel_vars = {}
        for text, key in panels:
            var = tk.BooleanVar(value=settings.get("panels", key, default=True))
            self.panel_vars[key] = var
            switch = ctk.CTkSwitch(settings_frame, text=text, variable=var, progress_color=ACCENT_COLOR,
                                   command=lambda k=key, v=var: self.on_panel_toggle(k, v))
            switch.pack(anchor="w", pady=8, padx=10)

    def on_panel_toggle(self, key, var):
        settings.set(var.get(), "panels", key)
        self.repack_panels()

    def repack_panels(self):
        self.duty_frame.pack_forget()
        self.speed_frame.pack_forget()
        self.double_click_frame.pack_forget()
        
        self.click_limit_frame.pack_forget()
        self.time_limit_frame.pack_forget()
        self.corner_stop_frame.pack_forget()
        self.edge_stop_frame.pack_forget()
        self.pos_frame.pack_forget()

        if settings.get("panels", "duty_cycle", default=True):
            self.duty_frame.pack(fill="x", pady=(0, 15))
        if settings.get("panels", "speed_variation", default=True):
            self.speed_frame.pack(fill="x", pady=(0, 15))
        if settings.get("panels", "double_click", default=True):
            self.double_click_frame.pack(fill="x", pady=(0, 15))
            
        if settings.get("panels", "click_limit", default=True):
            self.click_limit_frame.pack(fill="x", pady=(0, 15))
        if settings.get("panels", "time_limit", default=True):
            self.time_limit_frame.pack(fill="x", pady=(0, 15))
        if settings.get("panels", "corner_stop", default=True):
            self.corner_stop_frame.pack(fill="x", pady=(0, 15))
        if settings.get("panels", "edge_stop", default=True):
            self.edge_stop_frame.pack(fill="x", pady=(0, 15))
        if settings.get("panels", "position", default=True):
            self.pos_frame.pack(fill="x", pady=(0, 15))

    def create_feature_row(self, master, title, val_text, unit_text, command):
        frame = StyledFrame(master)
        
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
        
        lbl = ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(side="left")
        if title in TOOLTIPS:
            ToolTip(lbl, TOOLTIPS[title])
        
        right_side = ctk.CTkFrame(inner, fg_color="transparent")
        right_side.pack(side="right")
        
        entry = None
        if val_text:
            entry = ctk.CTkEntry(right_side, width=60, height=28, fg_color=INPUT_BG, border_width=0, font=ctk.CTkFont(size=12))
            entry.pack(side="left", padx=5)
            entry.insert(0, val_text)
            if unit_text:
                ctk.CTkLabel(right_side, text=unit_text, font=ctk.CTkFont(size=11), text_color="#666666").pack(side="left")
        
        switch = ctk.CTkSwitch(right_side, text="", width=40, progress_color=ACCENT_COLOR, command=lambda: command(switch.get()))
        switch.pack(side="left", padx=(10, 0))
        
        # Store entry references for access in handlers
        attr_name = title.lower().replace(" ", "_") + "_entry"
        setattr(self, attr_name, entry)
        
        return frame

    # Event Handlers
    def on_unit_change(self, val): clicker.set_unit(val)
    def on_mode_change(self, val): clicker.set_mode(val)
    def on_button_change(self, val): clicker.set_button(val)
    
    def on_duty_change(self, state):
        try:
            val = float(self.duty_cycle_entry.get())
            clicker.set_duty_cycle(val if state else 45)
        except (ValueError, AttributeError): pass

    def on_speed_variation_change(self, state):
        try:
            val = float(self.speed_variation_entry.get())
            clicker.set_speed_variation(val if state else 0)
        except (ValueError, AttributeError): pass

    def on_double_click_toggle(self, state):
        clicker.set_double_click(state)

    def on_click_limit_change(self, state):
        try:
            val = int(self.click_limit_entry.get())
            clicker.set_click_limit(state, val)
        except (ValueError, AttributeError): pass

    def on_time_limit_change(self, state):
        try:
            val = int(self.time_limit_entry.get())
            clicker.set_time_limit(state, val)
        except (ValueError, AttributeError): pass

    def on_corner_stop_change(self, state):
        try:
            val = int(self.corner_stop_entry.get())
            clicker.set_corner_stop(state, val)
        except (ValueError, AttributeError): pass

    def on_edge_stop_change(self, state):
        try:
            val = int(self.edge_stop_entry.get())
            clicker.set_edge_stop(state, val)
        except (ValueError, AttributeError): pass

    def on_position_change(self, state):
        clicker.set_position(state, (0, 0))

    def start_hotkey_recording(self):
        self.hotkey_btn.configure(text="...", text_color=ACCENT_COLOR)
        self.recording_hotkey = True
        self._pressed_keys = set()

    def toggle_clicker(self):
        try:
            cps = float(self.cps_entry.get())
            clicker.set_cps(cps)
        except ValueError: pass
        clicker.toggle()
        self.update_status()

    def update_status(self):
        if clicker.is_running():
            self.status_label.configure(text="STATUS: ON", text_color=ACCENT_COLOR)
            self.start_counter_update()
        else:
            self.status_label.configure(text="STATUS: OFF", text_color="#FF5555")

    def start_counter_update(self):
        self._update_counter_loop()

    def _update_counter_loop(self):
        if clicker.is_running():
            self.counter_label.configure(text=f"CLICKS: {clicker.get_click_count()}")
            self.after(100, self._update_counter_loop)

    def load_settings(self):
        c = settings.get("clicker", default={})
        self.cps_entry.delete(0, "end")
        self.cps_entry.insert(0, str(c.get("clicks_per_unit", 20)))
        self.unit_selector.set(c.get("unit", "s"))
        self.button_selector.set(c.get("button", "Left"))
        self.mode_selector.set(c.get("mode", "Toggle").capitalize())
        
        self.current_hotkey = settings.get("hotkey", "current_hotkey", default="f6")
        self.hotkey_btn.configure(text=self.current_hotkey.upper().replace("_L", "").replace("_R", ""))
        
        clicker.set_cps(float(self.cps_entry.get()))
        clicker.set_unit(self.unit_selector.get())
        clicker.set_button(self.button_selector.get())
        clicker.set_mode(self.mode_selector.get())
        
        clicker.set_duty_cycle(c.get("duty_cycle", 45))
        clicker.set_speed_variation(c.get("speed_variation", 35))
        clicker.set_double_click(c.get("double_click", False))

    def save_settings(self):
        settings.set(float(self.cps_entry.get()), "clicker", "clicks_per_unit")
        settings.set(self.unit_selector.get(), "clicker", "unit")
        settings.set(self.button_selector.get(), "clicker", "button")
        settings.set(self.mode_selector.get(), "clicker", "mode")
        settings.set(self.current_hotkey, "hotkey", "current_hotkey")
        settings.save()

    def start_hotkey_listener(self):
        self._pressed_keys = set()
        self.hotkey_listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

    def _get_key_str(self, key):
        try: return key.char.lower()
        except AttributeError: return str(key).replace("Key.", "")

    def _on_press(self, key):
        k = self._get_key_str(key)
        self._pressed_keys.add(k)
        
        if hasattr(self, 'recording_hotkey') and self.recording_hotkey:
            if k not in ["ctrl_l", "ctrl_r", "shift", "alt_l", "alt_gr"]:
                mods = [m for m in ["ctrl_l", "ctrl_r", "shift", "alt_l"] if m in self._pressed_keys]
                new_hotkey = "+".join(mods + [k]) if mods else k
                self.current_hotkey = new_hotkey
                self.hotkey_btn.configure(text=new_hotkey.upper().replace("_L", "").replace("_R", ""), text_color=TEXT_COLOR)
                self.recording_hotkey = False
            return

        hotkey_parts = self.current_hotkey.split("+")
        if all(part in self._pressed_keys for part in hotkey_parts):
            if len(self._pressed_keys) == len(hotkey_parts):
                self.after(0, self.toggle_clicker)

    def _on_release(self, key):
        k = self._get_key_str(key)
        self._pressed_keys.discard(k)
        if clicker.mode == "hold":
            hotkey_parts = self.current_hotkey.split("+")
            if k in hotkey_parts:
                self.after(0, clicker.stop)
                self.after(0, self.update_status)

    def on_close(self):
        self.save_settings()
        clicker.stop()
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = AutoClickerGUI()
    app.mainloop()