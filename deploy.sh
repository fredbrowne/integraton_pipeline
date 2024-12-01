#!/bin/bash

# Define paths
LAMBDA_SRC="./lambdas"
DEPLOYMENT_DIR="$LAMBDA_SRC/deployment"

# Ensure the deployment directory exists
mkdir -p "$DEPLOYMENT_DIR"

# Function to package a Lambda function
package_lambda() {
  local lambda_name=$1
  local source_dir="$LAMBDA_SRC/$lambda_name"
  local zip_file="$DEPLOYMENT_DIR/$lambda_name.zip"

  echo "Packaging Lambda: $lambda_name"

  # Check if the source directory exists
  if [ ! -d "$source_dir" ]; then
    echo "Error: Source directory $source_dir does not exist!"
    exit 1
  fi

  # Remove the existing ZIP file
  if [ -f "$zip_file" ]; then
    rm -f "$zip_file"
  fi

  # Install dependencies if requirements.txt exists
  if [ -f "$source_dir/requirements.txt" ]; then
    echo "Installing dependencies for $lambda_name..."
    pip install -r "$source_dir/requirements.txt" -t "$source_dir" > /dev/null
  fi

  # Create the ZIP file and exclude __pycache__
  echo "Creating ZIP file for $lambda_name..."
  zip -r "$zip_file" "$source_dir" -x "*/__pycache__/*" "*.pyc" "*.pyo" > /dev/null

  echo "Lambda $lambda_name packaged successfully: $zip_file"
}

# List of Lambda functions to package
LAMBDAS=("split_batches" "aggregate_results" "check_completion" "worker") # Add more Lambda names as needed

# Package each Lambda function
for lambda in "${LAMBDAS[@]}"; do
  package_lambda "$lambda"
done

echo "All Lambdas packaged successfully."
