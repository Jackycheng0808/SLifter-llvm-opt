from basicblock import BasicBlock
from instruction import Instruction

class Function:
    def __init__(self, file):
        self.ParseFunction(file)
        
    def ParseFunction(self, file):
        for line_num, line in enumerate(file.split('\n')):
            if (not ("/*" in line and "*/" in line)):
                continue

            # Get useful content
            items = line.split('*/')
            if (len(items) != 3):
                continue;
            
            # Retrieve instruction ID
            inst_id = self.GetInstNum(items[0])
            # Retrieve instruction opcode
            inst_opcode, rest_content = self.GetInstOpcode(items[1])
            # Retrieve instruction operands
            inst_ops = self.GetInstOperands(rest_content)

            # Create instruction
            inst = Instruction(inst_id, inst_opcode, inst_ops)

    def GetInstNum(self, line):
        items = line.split('/*')
        return items[1]
        
    def GetInstOpcode(self, line):
        items = line.split(';')
        line = (items[0].lstrip())
        items = line.split(' ')
        # Get opcode
        opcode = items[0]
        rest_content = line.replace(items[0], "")
            
        return opcode, rest_content
    
    def GetInstOperands(self, line):
        items = line.split(',')
        ops = []
        for item in items:
            operand = item.lstrip()
            if (operand != ''):
                ops.append(operand)
        return ops
        
    def Lift(self, lifter):
        print("lift function")
        
