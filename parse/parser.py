from parse.parser_sm52 import SaSSParser_SM52

class SaSSParser:
    def __init__(self, isa, file):
        print("parse ", isa)
        self.file = file
        if isa == "sm_52":
            self.parser = SaSSParser_SM52(isa, file)
            
    # Parse the SaSS text file
    def apply(self):
        return self.parser.apply()
        
