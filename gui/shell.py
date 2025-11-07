import customtkinter as ctk
from tools import sh_payload

class AdbShellWindow(ctk.CTk):
    def __init__(self,adb_dev):
        # ==[Stdout and ADB]== #
        self.stdout_main=""
        self.stdout_sys=""
        super().__init__()
        
        self.dev = adb_dev

        # ==[Window Setup]== #
        self.title("Fire 7/8 Shell")
        self.geometry("400x300")
        
        # Big stdout Row
        self.rowconfigure(0,weight=6)
        # Small stdin Row
        self.rowconfigure(1,weight=1)
        
        # Even Columns
        self.columnconfigure((0,1),weight=1)
        
        # ==[Widget Setup]== #
        
        # Main stdout Text
        # Frame for Background
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0,column=0,padx=20,pady=20,sticky="news")
        
        # Label
        self.main = ctk.CTkLabel(self.main_frame, text=self.stdout_main)
        self.main.grid(row=0,column=0,padx=5,pady=5,sticky="news")
        
        # System stdout Text
        # Frame for Background
        self.sys_frame = ctk.CTkFrame(self)
        self.sys_frame.grid(row=0,column=1,padx=20,pady=20,sticky="news")
        
        # Label
        self.sys = ctk.CTkLabel(self.sys_frame, text=self.stdout_sys)
        self.sys.grid(row=0,column=0,padx=5,pady=5,sticky="news")

        # ADB Shell Entry
        self.main_entry = ctk.CTkEntry(self, placeholder_text="ADB Shell Command...")
        self.main_entry.grid(row=1,column=0,padx=10,pady=10,sticky="news")
        self.main_entry.bind("<Return>", self.run_main)
        
        # System Shell Entry
        self.sys_entry = ctk.CTkEntry(self, placeholder_text="System Shell Command...")
        self.sys_entry.grid(row=1,column=1,padx=10,pady=10,sticky="news")
        self.sys_entry.bind("<Return>", self.run_sys)
    
    def update_labels(self):
            self.main.configure(text=self.stdout_main)
            self.sys.configure(text=self.stdout_sys)
            
    def run_main(self,_):
        # Get Command
        cmd = self.main_entry.get()
        
        # Clear Stdout
        if cmd == "clear":
            self.stdout_main=""
        else:
            # Write stdout
            self.stdout_main += self.dev.shell(cmd)
        
        # Clear Input Box
        self.main_entry.delete(0,len(cmd))
        
        # Update Labels
        self.update_labels()
    
    def run_sys(self,_):
        # Get Command
        cmd = self.sys_entry.get()
        
        # Clear Stdout
        if cmd == "clear":
            self.stdout_sys=""
        else:
            # Write stdout
            self.stdout_sys += sh_payload(self.dev, cmd)
        
        # Clear Input Box
        self.sys_entry.delete(0,len(cmd))
        
        # Update Labels
        self.update_labels()