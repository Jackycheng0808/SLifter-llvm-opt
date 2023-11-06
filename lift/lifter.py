from llvmlite import ir, binding

class Lifter :
    def __init__(self):
        # Initialize LLVM environment
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        self.ir = ir

    def AddIntrinsics(self, llvm_module):
        # Create thread idx function
        FuncTy = self.ir.FunctionType(self.ir.IntType(32), [])
        IRFunc = self.ir.Function(llvm_module, FuncTy, "thread_idx")

        self.GetThreadIdx = IRFunc
        
    def LiftModule(self, module, file):
        module.lift(self, file)

    def GetIRType(self, TypeDesc):
        if (TypeDesc == "Int32"):
            return self.ir.IntType(32)
        if (TypeDesc == "Float32"):
            return self.ir.FloatType()

        return self.ir.IntType(32)

    def Shutdown(self):
        # Cleanup LLVM environment
        binding.shutdown()
