from lift.lifter import Lifter

REG_PREFIX = 'R'
ARG_PREFIX = 'c[0x0]'
ARG_OFFSET = 320 # 0x140
THREAD_IDX = 'SR_TID'

class InvalidOperandException(Exception):
    pass

class Operand:
    def __init__(self, Name, Reg, Suffix, ArgOffset, IsReg, IsArg, IsDim, IsThreadIdx):
        self.Name = Name
        self.Reg = Reg
        self.Suffix = Suffix
        self.ArgOffset = ArgOffset
        self.IsReg = IsReg
        self.IsArg = IsArg
        self.IsDim = IsDim
        self.IsThreadIdx = IsThreadIdx
        self.Skipped = False
        
        self.TypeDesc = "NOTYPE"
        self.IRType = None
        self.IRRegName = None
        
    # Set the type description for operand
    def SetTypeDesc(self, Ty):
        self.TypeDesc = Ty

    # Get the type description
    def GetTypeDesc(self):
        return self.TypeDesc
    
    def GetIRType(self, lifter):
        if self.IRType == None:
            self.IRType = lifter.GetIRType(self.TypeDesc)

        return self.IRType

    def GetIRRegName(self, lifter):
        if self.IRRegName == None:
            self.IRRegName = self.Reg + self.TypeDesc

        return self.IRRegName
    
    def dump(self):
        print("operand: ", self.Name, self.Reg)
    
