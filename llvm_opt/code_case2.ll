define void @function(i32* %arg_0) {
entry:
    %R1_val = getelementptr inbounds i32, ptr %arg_0, i32 0
    %R5_val = load float, ptr %R1_val
    %R2_val = getelementptr inbounds i32, ptr %arg_0, i32 1
    %R6_val = load float, ptr %R2_val

  ret void
}