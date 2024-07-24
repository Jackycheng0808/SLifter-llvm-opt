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
      if (auto *GEP1 = dyn_cast<GetElementPtrInst>(&*I)) {
        auto *Load1 = findNextLoad(I, E);
        if (!Load1 || !Load1->getType()->isIntegerTy(32)) {
          ++I;
          continue;
        }

        auto NextGEP = std::next(I);
        while (NextGEP != E && !isa<GetElementPtrInst>(*NextGEP)) {
          ++NextGEP;
        }

        if (NextGEP == E) {
          ++I;
          continue;
        }

        auto *GEP2 = cast<GetElementPtrInst>(&*NextGEP);
        auto *Load2 = findNextLoad(NextGEP, E);

        if (!Load2 || !Load2->getType()->isIntegerTy(32)) {
          ++I;
          continue;
        }

        // Check if both GEPs have the same base pointer
        if (GEP1->getPointerOperand() == GEP2->getPointerOperand()) {
          if (Load1->getPointerOperand() == GEP1 && Load2->getPointerOperand() == GEP2) {
            if (GEP1->getNumOperands() > 1 && GEP2->getNumOperands() > 1) {
              // Check if the indices are continuous
              auto *Idx1 = dyn_cast<ConstantInt>(GEP1->getOperand(GEP1->getNumOperands() - 1));
              auto *Idx2 = dyn_cast<ConstantInt>(GEP2->getOperand(GEP2->getNumOperands() - 1));
              if (Idx1 && Idx2 && Idx2->getSExtValue() == Idx1->getSExtValue() + 1) {
                IRBuilder<> Builder(&BB);
                Builder.SetInsertPoint(GEP1);

                // Create a new GEP instruction
                Value *NewGEP = Builder.CreateGEP(GEP1->getSourceElementType(), 
                                                  GEP1->getPointerOperand(), 
                                                  {ConstantInt::get(Type::getInt32Ty(F.getContext()), Idx1->getSExtValue())});

                // Create a new load instruction with i64 type
                Value *NewPtr = Builder.CreateBitCast(NewGEP, Type::getInt64Ty(F.getContext())->getPointerTo());
                LoadInst *NewLoad = Builder.CreateLoad(Type::getInt64Ty(F.getContext()), NewPtr);
                NewLoad->setName("coalesced_load");
                NewLoad->setAlignment(Align(8));

                // Extract the two i32 values from the i64
                Value *LowerBits = Builder.CreateTrunc(NewLoad, Type::getInt32Ty(F.getContext()), "R5_val");
                Value *UpperBits = Builder.CreateLShr(NewLoad, 32);
                UpperBits = Builder.CreateTrunc(UpperBits, Type::getInt32Ty(F.getContext()), "R6_val");

                Load1->replaceAllUsesWith(LowerBits);
                Load2->replaceAllUsesWith(UpperBits);

                // Remove the old instructions
                Load2->eraseFromParent();
                GEP2->eraseFromParent();
                Load1->eraseFromParent();
                GEP1->eraseFromParent();

                Changed = true;
                I = NewLoad->getIterator();
                continue;
              }
            }
          }
        }
      }
      ++I;
    }
  }

  return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
  }

private:
  LoadInst* findNextLoad(BasicBlock::iterator I, BasicBlock::iterator E) {
    while (I != E) {
      if (auto *Load = dyn_cast<LoadInst>(&*I)) {
        return Load;
      }
      ++I;
    }
    return nullptr;
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