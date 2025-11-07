import customtkinter as ctk
from tools import sh_payload
from CTkMessagebox import CTkMessagebox as MsgBox
import tools
import apk_tools

class AdbMainWindow(ctk.CTk):
    def on_closing(self):
        MsgBox(title="Info", message="It's Recommended to reboot your Device, as most apps might be broken.\nBut I'll try fixing it for you.").get()
        self.destroy()
    
    def __init__(self, dev):
        super().__init__()
        
        self.dev = dev
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.title("Fire 7/8 Shell")
        self.geometry("400x300")

        # Small Top Bar Row
        self.rowconfigure(0,weight=0)
        
        # Big Content Row
        self.rowconfigure(1,weight=10)
        
        # Even Column
        self.columnconfigure((0,1,2),weight=1)
        
        ## TOP BAR
        self.apps_btn = ctk.CTkButton(self,text="Apps",command=lambda:self.toggle(0))
        self.apps_btn.grid(row=0,column=0,padx=20,pady=(20,0),sticky="news")
        
        self.debloat_btn = ctk.CTkButton(self,text="Debloat",command=lambda:self.toggle(1))
        self.debloat_btn.grid(row=0,column=1,padx=20,pady=(20,0),sticky="news")
        
        self.install_btn = ctk.CTkButton(self,text="Install",command=lambda:self.toggle(2))
        self.install_btn.grid(row=0,column=2,padx=20,pady=(20,0),sticky="news")
        
        
        ## CONTENT
        self.pkg_els = []
        
        self.apps_frame = ctk.CTkScrollableFrame(self)
        self.apps_frame.columnconfigure(0, weight=1)
        self.e_grid(self.apps_frame)
        
        self.debloat_frame = ctk.CTkScrollableFrame(self)
        self.debloat_frame.columnconfigure((0,1), weight=1)

        self.install_frame = ctk.CTkScrollableFrame(self)
        self.install_frame.columnconfigure(0, weight=1)

        ### INSTALL FRAME
        y = 0
        for pack in apk_tools.packs:
            btn=ctk.CTkButton(self.install_frame, text="Install: "+pack, command=lambda s=pack: self._install(s))
            btn.grid(row=y, column=0,padx=5,pady=5,sticky="news")
            y+=1

        ### APPS FRAME
        self.make_package_list()
        
        ### DEBLOAT FRAME
        y = 0
        for i in tools.debloat_lists:
            btn=ctk.CTkButton(self.debloat_frame, text="Debloat: "+i, command=lambda l=i:self._debloat(l))
            btn.grid(row=y,column=0,padx=5,pady=5,sticky="news")
            btn=ctk.CTkButton(self.debloat_frame, text="Rebloat: "+i, command=lambda l=i:self._rebloat(l))
            btn.grid(row=y,column=1,padx=5,pady=5,sticky="news")
            y+=1

        # Buttons for Fire Launcher
        btn=ctk.CTkButton(self.debloat_frame, text="Remove Fire Launcher", command=lambda:
                            print(tools.sh_payload(self.dev, "pm disable-user com.amazon.firelauncher"))
                          )
        btn.grid(row=y,column=0,padx=5,pady=5,sticky="news")
        
        btn=ctk.CTkButton(self.debloat_frame, text="Re-Add Fire Launcher", command=lambda:
                            print(tools.sh_payload(self.dev, "pm enable com.amazon.firelauncher"))
                          )
                          
        btn.grid(row=y,column=1,padx=5,pady=5,sticky="news")
    
    def _install(self, pack):
        apk_tools.install_pack(self.dev, pack)

    def _debloat(self, l):
        if l == "Extreme":
            msg = MsgBox(title="Debloat",message="This could potentially break things!\nContinue?",option_1="Yes",option_2="No",icon="warning")
            resp = msg.get()
            if resp != "Yes":
                return
        #MsgBox(title="Debloat", message="Debloating...")
        for pkg in tools.debloat_lists[l]:
            print(tools.sh_payload(self.dev, "pm disable-user "+pkg))
        if l == "Remove OTA":
            MsgBox(title="OTA", message="OTA Disabled!")
        else:
            MsgBox(title="Debloat", message="Debloat Finished!")
        
    def _rebloat(self, l):
        msg = MsgBox(title="Rebloat",message="Are you sure you want to continue?",option_1="Yes",option_2="No",icon="question")
        resp = msg.get()
        if resp != "Yes":
            return
        #MsgBox(title="Debloat", message="Debloating...")
        for pkg in tools.debloat_lists[l]:
            print(tools.sh_payload(self.dev, "pm enable "+pkg))
        if l == "Remove OTA":
            MsgBox(title="OTA", message="OTA Disabled!")
        else:
            MsgBox(title="Rebloat", message="Re-bloat Finished!")
    
    def e_grid(self, e): e.grid(row=1,column=0,columnspan=3,padx=20,pady=20,sticky="news")
    
    def toggle(self, i):
        self.apps_frame.grid_forget()
        self.debloat_frame.grid_forget()
        self.install_frame.grid_forget()
        if i == 0:
            self.e_grid(self.apps_frame)
        elif i == 1:
            self.e_grid(self.debloat_frame)
        elif i == 2:
            self.e_grid(self.install_frame)
    
    def make_package_list(self):
        self.pkgs = tools.get_packages(self.dev)
        
        # Remove Original Elements
        for p in self.pkg_els:
            p.destroy()
        self.pkg_els.clear()
        
        y = 0
        for p in self.pkgs:
            # Protection for Important Apps
            if p.name == "*":
                p.assign(ctk.CTkButton(self.apps_frame, text=p.pkg), False)
            else:
                p.assign(ctk.CTkButton(self.apps_frame, text=p.name, command=lambda v=p: v.toggle()))
            p.btn.grid(row=y,column=0,padx=5,pady=5,sticky="news")
            y+=1

            