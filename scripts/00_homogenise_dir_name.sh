# Author: Jyoti Mangal, Date: 13/10/2026
# Script to homogenise the directory names in the raw_xnat/MinMo/ folder
#!/bin/bash
# run from W:/MinMo_CI/raw_xnat/MinMo/ (or equivalent path in WSL)

for dir in Min-Mo-*/; do
    newname="${dir/Min-Mo-/MinMo-}"
    mv "$dir" "$newname"
    echo "Renamed: $dir -> $newname"
done