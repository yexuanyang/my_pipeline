#!/bin/sh
echo "hello, i am cancel_job"
echo "pr_number is ${pr_number}"
echo "last_build is ${last_build}"
echo "multi is ${multi}"
if [ ${multi} == "true" ]; then
    echo "multi is true"
else
    echo "multi is false"
fi