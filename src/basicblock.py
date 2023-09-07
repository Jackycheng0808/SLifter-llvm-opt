from instruction import Instruction

class BasicBlock:
    def __init__(self):
        self.instructions = []
        
    def Lift(self, lifter):
        print("print basic block")
