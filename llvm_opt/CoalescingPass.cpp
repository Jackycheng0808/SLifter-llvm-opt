#include "llvm/IR/PassManager.h"
#include "llvm/IR/PatternMatch.h"
#include "llvm/Pass.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;
using namespace llvm::PatternMatch;

namespace {
struct CoalescingPass : public PassInfoMixin<CoalescingPass> {
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
    bool Changed = false;

    for (auto &BB : F) {
      for (auto I = BB.begin(), E = BB.end(); I != E; ) {
        // Look for getelementptr instruction
        if (auto *GEP = dyn_cast<GetElementPtrInst>(&*I)) {
          auto NextI = std::next(I);
          if (NextI != E) {
            // Check if the next instruction is a load
            if (auto *Load = dyn_cast<LoadInst>(&*NextI)) {
              // Check if the load uses the result of the getelementptr
              if (Load->getPointerOperand() == GEP) {
                // Create a new load instruction with double type
                IRBuilder<> Builder(&BB);
                Builder.SetInsertPoint(Load);
            Value *NewPtr = Builder.CreateBitCast(GEP->getPointerOperand(), Type::getDoubleTy(F.getContext())->getPointerTo());
                LoadInst *NewLoad = Builder.CreateLoad(Type::getDoubleTy(F.getContext()), NewPtr);
                NewLoad->setName(Load->getName().str() + "_dval");

                // Replace uses of the old load with the new one
                Load->replaceAllUsesWith(NewLoad);

                // Remove the old instructions
                Load->eraseFromParent();
                GEP->eraseFromParent();

                Changed = true;
                I = NewLoad->getIterator();
                continue;
              }
            }
          }
        }
        ++I;
      }
    }

    return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
  }
};
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "CoalescingPass", LLVM_VERSION_STRING,
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, FunctionPassManager &FPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "coalescing") {
            FPM.addPass(CoalescingPass());
            return true;
          }
          return false;
        });
    }
  };
}