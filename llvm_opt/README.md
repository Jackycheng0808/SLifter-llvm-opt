# SASS to LLVM Converter and Optimizer

This script automates the process of converting SASS (Shader Assembly) to LLVM IR, optimizing the LLVM IR, and generating executable code. It's designed to work with CUDA kernels, specifically for matrix addition operations.

## Prerequisites

- Python 3.x
- LLVM toolchain (including `opt`, `llc`, and `clang`)
- SASS Lifter (assumed to be in the parent directory)

## Usage

1. Place your SASS file in the `file/` directory with the name `addMatrices_large.sass`.
2. Ensure the SASS Lifter script (`main.py`) is in the parent directory.
3. Run the script:

./run.sh

## Process

The script performs the following steps:

1. **SASS to LLVM Conversion**
- Converts SASS to LLVM IR using the SASS Lifter.
- Performs post-processing on the generated LLVM IR.

2. **LLVM Optimization**
- Applies the `mem2reg` optimization pass.
- Additional optimization passes are available but commented out.

3. **Code Generation**
- Compiles the optimized LLVM IR to an object file.
- Compiles the C wrapper code (`printInfo.c`) to an object file.
- Links the object files to create an executable.

4. **Execution**
- Runs the generated executable.

## Output

- Intermediate files are stored in the `exp/` directory.
- The final executable is named `printInfo` and placed in the current directory.

## Note

This script is designed for a specific use case (matrix addition). Modifications may be necessary for other CUDA kernels or operations.