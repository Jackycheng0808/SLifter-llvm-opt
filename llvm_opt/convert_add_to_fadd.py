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

def add_simple_main_function(file_path):
    with open(file_path, 'r') as infile:
        lines = infile.readlines()

    # Add a simple main function
    main_function = '''
        define i32 @main() {
            %a = alloca [10 x float]
            %b = alloca [10 x float]
            %c = alloca [10 x float]
            %a_ptr = getelementptr inbounds [10 x float], [10 x float]* %a, i32 0, i32 0
            %b_ptr = getelementptr inbounds [10 x float], [10 x float]* %b, i32 0, i32 0
            %c_ptr = getelementptr inbounds [10 x float], [10 x float]* %c, i32 0, i32 0
            call void @_Z9addArraysiPfS_S_(i32 10, float* %a_ptr, float* %b_ptr, float* %c_ptr)
            ret i32 0
        }
        '''
    lines.append(main_function)

    with open(file_path, 'w') as outfile:
        outfile.writelines(lines)

if __name__ == "__main__":
    file_path = sys.argv[1]
    replace_thread_idx_and_store_zero(file_path)
    convert_add_to_fadd(file_path)
    add_simple_main_function(file_path)