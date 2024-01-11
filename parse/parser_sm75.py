from sir.function import Function
from sir.basicblock import BasicBlock
from sir.instruction import Instruction
from sir.controlcode import ControlCode
from sir.operand import Operand
from sir.operand import InvalidOperandException

from parse.parser_base import SaSSParserBase

SM75_CTLCODE_LEN = 1

class SaSSParser_SM35(SaSSParserBase):
    def __init__(self, isa, file):
        self.file = file

    # Parse the SaSS text file
    def applyx(self):
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

        # Parse the function body from file lines
    def ParseFuncBody(self, line, Insts, CurrFunc):
        # Process function body 
        items = line.split('*/')
        if len(items) == 2:
            # Parse the control code
            self.ParseControlCode(items[0], self.CtlCodes)
        elif len(items) == 3:    
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

            # Add control code
            if len(self.CtlCodes) > 0:
                CtlCode = self.CtlCodes[0]
                inst.SetCtlCode(CtlCode)
                # Remove the control code from temprory storage
                self.CtlCodes.remove(CtlCode)
            else:
                raise UnmatchedControlCode
            
            # Add instruction into list
            Insts.append(inst)
            
    # Parse control code 
    def ParseControlCode(self, Content, ControlCodes):
        Content = Content.replace("/*", "")
        Content = Content.replace(" ", "")

        # This parsing process is correspoinding to Volta and Turing architecture, which 
        # has one 17-bits sections in the top part of 128-bits instruction

        # Extract control sections
        Sec = Content[2 : 8]

        Sec1Num = int("0x" + Sec, 16) & int("0xffffe", 16)
        
        Stall = (SecNum & 15) >> 0
        Yield = (SecNum & 16) >> 4
        WrtB  = (SecNum & 224) >> 5
        ReadB = (SecNum & 1792) >> 8
        WaitB = (SecNum & 129024) >> 11
        ControlCodes.append(ControlCode(Content, WaitB, ReadB, WrtB, Yield, Stall))
        
        return ControlCodes
      
