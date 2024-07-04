class IRCodeOptimizer:
    def __init__(self):
        self.current_ir = ""
        self.type_conversion = {
            ("i8", "i8"): "i16",
            ("i16", "i16"): "i32",
            ("i32", "i32"): "i64",
            ("float", "float"): "double"
        }
    
    def calculate_coalesced_type(self, type1, type2):
        """
        Calculate the coalesced type based on two input types.
        """
        return self.type_conversion.get((type1, type2), None)

    def load_elimination(self):
        """
        Perform load elimination on the current IR code.
        """
        optimized_code = []
        lines = self.current_ir.split("\n")
        last_load = None
        last_value = None

        for line in lines:
            if "load" in line:
                last_load = line
                last_value = line.split(",")[1].strip()
            elif "add" in line and last_load:
                if last_value in line:
                    optimized_code.append(line)
                    last_value = line.split(" ")[0]
                else:
                    optimized_code.append(line)
                    last_load = None
            elif "store" in line and last_load:
                store_value = line.split(" ")[1]
                if last_value in store_value:
                    optimized_code[-1] = optimized_code[-1].replace(last_value, store_value.split(",")[1].strip())
                    last_load = None
                else:
                    optimized_code.append(line)
            else:
                optimized_code.append(line)
        
        self.current_ir = "\n".join(optimized_code)

    
    def operands_coalescing(self):
        """
        Perform operands coalescing on the current IR code.
        """
        optimized_code = []
        lines = self.current_ir.split("\n")
        getelementptrs = {}
        loads = []

        # Collect all getelementptr and load instructions
        for line in lines:
            if "getelementptr" in line:
                parts = line.split(", ")
                var_name = line.split("=")[0].strip()
                base_ptr = parts[1].split(" ")[1]
                index = int(parts[2].split(" ")[1])
                # length = int(parts[2].split(" ")[0])
                # getelementptrs[var_name] = (base_ptr, index, length, line)
                getelementptrs[var_name] = (base_ptr, index, line)
            elif "load" in line:
                parts = line.split(", ")
                var_name = parts[1].split(" ")[1]
                loads.append((var_name, line))
        i = 0
        res = {}
        
        for key, value in loads:
            load_args = value.split("=")[0].strip()
            load_type = value.split("=")[1].split(",")[0].split(" ")[-1]
            if getelementptrs[key][0] in res:
                res[getelementptrs[key][0]].append((getelementptrs[key], load_args, load_type))
            else:
                res[getelementptrs[key][0]] = [(getelementptrs[key], load_args, load_type)]
            
        optimized_code = []
        
        for key, pair in res.items():
            load_1, load_2 = pair[0][0][-1], pair[1][0][-1]
            load_args_1, load_args_2 = pair[0][1], pair[1][1]
            load_dtype_1, load_dtype_2 = pair[0][2], pair[1][2]

            gep_line = pair[0][0][-1]

            load_1_idx = int(load_1.split("=")[1].split(", ")[-1].split(" ")[1])
            load_2_idx = int(load_2.split("=")[1].split(", ")[-1].split(" ")[1])

            if abs(load_2_idx - load_1_idx) != 1:
                break 
            else:
                coalesced_type = self.calculate_coalesced_type(load_dtype_1, load_dtype_2)
                coalesced_ptr = load_1.split("=")[0].strip()
                coalesced_args = load_args_1
                coalesced_load = f"{coalesced_args} = load {coalesced_type}, ptr {coalesced_ptr}"
                optimized_code.append(gep_line)
                optimized_code.append(coalesced_load)

            i += 1
        
        self.current_ir = "\n".join(optimized_code)

    def load_ir_from_file(self, file_path):
        """
        Load IR code from a file and store it in the current_ir attribute.
        """
        with open(file_path, 'r') as file:
            self.current_ir = file.read()

    def print_ir(self):
        """
        Print the current IR code.
        """
        print(self.current_ir)


# Example usage:
optimizer = IRCodeOptimizer()

# Load IR code from files
optimizer.load_ir_from_file('./code_case1.ll')
optimizer.load_elimination()
optimizer.print_ir()

optimizer.load_ir_from_file('./code_case2.ll')
optimizer.operands_coalescing()
optimizer.print_ir()