import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import keyboard as kb
from pynput import keyboard
from pynput.keyboard import Key, Listener


class RemappingRow:
    """Represents a single remapping configuration"""
    def __init__(self, source_key=None, target_keys=None):
        self.source_key = source_key
        self.target_keys = target_keys if target_keys else []
        self.hook_handle = None


class KeyRemapper:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Key Remapper")
        self.root.geometry("700x500")
        
        # Remapping configurations - list of RemappingRow objects
        self.remappings = []
        self.is_active = False
        self.hook_handles = []  # Store all hook handles
        
        # UI Setup
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, text="Key Remappings", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="+ Add Remapping", 
                  command=self.add_remapping_row).pack(side=tk.RIGHT)
        
        # Column headers
        headers_frame = ttk.Frame(main_frame)
        headers_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(headers_frame, text="Source Key", font=("Arial", 10, "bold"), 
                 width=15).grid(row=0, column=0, padx=(0, 10))
        ttk.Label(headers_frame, text="Target Keys", font=("Arial", 10, "bold"), 
                 width=40).grid(row=0, column=1, padx=(0, 10))
        ttk.Label(headers_frame, text="Actions", font=("Arial", 10, "bold"), 
                 width=15).grid(row=0, column=2)
        
        # Scrollable frame for remapping rows
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        canvas = tk.Canvas(canvas_frame, height=300)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.rows_frame = ttk.Frame(canvas)
        
        self.rows_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(control_frame, text="Start Remapping", 
                                       command=self.start_remapping, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Remapping", 
                                      command=self.stop_remapping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Inactive", 
                                      font=("Arial", 9), foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def add_remapping_row(self, source_key=None, target_keys=None):
        """Add a new remapping row to the UI"""
        row_index = len(self.remappings)
        remapping = RemappingRow(source_key, target_keys)
        self.remappings.append(remapping)
        
        # Create row frame
        row_frame = ttk.Frame(self.rows_frame, relief=tk.RIDGE, borderwidth=1)
        row_frame.grid(row=row_index, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                      padx=5, pady=2)
        
        # Source key display and button
        source_frame = ttk.Frame(row_frame, width=150)
        source_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        source_frame.columnconfigure(0, weight=1)
        
        source_label = ttk.Label(source_frame, text="Not set", 
                                font=("Arial", 9), foreground="gray", width=12)
        source_label.grid(row=0, column=0, sticky=tk.W)
        
        source_button = ttk.Button(source_frame, text="Set Key", 
                                  command=lambda idx=row_index: self.set_source_key(idx))
        source_button.grid(row=0, column=1, padx=(5, 0))
        
        # Target keys display
        target_frame = ttk.Frame(row_frame, width=400)
        target_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        target_frame.columnconfigure(0, weight=1)
        
        target_label = ttk.Label(target_frame, text="No target keys", 
                                font=("Arial", 9), foreground="gray", anchor=tk.W)
        target_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        target_buttons_frame = ttk.Frame(target_frame)
        target_buttons_frame.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Button(target_buttons_frame, text="Add", 
                  command=lambda idx=row_index: self.add_target_key(idx)).pack(side=tk.LEFT, padx=2)
        ttk.Button(target_buttons_frame, text="Clear", 
                  command=lambda idx=row_index: self.clear_target_keys(idx)).pack(side=tk.LEFT, padx=2)
        
        # Actions
        actions_frame = ttk.Frame(row_frame, width=100)
        actions_frame.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Remove", 
                  command=lambda idx=row_index: self.remove_remapping_row(idx)).pack()
        
        # Store UI references in the remapping object
        remapping.row_frame = row_frame
        remapping.source_label = source_label
        remapping.source_button = source_button
        remapping.target_label = target_label
        remapping.target_buttons_frame = target_buttons_frame
        
        # Update display
        self.update_row_display(row_index)
        self.check_ready_state()
        
    def set_source_key(self, row_index):
        """Set the source key for a remapping row"""
        if row_index >= len(self.remappings):
            return
        
        remapping = self.remappings[row_index]
        remapping.source_button.config(state=tk.DISABLED, text="Press key...")
        self.root.update()
        
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char:
                    remapping.source_key = key.char.lower()
                    display_key = key.char
                else:
                    remapping.source_key = key
                    display_key = str(key).replace('Key.', '').title()
                
                self.update_row_display(row_index)
                remapping.source_button.config(state=tk.NORMAL, text="Set Key")
                self.check_ready_state()
                return False  # Stop listener
            except AttributeError:
                pass
        
        listener = Listener(on_press=on_press)
        listener.start()
        
    def add_target_key(self, row_index):
        """Add a target key to a remapping row"""
        if row_index >= len(self.remappings):
            return
        
        remapping = self.remappings[row_index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Target Key")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Press the key you want to add:", 
                 font=("Arial", 9)).pack(pady=20)
        
        status_label = ttk.Label(dialog, text="Waiting for key...", 
                                font=("Arial", 8), foreground="gray")
        status_label.pack(pady=10)
        
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char:
                    target_key = key.char.lower()
                    display_key = key.char
                else:
                    target_key = key
                    display_key = str(key).replace('Key.', '').title()
                
                # Check if key already exists
                if target_key not in remapping.target_keys:
                    remapping.target_keys.append(target_key)
                    self.update_row_display(row_index)
                    status_label.config(text=f"Added: {display_key}", foreground="green")
                    self.check_ready_state()
                else:
                    status_label.config(text="Key already added!", foreground="orange")
                
                dialog.after(500, dialog.destroy)
                return False  # Stop listener
            except AttributeError:
                pass
        
        listener = Listener(on_press=on_press)
        listener.start()
        
        def close_dialog():
            listener.stop()
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        
    def clear_target_keys(self, row_index):
        """Clear all target keys for a remapping row"""
        if row_index >= len(self.remappings):
            return
        
        remapping = self.remappings[row_index]
        remapping.target_keys.clear()
        self.update_row_display(row_index)
        self.check_ready_state()
        
    def remove_remapping_row(self, row_index):
        """Remove a remapping row"""
        if row_index >= len(self.remappings):
            return
        
        # Remove hook if active
        remapping = self.remappings[row_index]
        if remapping.hook_handle is not None:
            try:
                remapping.hook_handle()
            except:
                pass
        
        # Remove from list
        self.remappings.pop(row_index)
        
        # Rebuild UI
        self.rebuild_rows_ui()
        self.check_ready_state()
        
    def update_row_display(self, row_index):
        """Update the display for a remapping row"""
        if row_index >= len(self.remappings):
            return
        
        remapping = self.remappings[row_index]
        
        # Update source key display
        if remapping.source_key:
            if isinstance(remapping.source_key, str) and len(remapping.source_key) == 1:
                display_key = remapping.source_key.upper()
            else:
                display_key = str(remapping.source_key).replace('Key.', '').title()
            remapping.source_label.config(text=display_key, foreground="black")
        else:
            remapping.source_label.config(text="Not set", foreground="gray")
        
        # Update target keys display
        if remapping.target_keys:
            # Create display string
            display_keys = []
            for target_key in remapping.target_keys:
                if isinstance(target_key, str) and len(target_key) == 1:
                    display_keys.append(target_key.upper())
                else:
                    display_keys.append(str(target_key).replace('Key.', '').title())
            display_text = ", ".join(display_keys)
            remapping.target_label.config(text=display_text, foreground="black")
        else:
            remapping.target_label.config(text="No target keys", foreground="gray")
        
    def rebuild_rows_ui(self):
        """Rebuild the entire rows UI after a removal"""
        # Clear existing rows
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        
        # Rebuild all rows
        for i, remapping in enumerate(self.remappings):
            # Create row frame
            row_frame = ttk.Frame(self.rows_frame, relief=tk.RIDGE, borderwidth=1)
            row_frame.grid(row=i, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                          padx=5, pady=2)
            
            # Source key display and button
            source_frame = ttk.Frame(row_frame, width=150)
            source_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            source_frame.columnconfigure(0, weight=1)
            
            source_label = ttk.Label(source_frame, text="Not set", 
                                    font=("Arial", 9), foreground="gray", width=12)
            source_label.grid(row=0, column=0, sticky=tk.W)
            
            source_button = ttk.Button(source_frame, text="Set Key", 
                                      command=lambda idx=i: self.set_source_key(idx))
            source_button.grid(row=0, column=1, padx=(5, 0))
            
            # Target keys display
            target_frame = ttk.Frame(row_frame, width=400)
            target_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
            target_frame.columnconfigure(0, weight=1)
            
            target_label = ttk.Label(target_frame, text="No target keys", 
                                    font=("Arial", 9), foreground="gray", anchor=tk.W)
            target_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
            
            target_buttons_frame = ttk.Frame(target_frame)
            target_buttons_frame.grid(row=0, column=1, padx=(5, 0))
            
            ttk.Button(target_buttons_frame, text="Add", 
                      command=lambda idx=i: self.add_target_key(idx)).pack(side=tk.LEFT, padx=2)
            ttk.Button(target_buttons_frame, text="Clear", 
                      command=lambda idx=i: self.clear_target_keys(idx)).pack(side=tk.LEFT, padx=2)
            
            # Actions
            actions_frame = ttk.Frame(row_frame, width=100)
            actions_frame.grid(row=0, column=2, padx=5, pady=5)
            
            ttk.Button(actions_frame, text="Remove", 
                      command=lambda idx=i: self.remove_remapping_row(idx)).pack()
            
            # Update UI references
            remapping.row_frame = row_frame
            remapping.source_label = source_label
            remapping.source_button = source_button
            remapping.target_label = target_label
            remapping.target_buttons_frame = target_buttons_frame
            
            # Update display
            self.update_row_display(i)
        
    def check_ready_state(self):
        """Check if remapping can be started"""
        # Check if at least one remapping has source and target keys
        valid_remappings = [r for r in self.remappings 
                           if r.source_key and len(r.target_keys) > 0]
        
        if len(valid_remappings) > 0:
            self.start_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.DISABLED)
    
    def convert_key_to_kb_format(self, key):
        """Convert a key (pynput format or string) to keyboard library format"""
        if isinstance(key, str) and len(key) == 1:
            return key
        else:
            key_name = str(key).replace('Key.', '')
            key_mapping = {
                'space': 'space',
                'enter': 'enter',
                'backspace': 'backspace',
                'tab': 'tab',
                'shift': 'shift',
                'ctrl': 'ctrl',
                'alt': 'alt',
            }
            return key_mapping.get(key_name.lower(), key_name.lower())
    
    def start_remapping(self):
        """Start all key remappings"""
        # Get valid remappings
        valid_remappings = [r for r in self.remappings 
                           if r.source_key and len(r.target_keys) > 0]
        
        if len(valid_remappings) == 0:
            messagebox.showwarning("Warning", "Please configure at least one remapping with a source key and target keys.")
            return
        
        self.is_active = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Status: Active ({len(valid_remappings)} remapping(s))", 
                                foreground="green")
        
        # Set up hooks for each remapping
        for remapping in valid_remappings:
            source_key_str = self.convert_key_to_kb_format(remapping.source_key)
            
            def create_callback(remap):
                """Create a callback function for a specific remapping"""
                def on_key_press(event):
                    if not self.is_active:
                        return
                    
                    try:
                        pressed_key = event.name.lower() if event.name else None
                        
                        if pressed_key == source_key_str:
                            # Select random target key
                            random_target = random.choice(remap.target_keys)
                            target_key_str = self.convert_key_to_kb_format(random_target)
                            
                            # Send target key
                            if isinstance(target_key_str, str) and len(target_key_str) == 1:
                                kb.write(target_key_str)
                            else:
                                kb.press_and_release(target_key_str)
                    except Exception as e:
                        print(f"Error in key remapping: {e}")
                
                return on_key_press
            
            try:
                hook_handle = kb.on_press_key(source_key_str, create_callback(remapping), suppress=True)
                remapping.hook_handle = hook_handle
                self.hook_handles.append(hook_handle)
            except Exception as e:
                messagebox.showerror("Error", 
                    f"Could not set up remapping for key '{source_key_str}': {e}\n\n"
                    "Note: On Windows, you may need to run as administrator.")
                self.stop_remapping()
                return
    
    def stop_remapping(self):
        """Stop all key remappings"""
        self.is_active = False
        
        # Unhook all keyboard hooks
        for remapping in self.remappings:
            if remapping.hook_handle is not None:
                try:
                    remapping.hook_handle()
                    remapping.hook_handle = None
                except:
                    pass
        
        self.hook_handles.clear()
        
        try:
            kb.unhook_all()
        except:
            pass
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Inactive", foreground="red")


def main():
    root = tk.Tk()
    app = KeyRemapper(root)
    root.mainloop()


if __name__ == "__main__":
    main()
