from operand import Operand

class Instruction:
    def __init__(self, id, opcode, operands):
        self.id = id
        self.opcode = opcode
        self.operands = [] 
        self.insts = []
        # Check the instruction's detail
        self.ParseInstruction(opcode, operands)
        
    def ParseInstruction(self, opcode, operands):
        # Check the case of composed instruction opcode
        self.CheckComposion(opcode)
        
        # Check the operands
        self.CheckOperands(operands)

    def CheckComposion(self, opcode):
        opcodes = opcode.split('.')

    def CheckOperands(self, operands):
        for operand in operands:
            self.operands.append(Operand(operand))
            
    def Lift(self, lifter):
        print("print instruciton ")

