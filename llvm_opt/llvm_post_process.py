import sys

# Remove the function declaration and replace the store instruction
def replace_thread_idx_and_store_zero(file_path):
    with open(file_path, 'r') as infile:
        lines = infile.readlines()

    modified_lines = []
    for line in lines:
        if 'declare i32 @"thread_idx"()' in line:
            continue  # Skip the declare line
        if 'call i32 @"thread_idx"()' in line:
            line = line.replace('%"ThreadIdx" = call i32 @"thread_idx"()', '')  # Remove the call instruction
        if 'store i32 %"ThreadIdx", i32* %"R2INT"' in line:
            line = line.replace('store i32 %"ThreadIdx", i32* %"R2INT"', 'store i32 0, i32* %"R2INT"')
        if '@"_Z9addArraysiPfS_S_"(i32 %".1", float* %".2", float* %".3", i32 %".4")' in line:
            line = line.replace('i32 %".4"', 'float* %".4"')
        if '%"Arg3" = alloca i32, i32 8' in line:
            line = line.replace('%"Arg3" = alloca i32, i32 8', '%"Arg3" = alloca float*, i32 8')
        if 'store i32 %".4", i32* %"Arg3"' in line:
            line = line.replace('store i32 %".4", i32* %"Arg3"', 'store float* %".4", float** %"Arg3"')
        if '%"cmp" = icmp sge i32 %"val1", %"val2"' in line:
            line = line.replace('sge', 'slt')
        if 'R6Int32' in line:
            line = line.replace('R6Int32', 'R6INT')
        modified_lines.append(line)

    with open(file_path, 'w') as outfile:
        outfile.writelines(modified_lines)

def change_saving_address(file_path):
    with open(file_path, 'r') as infile:
        lines = infile.readlines()

    modified_lines = []
    for line in lines:
        if '%"loadptr.2" = load float*, float** %"R6Float32_PTR"' in line:
            modified_lines.append('  %"ptr.2" = load float*, float** %"Arg3"\n')
            modified_lines.append('  %".17" = getelementptr inbounds float, float* %"ptr.2", i32 %"offset"\n')
        elif '%"loadval.1" = load float, float* %"R0Float32"' in line:
            modified_lines.append(line)
        elif 'store float %"loadval.1", float* %"loadptr.2"' in line:
            modified_lines.append('  store float %"loadval.1", float* %".17"\n')
        else:
            modified_lines.append(line)

    with open(file_path, 'w') as outfile:
        outfile.writelines(modified_lines)

def add_loop_structure(file_path):
    with open(file_path, 'r') as infile:
        lines = infile.readlines()

    modified_lines = []
    for line in lines:
        if 'store i32 0, i32* %"R2INT"' in line:
            modified_lines.append(line)
            modified_lines.append('  br label %LoopCond\n\n')
            modified_lines.append('LoopCond:\n')
        elif 'br i1 %"cmp", label %"BB_0058", label %"BB_0050"' in line:
            modified_lines.append('  br i1 %"cmp", label %"BB_0050", label %"BB_0058"\n')
        elif 'ret void' in line and 'BB_0058:' not in modified_lines[-1]:
            modified_lines.append('\n  ; Increment loop counter\n')
            modified_lines.append('  %"next" = add i32 %"loadval", 1\n')
            modified_lines.append('  store i32 %"next", i32* %"R0INT"\n')
            modified_lines.append('  br label %LoopCond\n\n')
            modified_lines.append(line)
        else:
            modified_lines.append(line)

    with open(file_path, 'w') as outfile:
        outfile.writelines(modified_lines)

def convert_add_to_fadd(file_path):
    with open(file_path, 'r') as infile:
        lines = infile.readlines()

    # Replace `add` with `fadd` for floating-point addition
    modified_lines = [line.replace('add float', 'fadd float') for line in lines]

    modified_lines = [line.replace('target triple = "unknown-unknown-unknown"', 
                                'target triple = "arm64-apple-macosx11.0.0"') for line in modified_lines]

    with open(file_path, 'w') as outfile:
        outfile.writelines(modified_lines)

def remove_duplicates_and_unused(file_path):
    with open(file_path, 'r') as infile:
        lines = infile.readlines()

    save_set = set()
    modified_lines = []
    allowed_case = ['ret', 'br']
    for line in lines:
        if line in save_set and (line not in allowed_case):
            for case in allowed_case:
                if case in line:
                    save_set.add(line)
                    modified_lines.append(line)
                    continue
            continue
        save_set.add(line)
        modified_lines.append(line)

    with open(file_path, 'w') as outfile:
        outfile.writelines(modified_lines)

if __name__ == "__main__":
    file_path = sys.argv[1]
    replace_thread_idx_and_store_zero(file_path)
    convert_add_to_fadd(file_path)
    add_loop_structure(file_path)
    change_saving_address(file_path)
    remove_duplicates_and_unused(file_path)