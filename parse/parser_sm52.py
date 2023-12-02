from sir.function import Function
from sir.basicblock import BasicBlock
from sir.instruction import Instruction
from sir.controlcode import ControlCode
from sir.operand import Operand
from sir.operand import InvalidOperandException

REG_PREFIX = 'R'
ARG_PREFIX = 'c[0x0]'
ARG_OFFSET = 320 # 0x140
THREAD_IDX = 'SR_TID'

PTRREG_PREFIX = '[R'
PTR_PREFIX = '['
PTR_SUFFIX = ']'

class SaSSParser_SM52:
    def __init__(self, isa, file):
        self.file = file

    # Parse the SaSS text file
    def apply(self):
        # List of functions
        Funcs = []
        # List of basic blocks in current function
        Blocks = []
    
        # If the current loop iteration is parsing function
        IsParsingFunc = False
        # If the current loop iteration is parsing basic block
        IsParsingBB = False
        
        # Current function
        CurrFunc = None
        # Current basic block
        CurrBB = None
        # Current control code associated with basic block
        CurrCtrCode = None
        
        # Main loop that parses the SaSS text file
        for line_num, line in enumerate(self.file.split('\n')):
            # Process lines in SaSS text file

            # Process function title and misc
            if (not ("/*" in line and "*/" in line)):
                # Check function start
                if ("Function : " in line):
                    # Wrap up previous function
                    if IsParsingFunc and CurrFunc != None:
                        CurrFunc.blocks = self.CreateCFG(Blocks)
                        # Reset current function, list of basic blocks and instructions
                        Func = None
                        Blocks = []
                
                    items = line.split(' : ')

                    # Create new function
                    CurrFunc = Function(items[1])
                    Funcs.append(CurrFunc);
                    
                    # Setup the flags that for parsing function
                    IsParsingFunc = True
                continue

            # Process function body 
            items = line.split('*/')
            if len(items) == 2:
                # This is the interval between code sections, and represent control branch
                IsParsingBB = False

                # Parse the control code
                CurrCtrCodes = self.ParseControlCode(items[0])
                
                continue;
            elif len(items) == 3 and not IsParsingBB:
                # Set the flag to start a new basic block 
                IsParsingBB = True

                # Create a new basic block
                CurrBB = BasicBlock(self.GetInstNum(items[0]), CurrCtrCode)
                CurrBB.ControlCodes = CurrCtrCodes
                Blocks.append(CurrBB)
                
            # Retrieve instruction ID
            inst_id = self.GetInstNum(items[0])
            # Retrieve instruction opcode
            inst_opcode, rest_content = self.GetInstOpcode(items[1])
            rest_content = rest_content.replace(" ", "")
            if (rest_content == "EXIT"):
                # Special case for exit instruction
                inst_ops = inst_opcode
                inst_opcode = rest_content
            else:
                # Retrieve instruction operands
                inst_ops = self.GetInstOperands(rest_content)
            
            # Create instruction
            inst = self.ParseInstruction(inst_id, inst_opcode, inst_ops, rest_content, CurrFunc)

            # Add instruction into list
            CurrBB.AppendInst(inst)

        # Wrap up previous function
        if IsParsingFunc and CurrFunc != None:
            CurrFunc.blocks = self.CreateCFG(Blocks)

        CurrFunc.DumpCFG()
        
        return Funcs

    # Retrieve instruction ID
    def GetInstNum(self, line):
        items = line.split('/*')
        return items[1]
    
    # Retrieve instruction's opcode
    def GetInstOpcode(self, line):
        items = line.split(';')
        line = (items[0].lstrip())
        items = line.split(' ')
        # Get opcode
        opcode = items[0]
        rest_content = line.replace(items[0], "")
            
        return opcode, rest_content

    # Retrieve instruction's operands
    def GetInstOperands(self, line):
        items = line.split(',')
        ops = []
        for item in items:
            operand = item.lstrip()
            if (operand != ''):
                ops.append(operand)

        return ops 

    # Parse instruction, includes operators and operands
    def ParseInstruction(self, InstID, Opcode_Content, Operands_Content, Operands_Detail, CurrFunc):
        # Parse opcodes
        Opcodes = Opcode_Content.split('.')

        # Parse operands
        Operands = []
        for Operand_Content in Operands_Content:
            Operands.append(self.ParseOperand(Operand_Content, CurrFunc))

        # Create instruction
        return Instruction(InstID, Opcodes, Operands, Opcode_Content + " " + Operands_Detail)

    # Parse operand
    def ParseOperand(self, Operand_Content, CurrFunc):
        Operand_Content = Operand_Content.lstrip()
        IsReg = False
        Reg = None
        Name = None
        Suffix = None
        ArgOffset = -1
        IsArg = False
        IsDim = False
        IsThreadIdx = False

        # Check if it is a register for address pointer, e.g. [R0]
        if Operand_Content.find(PTRREG_PREFIX) == 0: # operand starts from '[R'
            # Fill out the ptr related charactors
            Operand_Content = Operand_Content.replace(PTR_PREFIX, "")
            Operand_Content = Operand_Content.replace(PTR_SUFFIX, "")

            # print("revised op content: ", Operand_Content)
            
        # Check if it is a register
        if Operand_Content.find(REG_PREFIX) == 0: # operand starts from 'R'
            IsReg = True
            Reg = Operand_Content
            Name = Operand_Content
            
            # Get the suffix of given operand
            items = Operand_Content.split('.')
            if len(items) > 1:
                Reg = items[0]
                Suffix = items[1]
                if len(items) > 2:
                    raise InvalidOperandException
                
            return Operand(Name, Reg, Suffix, ArgOffset, IsReg, IsArg, IsDim, IsThreadIdx)
        
        # Check if it is a function argument or dimension related value
        if Operand_Content.find(ARG_PREFIX) == 0: 
            IsArg = True

            # Get the suffix of given operand
            items = Operand_Content.split('.')
            if len(items) > 1:
                Suffix = items[1]
                if len(items) > 2:
                    raise InvalidOperandException

                Operand_Content = items[0]
        
            ArgOffset = self.GetArgOffset(Operand_Content.replace(ARG_PREFIX, ""))
            # print("compare: ", ARG_OFFSET, self.ArgOffset)
            if ArgOffset < ARG_OFFSET:
                IsArg = False
                IsDim = True

            # Create argument operaand
            Arg = Operand(Name, Reg, Suffix, ArgOffset, IsReg, IsArg, IsDim, IsThreadIdx)

            # Register argument to function
            CurrFunc.RegisterArg(ArgOffset, Arg)

            return Arg
        
        # Check if it is a special value
        items = Operand_Content.split('.')
        if len(items) == 2:
            if items[0].find(THREAD_IDX) == 0:                
                IsThreadIdx = True
                Suffix = items[1]

        return Operand(Name, Reg, Suffix, ArgOffset, IsReg, IsArg, IsDim, IsThreadIdx)

    # Parse the argument offset
    def GetArgOffset(self, offset):
        offset = offset.replace('[', "")
        offset = offset.replace(']', "")
        return int(offset, base = 16)

    # Parse control code 
    def ParseControlCode(self, Content):
        ControlCodes = []
        Content = Content.replace("/*", "")
        Content = Content.replace(" ", "")

        # This parsing process is correspoinding to Maxwell architecture, which has
        # 3 17-bits sections for control and 3 4-bits sections for reuse

        # Extract control sections
        Sec1 = Content[2 : 7]
        Sec2 = Content[8 : 13]
        Sec3 = Content[13 : ]
        Sec1Num = int("0x" + Sec1, 16) & int("0x7fffc", 16)
        Sec2Num = int("0x" + Sec2, 16) & int("0x3fffe", 16)
        Sec3Num = int("0x" + Sec3, 16) & int("0x1ffff", 16)

        Stall = (Sec3Num & 15) >> 0
        Yield = (Sec3Num & 16) >> 4
        WrtB  = (Sec3Num & 224) >> 5
        ReadB = (Sec3Num & 1792) >> 8
        WaitB = (Sec3Num & 129024) >> 11
        ControlCodes.append(ControlCode(Content, WaitB, ReadB, WrtB, Yield, Stall))
        
        Stall = (Sec2Num & 15) >> 0
        Yield = (Sec2Num & 16) >> 4
        WrtB  = (Sec2Num & 224) >> 5
        ReadB = (Sec2Num & 1792) >> 8
        WaitB = (Sec2Num & 129024) >> 11
        ControlCodes.append(ControlCode(Content, WaitB, ReadB, WrtB, Yield, Stall))
        
        Stall = (Sec1Num & 15) >> 0
        Yield = (Sec1Num & 16) >> 4
        WrtB  = (Sec1Num & 224) >> 5
        ReadB = (Sec1Num & 1792) >> 8
        WaitB = (Sec1Num & 129024) >> 11
        ControlCodes.append(ControlCode(Content, WaitB, ReadB, WrtB, Yield, Stall))
        # print("flags ", int("0xf", 16), int("0x10", 16), int("0xe0", 16), int("0x700", 16), int("0x1f800", 16))

        return ControlCodes
        
    # Create the control-flow graph
    def CreateCFG(self, Blocks):
        # No need to process single basic block case
        if len(Blocks) == 1:
            return Blocks

        # Handle the multi-block case
        JumpTargets = {}
        for i in range(len(Blocks)):
            CurrBB = Blocks[i]
            # Handle branch target case: the branch instruciton locates in current basic block
            self.CheckAndAddTarget(CurrBB, CurrBB.GetBranchTarget(), JumpTargets)
 
            # Handle the direct target case: the next basic block contains exit instruction
            if i < len(Blocks) - 1:
                self.CheckAndAddTarget(CurrBB, CurrBB.GetDirectTarget(Blocks[i + 1]), JumpTargets)
            # print("Target ", CurrBB.addr)

        MergedTo = {}
        NewBlocks = []
        CurrBB = None
        for i in range(len(Blocks)):
            NextBB = Blocks[i]
            # Add CFG connection to its jump source
            if NextBB.addr in JumpTargets:
                for TargetBB in JumpTargets[NextBB.addr]:
                    if TargetBB in MergedTo:
                        TargetBB = MergedTo[TargetBB]
                    
                    TargetBB.AddSucc(NextBB)
                    NextBB.AddPred(TargetBB)
                    print("Connect BB: ", TargetBB.addr_content, NextBB.addr_content)
                # Reset current basic block, i.e. restart potential merging
                CurrBB = None
                
            # Handle the basic block merge case
            if CurrBB != None and NextBB.addr not in JumpTargets:
                # Merge two basic blocks
                CurrBB.Merge(NextBB)
                MergedTo[NextBB] = CurrBB
                # print("Merge BB: ", CurrBB.addr_content, NextBB.addr_content)

                continue
            
            if CurrBB == None:
                # Reset current basic block
                CurrBB = NextBB
                # Add current basic block to translated block list
                NewBlocks.append(CurrBB)

        for NewBB in NewBlocks:
            NewBB.EraseRedundency()
            # NewBB.dump()
                
        return NewBlocks

    # Check if the target address is legal, then add the target address associated with its jump source
    def CheckAndAddTarget(self, CurrBB, TargetAddr, JumpTargets):
        if TargetAddr > 0:
            if TargetAddr not in JumpTargets:
                JumpTargets[TargetAddr] = []
            JumpTargets[TargetAddr].append(CurrBB)
            # print("Add Jump Target: ", TargetAddr, CurrBB.addr_content)
