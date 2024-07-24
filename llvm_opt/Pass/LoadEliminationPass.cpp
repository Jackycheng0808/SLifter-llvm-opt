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
struct LoadEliminationPass : public PassInfoMixin<LoadEliminationPass> {
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
  bool Changed = false;

  for (auto &BB : F) {
    for (auto II = BB.begin(); II != BB.end();) {
      // Store the next iterator in case we need to erase the current instruction
      auto NextII = std::next(II);
      
      if (NextII == BB.end()) {
        // We've reached the end of the basic block
        break;
      }

      Instruction *Inst = &*II;
      if (!Inst) {
        errs() << "Warning: Null instruction encountered, skipping\n";
        II = NextII;
        continue;
      }

      auto *Store = dyn_cast<StoreInst>(Inst);
      if (!Store) {
        II = NextII;
        continue;
      }

      // errs() << "Found StoreInst: " << *Store << "\n";
      Value *StoreValue = Store->getValueOperand();
      if (!StoreValue) {
        II = NextII;
        continue;
      }

      auto *RHS = dyn_cast<BinaryOperator>(StoreValue);
      if (!RHS) {
        II = NextII;
        continue;
      }

      // errs() << "  RHS is BinaryOperator: " << *RHS << "\n";
      Value *Load1Value = RHS->getOperand(0);
      if (!Load1Value) {
        II = NextII;
        continue;
      }

      auto *Load1 = dyn_cast<LoadInst>(Load1Value);
      if (!Load1) {
        II = NextII;
        continue;
      }

      // errs() << "    Load1 is LoadInst: " << *Load1 << "\n";
      Value *Ptr = Load1->getPointerOperand();
      if (!Ptr) {
        II = NextII;
        continue;
      }

      auto JJ = NextII;
      while (JJ != BB.end()) {
        Instruction *NextInst = &*JJ;
        if (!NextInst) {
          errs() << "Warning: Null NextInst, breaking inner loop\n";
          break;
        }

        auto *Load2 = dyn_cast<LoadInst>(NextInst);
        if (!Load2) {
          ++JJ;
          continue;
        }

        // errs() << "      Found LoadInst: " << *Load2 << "\n";
        if (Load2->getPointerOperand() == Ptr) {
          
          auto KK = std::next(JJ);
          while (KK != BB.end()) {
            Instruction *NextNextInst = &*KK;
            if (!NextNextInst) {
              break;
            }

            auto *StoreNext = dyn_cast<StoreInst>(NextNextInst);
            if (!StoreNext) {
              ++KK;
              continue;
            }

            // errs() << "          Found StoreInst: " << *StoreNext << "\n";
            if (StoreNext->getPointerOperand() == Ptr) {
              Value *StoreNextValue = StoreNext->getValueOperand();
              if (!StoreNextValue) {
                ++KK;
                continue;
              }

              auto *RHSNext = dyn_cast<BinaryOperator>(StoreNextValue);
              if (!RHSNext) {
                ++KK;
                continue;
              }

              errs() << " RHSNext is BinaryOperator: " << *RHSNext << "\n";
              if (RHSNext->getOperand(0) == Load2) {
                errs() << " RHSNext uses Load2\n";
                // Ensure that RHSNext has the expected operand before replacing uses
                if (Load2->hasOneUse() && RHSNext->getOperand(0) == Load2) {
                  // Perform transformation
                  Load2->replaceAllUsesWith(RHS);
                  StoreNext->setOperand(0, RHSNext->getOperand(1));
                  RHSNext->replaceAllUsesWith(RHSNext->getOperand(1));
                  RHSNext->eraseFromParent();
                  Load2->eraseFromParent();
                  Changed = true;
                  II = Store->getIterator();
                  NextII = std::next(II);
                  break;
                } else {
                  errs() << " Load2 does not have the expected uses\n";
                }
              }
            }
            ++KK;
          }
        }
        ++JJ;
      }

      II = NextII;
    }
  }

  return (Changed ? PreservedAnalyses::none() : PreservedAnalyses::all());
}
};
} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "LoadEliminationPass", LLVM_VERSION_STRING,
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, FunctionPassManager &FPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "load-elimination") {
            FPM.addPass(LoadEliminationPass());
            return true;
          }
          return false;
        }
      );
    }
  };
}