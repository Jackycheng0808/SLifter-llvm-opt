#!/bin/bash

# ===========================================
# Part 1: Convert SASS to LLVM (SASS Lifter)
# ===========================================

# Generate .ll from SASS using the provided Python script
echo "Part 1: Converting SASS to LLVM..."
python ../main.py -i file/addMatrices_large.sass -o exp/addMatrices

# Ensure the output directory exists
output_dir="exp"
if [ ! -d "$output_dir" ]; then
    mkdir "$output_dir"
    echo "Directory '$output_dir' created."
fi

# Copy the generated .ll file for further modifications
cp exp/addMatrices.ll exp/addMatrices_mod.ll

# Post-processing
python llvm_post_process.py exp/addMatrices_mod.ll
echo "SASS to LLVM conversion done."

# ==============================
# Part 2: LLVM Optimization
# ==============================

echo "Part 2: Optimizing LLVM IR..."
# Optimize the modified LLVM IR file
opt -passes='mem2reg' -S exp/addMatrices_mod.ll -o exp/addMatrices_mod_opt.ll

# Uncomment the following lines to apply additional optimizations
# opt -passes='dce' -S exp/addMatrices_mod_opt.ll -o exp/addMatrices_mod_opt.ll
# opt -passes='instsimplify' -S exp/addMatrices_mod_opt.ll -o exp/addMatrices_mod_opt.ll
# opt -O1 exp/addMatrices_mod.ll -o exp/addMatrices_mod_opt.ll

echo "LLVM optimization done."

# ==============================
# Part 3: LLVM Codegen
# ==============================

# Compile the LLVM IR to an object file
echo "Part 3: Compiling LLVM IR to object file..."
llc -filetype=obj exp/addMatrices_mod_opt.ll -o exp/addMatrices.o

# Compile C code to object file
echo "Compiling C code to object file..."
clang -c printInfo.c -o exp/printInfo.o

# Link the object files
echo "Linking object files..."
clang exp/addMatrices.o exp/printInfo.o -o exp/printInfo

# Run the executable
echo "Running the executable..."
./exp/printInfo

echo "Process completed."