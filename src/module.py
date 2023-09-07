from function import Function
from llvmlite import ir, binding

class Module :
    def __init__(self, name, file):
        self.name = name

        # Parse the module
        self.ParseModule(file)

    def ParseModule(self, file):
        self.func = self.ParseFunction(file)

    def ParseFunction(self, file):
        return Function(file)

    def Lift(self, lifter, outfile):
        # Generate module level information
        llvm_module = lifter.ir.Module(self.name)

        # Lift function
        self.func.Lift(lifter)

        # Generate IR file 
        print(llvm_module, file = outfile)
        
