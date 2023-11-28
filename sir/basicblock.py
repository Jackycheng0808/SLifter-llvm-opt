from sir.instruction import Instruction

class BasicBlock:
    def __init__(self, addr_content, ControlCode):
        # The address of the start of this basic block
        self.addr_content = addr_content
        # Calculate the integer offset
        self.addr = int(addr_content, base = 16)
        # Instruction list
        self.instructions = []
        # Predecessor
        self.preds = []
        # Successors
        self.succs = []
        # Control Code
        self.ControlCode = ControlCode

    def AppendInst(self, inst):
        self.instructions.append(inst)
        
    def AddPred(self, pred):
        if pred not in self.preds:
            self.preds.append(pred)

    def AddSucc(self, succ):
        if succ not in self.succs:
            self.succs.append(succ)

    def HasBranch(self):
        for inst in self.instructions:
            if inst.IsBranch():
                return True
            
        return False

    def GetBranchTarget(self):
        for i in range(len(self.instructions)):
            inst = self.instructions[i]
            if inst.IsBranch():
                if i == len(self.instructions) - 1:
                    # The last instruction in basic block
                    return self.addr + 64
                else:
                    # Not the last instruction in basic block
                    if self.instructions[len(self.instructions) - 1].IsExit():
                        return self.addr + 32
                    
        return 0

    def GetDirectTarget(self, NextBB):
        TargetInst = NextBB.instructions[0]
        if TargetInst.IsExit():
            return NextBB.addr

        return 0

    # Merge congtent with another basic block
    def Merge(self, another):
        # Append instruction list
        self.instructions = self.instructions + another.instructions
        # Erase old successor
        if another in self.succs:
            self.succs.remove(another)
        # Add new successor
        self.succs = self.succs + another.succs
        
    # Erase the redundency in basic block
    def EraseRedundency(self):
        inst = self.instructions[0]
        if inst.IsExit():
            # Empty the instruction list and just keep the exit instruction
            self.instructions = []
            self.instructions.append(inst)

    # Collect registers with type
    def GetRegs(self, Regs, lifter):
        for Inst in self.instructions:
            Inst.GetRegs(Regs, lifter)
        
    def Lift(self, lifter, IRBuilder, IRRegs, IRArgs, BlockMap, IRFunc):
        for i in range(len(self.instructions)):
            Inst = self.instructions[i]
            if Inst.IsBranch():
                if i < len(self.instructions) - 1:
                    NextInst = self.instructions[i + 1]
                    if NextInst.IsExit():
                        # Append a basic block to perofrm exit operation
                        ExitBlock = IRFunc.append_basic_block("Internal_Exit")
                        ExitIRBuilder = lifter.ir.IRBuilder(ExitBlock)
                        # Add exit instruction
                        ExitIRBuilder.ret_void()
                    
                        # Setup jump target
                        TrueBr = ExitBlock
                        FalseBr = BlockMap[self.succs[0]]
                        # Lift branch instruction
                        Inst.LiftBranch(lifter, IRBuilder, IRRegs, IRArgs, TrueBr, FalseBr)
                        
                        break

            # Lift instruction
            Inst.Lift(lifter, IRBuilder, IRRegs, IRArgs)
        
    def dump(self):
        print("BB Addr: ", self.addr_content)
        for inst in self.instructions:
            inst.dump();
        print("BB End-------------")
        
