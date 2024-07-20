clang++ -fPIC -shared -o LoadEliminationPass.so LoadEliminationPass.cpp `llvm-config --cxxflags --ldflags --system-libs --libs core passes`
opt -load-pass-plugin=./LoadEliminationPass.so -passes="load-elimination" -S code_case1.ll -o code_case1_opt.ll

clang++ -fPIC -shared -o CoalescingPass.so CoalescingPass.cpp `llvm-config --cxxflags --ldflags --system-libs --libs core passes`
opt -load-pass-plugin=./CoalescingPass.so -passes="coalescing" -S code_case2.ll -o code_case2_opt.ll