class Operand:
    def __init__(self, operand):
        self.operand = operand
        self.ParseOperand(operand)

    def ParseOperand(self, operand):
        # Check if it is a register
        self.IsReg = True
        
        # Check if it is a function argument

        
        # check if it is a special value
