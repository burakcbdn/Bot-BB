import platform
class OsController:

    def __init__(self):
        self.slash_prefix = "\\"
        sys = platform.system
        if (sys == "Windows"):
            self.slash_prefix = "\\"
        elif (sys == "Linux"):
            self.slash_prefix = "/"
        
    
    
    