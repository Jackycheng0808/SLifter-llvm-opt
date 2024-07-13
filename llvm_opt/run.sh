#!/bin/bash

# ===========================================
# Part 1: Convert SASS to LLVM (SASS Lifter)
# ===========================================

# Generate .ll from SASS using the provided Python script
echo "Part 1: Converting SASS to LLVM..."
python ../main.py -i file/addMatrices.sass -o exp/addMatrices

# Ensure the output directory exists
dir_name="exp"

if [ ! -d "$dir_name" ]; then
    mkdir "$dir_name"
    echo "Directory '$dir_name' created."
fi

# Copy the generated .ll file for further modifications
cp exp/addMatrices.ll exp/addMatrices_mod.ll

# Post-processing
python convert_add_to_fadd.py exp/addMatrices_mod.ll
echo "SASS to LLVM conversion done."

# ==============================
# Part 2: LLVM Optimization
# ==============================

echo "Part 2: Optimizing LLVM IR..."
# Optimize the modified LLVM IR file
opt -passes='mem2reg' -S exp/addMatrices_mod.ll -o exp/addMatrices_mod_opt.ll
# opt -passes='dce' -S exp/addMatrices_mod_opt.ll -o exp/addMatrices_mod_opt.ll
# opt -passes='instsimplify' -S exp/addMatrices_mod_opt.ll -o exp/addMatrices_mod_opt.ll

# opt -O1 exp/addMatrices_mod.ll -o exp/addMatrices_mod_opt.ll
# opt -O1  exp/addMatrices_mod.ll

echo "LLVM optimization done."

# =========================
# Part 3: Code Generation
# =========================

echo "Part 3: Code Generation..."
# Compile the optimized LLVM IR to an object file for macOS-arm64
llc -filetype=obj -mtriple=aarch64-apple-darwin exp/addMatrices_mod_opt.ll -o exp/addMatrices.o

# Link the object file to create an executable
clang -target arm64-apple-macosx11.0.0 exp/addMatrices.o -o exp/addMatrices

echo "Code generation done."

# =========================
# Part 4: Running and Testing
# =========================

echo "Part 4: Running the addMatrices program..."

# Execute the program and measure the running time
start_time_sec=$(date +%s)
start_time_nsec=$(date +%N)
./exp/addMatrices
end_time_sec=$(date +%s)
end_time_nsec=$(date +%N)

# Calculate execution time in milliseconds
start_time=$((start_time_sec * 1000000000 + start_time_nsec))
end_time=$((end_time_sec * 1000000000 + end_time_nsec))
execution_time=$((end_time - start_time))
execution_time_in_ms=$((execution_time / 1000000))

echo "Execution time: $execution_time_in_ms ms"

echo "All steps completed successfully."