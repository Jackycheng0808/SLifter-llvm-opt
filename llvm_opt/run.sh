#!/bin/bash

# Define variables
sass_file="file/addMatrices.sass"
output_dir="exp"
initial_ll_file="$output_dir/addMatrices"
modified_ll_file="$output_dir/addMatrices_mod.ll"
optimized_ll_file="$output_dir/addMatrices_mod_opt.ll"
object_file="$output_dir/addMatrices.o"
c_source_file="printInfo.c"
c_object_file="$output_dir/main.o"
executable_file="$output_dir/main"

# ===========================================
# Part 1: Convert SASS to LLVM (SASS Lifter)
# ===========================================

# Generate .ll from SASS using the provided Python script
echo "Part 1: Converting SASS to LLVM..."
python ../main.py -i "$sass_file" -o "$initial_ll_file"

# Ensure the output directory exists
if [ ! -d "$output_dir" ]; then
    mkdir "$output_dir"
    echo "Directory '$output_dir' created."
fi

# Copy the generated .ll file for further modifications
cp "$initial_ll_file".ll "$modified_ll_file"

# Post-processing
python llvm_post_process.py "$modified_ll_file"
echo -e "SASS to LLVM conversion done.\n"


# ==============================
# Part 2: LLVM Optimization
# ==============================

echo "Part 2: Optimizing LLVM IR..."
# Optimize the modified LLVM IR file
opt -passes='mem2reg' -S "$modified_ll_file" -o "$optimized_ll_file"

# Uncomment the following lines to apply additional optimizations
# opt -passes='dce' -S "$optimized_ll_file" -o "$optimized_ll_file"
# opt -passes='instsimplify' -S "$optimized_ll_file" -o "$optimized_ll_file"
# opt -O1 "$modified_ll_file" -o "$optimized_ll_file"

echo -e "LLVM optimization done.\n"

# ==============================
# Part 3: LLVM Codegen
# ==============================

# Compile the LLVM IR to an object file
echo "Part 3: Compiling LLVM IR to object file..."
llc -filetype=obj "$optimized_ll_file" -o "$object_file"

# Compile C code to object file
echo "Compiling C code to object file..."
clang -c "$c_source_file" -o "$c_object_file"
clang "$object_file" "$c_object_file" -o "$executable_file"

# Run the executable
echo
./"$executable_file"

echo -e "Process completed. \n"