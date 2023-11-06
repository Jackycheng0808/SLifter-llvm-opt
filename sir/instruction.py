from sir.operand import Operand

class UnsupportedOperatorException(Exception):
    pass

class InvalidTypeException(Exception):
    pass

class Instruction:
    def __init__(self, id, opcodes, operands):
        self.id = id
        self.opcodes = opcodes
        self.operands = operands
        self.TwinIdx = ""

    def GetArgsAndRegs(self):
        regs = []
        args = []
        for operand in self.operands:
            if operand.IsReg:
                regs.append(operand)
            if operand.IsArg:
                args.append(operand)

        return args, regs

    def IsExit(self):
        return self.opcodes[0] == "EXIT"

    def IsBranch(self):
        return self.opcodes[0] == "ISETP"

    def IsBinary(self):
        return self.opcodes[0] == "FFMA" or self.opcodes[0] == "FADD" or self.opcodes[0] == "XMAD" or self.opcodes[0] == "SHL" or self.opcodes[0] == "SHR" or self.opcodes[0] == "S2R"
    
    def IsNOP(self):
        return self.opcodes[0] == "NOP"

    def IsAddrCompute(self):
        if self.opcodes[0] == "IADD":
            # Check operands
            if len(self.operands) == 3:
                operand = self.operands[2]
                # Check function argument operand
                return operand.IsArg

        return False

    def IsLoad(self):
        return self.opcodes[0] == "LDG"

    def IsStore(self):
        return self.opcodes[0] == "STG"
    
    def ResolveType(self):
        if not self.DirectlySolveType():
            if not self.PartialSolveType():
                raise UnsupportedOperatorException

    # Collect registers used in instructions
    def GetRegs(self, Regs, lifter):
        # Check twin instruction case
        TwinIdx = self.TwinIdx
        
        for Operand in self.operands:
            if Operand.IsReg:
                if TwinIdx.find(Operand.Reg) == 0:
                    if not Operand.TypeDesc == "NOTYPE":
                        RegName = TwinIdx + Operand.TypeDesc
                        Regs[RegName] = Operand
                else:
                    if not Operand.TypeDesc == "NOTYPE":
                        Regs[Operand.GetIRRegName(lifter)] = Operand
        
    # Get def operand
    def GetDef(self):
        return self.operands[0]

    # Get use operand
    def GetUses(self):
        Uses = []
        for i in range(1, len(self.operands)):
            Uses.append(self.operands[i])

        return Uses

    # Check and update the use operand's type from the givenn operand
    def CheckAndUpdateUseType(self, Def):
        for i in range(1, len(self.operands)):
            CurrOperand = self.operands[i]
            if CurrOperand.Name == Def.Name:
                CurrOperand.SetTypeDesc(Def.TypeDesc)
                return True

        return False
    
    # Check and update the def operand's type from the given operands
    def CheckAndUpdateDefType(self, Uses):
        Def = self.operands[0]
        for i in range(len(Uses)):
            CurrUse = Uses[i]
            if CurrUse.Name == Def.Name:
                Def.SetTypeDesc(CurrUse.TypeDesc)
                return True

        return False
    
    # Directly resolve the type description, this is mainly working for binary operation
    def DirectlySolveType(self):
        TypeDesc = None
        if self.opcodes[0] == "FFMA":
            TypeDesc = "Float32"
        elif self.opcodes[0] == "FADD":
            TypeDesc = "Float32"
        elif self.opcodes[0] == "XMAD":
            TypeDesc = "INT"
        elif self.opcodes[0] == "SHL":
            TypeDesc = "INT"
        elif self.opcodes[0] == "SHR":
            TypeDesc = "INT"
        elif self.opcodes[0] == "S2R":
            TypeDesc = "INT"
        elif self.opcodes[0] == "ISETP":
            TypeDesc = "INT"
        else:
            return False
        
        for operand in self.operands:
            operand.SetTypeDesc(TypeDesc)

        return True
    
    def PartialSolveType(self):
        if self.opcodes[0] == "LDG":
            TypeDesc = self.operands[0].GetTypeDesc()
            if TypeDesc != None:
                self.operands[1].SetTypeDesc(TypeDesc + "_PTR")
            else:
                TypeDesc = self.operands[1].GetTypeDesc()
                if TypeDesc != None:
                    self.operands[0].SetTypeDesc(TypeDesc.replace('_PTR', ""))
                else:
                    raise InvalidTypeException
        elif self.opcodes[0] == "STG":
            TypeDesc = self.operands[1].GetTypeDesc()
            if TypeDesc != None:
                self.operands[0].SetTypeDesc(TypeDesc + "_PTR")
            else:
                TypeDesc = self.operands[0].GetTypeDesc()
                if TypeDesc != None:
                    self.operands[0].SetTypeDesc(TypeDesc.replace('_PTR', ""))
                else:
                    raise InvalidTypeException
        elif self.opcodes[0] == 'IADD':
            TypeDesc = self.operands[0].GetTypeDesc()
            if TypeDesc != None:
                self.operands[1].SetTypeDesc(TypeDesc)
                self.operands[2].SetTypeDesc(TypeDesc)
        else:
            return False

        return True

    def Lift(self, lifter, IRBuilder, IRRegs, IRArgs):
        if self.opcodes[0] == "EXIT":
            IRBuilder.ret_void()
        elif self.opcodes[0] == "FADD":
            Res = self.operands[0]
            Op1 = self.operands[1]
            Op2 = self.operands[2]
            if Res.IsReg and Op1.IsReg and Op2.IsReg:
                IRRes = IRRegs[Res.GetIRRegName(lifter)]
                IROp1 = IRRegs[Op1.GetIRRegName(lifter)]
                IROp2 = IRRegs[Op2.GetIRRegName(lifter)]
            
                # Load operands
                Load1 = IRBuilder.load(IROp1, "load")
                Load2 = IRBuilder.load(IROp2, "load")

                # FADD instruction
                IRVal = IRBuilder.add(Load1, Load2, "fadd")

                # Store result
                IRBuilder.store(IRVal, IRRes)
                
        elif self.opcodes[0] == "ISETP":
            for i in range(1, len(self.operands)):
                Operand = self.operands[i]

        elif self.opcodes[0] == "SHL":
            ResOp = self.operands[0]
            Op1 = self.operands[1]

            if ResOp.IsReg and Op1.IsReg:
                IRRes = IRRegs[ResOp.GetIRRegName(lifter)]
                IROp1 = IRRegs[Op1.GetIRRegName(lifter)]

                # Load value
                Load1 = IRBuilder.load(IROp1, "load")

                # Add 0
                IRVal = IRBuilder.add(Load1, lifter.ir.Constant(lifter.ir.IntType(32), 0), "add")

                # Store result
                IRBuilder.store(IRVal, IRRes)
                
        elif self.opcodes[0] == "IADD":
            ResOp = self.operands[0]
            Op1 = self.operands[1]
            Op2 = self.operands[2]
                
            #if Op1.IsReg and Op2.IsArg:
                #IRRes = IRRegs[ResOp.GetIRRegName(lifter)];
                #IROp1 = IRRegs[Op1.GetIRRegName(lifter)]
                #IROp2 = IRArgs[Op2.ArgOffset]

                # Load values
                #Load1 = IRBuilder.load(IROp1, "load")
                #Load2 = IRBuilder.load(IROp2, "load")

                # Add operands
                #IRVal = IRBuilder.gep(Load2, Load1, "addr")

                # Store the value
                #IRBuilder.store(IRVal, IRRes)
                
        elif self.opcodes[0] == "S2R":
            ResOp = self.operands[0]
            ValOp = self.operands[1]
            if ValOp.IsThreadIdx and ResOp.IsReg:
                IRResOp = IRRegs[ResOp.GetIRRegName(lifter)]
                
                # Call thread idx operation
                IRVal = IRBuilder.call(lifter.GetThreadIdx, [], "ThreadIdx")

                # Store the result
                IRBuilder.store(IRVal, IRResOp)
                
        elif self.opcodes[0] == "LDG":
            PtrOp = self.operands[1]
            ValOp = self.operands[0]
            if PtrOp.IsReg and ValOp.IsReg:
                IRPtrOp = IRRegs[PtrOp.GetIRRegName(lifter)]
                IRValOp = IRRegs[ValOp.GetIRRegName(lifter)]

                # Load operands
                LoadPtr = IRBuilder.load(IRPtrOp, "load")

                # Type convert
                Addr = IRBuilder.inttoptr(LoadPtr, lifter.ir.PointerType(lifter.ir.FloatType()), "cast")
                
                # Load instruction
                IRRes = IRBuilder.load(Addr, "load_inst")

                # Store the result
                IRBuilder.store(IRRes, IRValOp)
        elif self.opcodes[0] == "STG":
            PtrOp = self.operands[0]
            ValOp = self.operands[1]
            if PtrOp.IsReg and ValOp.IsReg:
                IRPtrOp = IRRegs[PtrOp.GetIRRegName(lifter)]
                IRValOp = IRRegs[ValOp.GetIRRegName(lifter)]

                # Load operands
                LoadPtr = IRBuilder.load(IRPtrOp, "load")
                LoadVal = IRBuilder.load(IRValOp, "load")

                # Type convert
                Addr = IRBuilder.inttoptr(LoadPtr, lifter.ir.PointerType(lifter.ir.FloatType()), "cast"
                )
                # Store instruction
                IRBuilder.store(LoadVal, Addr)
                
    def dump(self):
        for operand in self.operands:
            operand.dump()
        
