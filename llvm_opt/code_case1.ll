%R1_val = load i32, ptr %s_val1
%R2_val = add %R1_val, i32 1
store i32 %R2_val, ptr %s_val1
%R1_val1 = load i32, ptr %s_val1
%R2_val1 = add %R1_val1, i32 2
store i32 %R2_val1, ptr %s_val1