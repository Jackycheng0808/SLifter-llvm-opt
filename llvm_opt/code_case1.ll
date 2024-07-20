define void @function() {
entry:
  %s_val1 = alloca i32, align 4
  %R1_val = load i32, i32* %s_val1, align 4
  %R2_val = add i32 %R1_val, 1
  store i32 %R2_val, i32* %s_val1, align 4
  %R1_val1 = load i32, i32* %s_val1, align 4
  %R2_val1 = add i32 %R1_val1, 2
  store i32 %R2_val1, i32* %s_val1, align 4

  ret void
}