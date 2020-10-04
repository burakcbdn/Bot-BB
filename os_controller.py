import platform
class osController:

    def __init__(self):
        self.slash_prefix = "\\"
        sys = platform.system
        if (sys == "Windows"):
            self.slash_prefix = "\\"
        else if (sys == "Linux"):
            self.slash_prefix = "/"
        
    
    
    