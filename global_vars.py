class GlobalVars:

    _instance = None

    def __init__(self):
       
        if GlobalVars._instance is not None:
            return GlobalVars._instance
       
        super().__init__()
        self.weights_path = ""
        self.threshold = 0.7 
        self.fps = 30

        GlobalVars._instance = self

    @staticmethod
    def get_instance():
        if GlobalVars._instance is None:
            GlobalVars()
        return GlobalVars._instance        