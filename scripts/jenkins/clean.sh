#!/bin/sh
echo "pr_number is ${pr_number}"
echo "last_build is ${last_build}"
echo "multi is ${multi}"
echo "origin_comment is ${comment_id}"
# prefix=""
# normal_jobs="$prefix/pr-${pr_number}/${last_build}/jobs"
# addition_jobs="$prefix/pr-${pr_number}/test-latest/jobs"
echo "start cleaning addition_jobs"
python3 scripts/jenkins/lava.py ${pr_number} ${comment_id}
echo "finish cleaning addition_jobs"
if [ ${multi} == "true" ]; then
    echo "start cleaning normal_jobs"
    python3 scripts/jenkins/stop.py ${pr_number} ${last_build}
    echo "finfish cleaning normal_jobs"
fi