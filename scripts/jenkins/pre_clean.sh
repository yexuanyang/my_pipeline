#!/bin/sh
echo "pr_number is ${pr_number}"
echo "last_build is ${last_build}"
echo "multi is ${multi}"
# prefix=""
# normal_jobs="$prefix/pr-${pr_number}/${last_build}/jobs"
# addition_jobs="$prefix/pr-${pr_number}/test-latest/jobs"
echo "start cleaning addition_jobs"
# 删除addition_jobs
echo "finish cleaning addition_jobs"
if [ ${multi} == "true" ]; then
    echo "start cleaning normal_jobs"
    # 删除normal_jobs
    echo "finfish cleaning normal_jobs"
fi