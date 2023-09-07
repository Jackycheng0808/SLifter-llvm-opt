from llvmlite import ir, binding

class Lifter :
    def __init__(self):
        # Initialize LLVM environment
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        self.ir = ir
        
    def LiftModule(self, module, file):
        module.lift(self, file)

    def Shutdown(self):
        # Cleanup LLVM environment
        binding.shutdown()
