# Step 1: generate .ll
python ../main.py -i ../test/spaxy.sass -o exp/output -arch 75

# Step 2: optimize .ll with 
dir_name="exp"

# Check if the directory exists
if [ ! -d "$dir_name" ]; then
    # Create the directory
    mkdir "$dir_name"
    echo "Directory '$dir_name' created."

opt -O1 -print-after-all exp/output.ll &> log.txt


opt -passes='mem2reg' -S exp/output.ll -o exp/optimized_mem2req.ll
opt -passes='dce' -S exp/output.ll -o exp/optimized_dce.ll
opt -passes='instsimplify' -S exp/output.ll -o exp/optimized_constantFolding.ll

# opt -passes='mem2reg,instcombine,loop-unroll,loop-vectorize,inline,constprop' input.ll -o optimized.ll



