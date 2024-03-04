#!/bin/bash

# Counter for failures
failures=0

# Run the test 1000 times
for ((i=1; i<=1000; i++))
do
    # Run the test and capture the output
    output=$(pytest test/api_tests/throttling_tests.py::test_main_throttling_sequence -s 2>&1)

    # Check if the output contains 'FAILED'
    if [[ $output == *"FAILED"* ]]; then
        # Increment the failure count
        ((failures++))
        # Print the output if the test fails
        echo "Test failed in run $i:"
        echo "$output"
    fi
done

# Print the total number of failures
echo "Total number of failures: $failures"
