#!/usr/bin/env python3
# convert a directory of yaml files to json format

import os
import json
import yaml
import argparse

def convert_yaml_to_json(yaml_directory, json_directory):
    # Ensure the JSON directory exists
    if not os.path.exists(json_directory):
        os.makedirs(json_directory)

    # Iterate over all files in the yaml_directory
    for filename in os.listdir(yaml_directory):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            yaml_file_path = os.path.join(yaml_directory, filename)
            json_file_path = os.path.join(json_directory, filename.rsplit('.', 1)[0] + '.json')

            # Read the YAML file
            with open(yaml_file_path, 'r') as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)

            # Write the JSON file
            with open(json_file_path, 'w') as json_file:
                json.dump(yaml_content, json_file, indent=4)

            print(f"Converted {filename} to JSON.")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Convert YAML files to JSON.")
    parser.add_argument("input_dir", help="Directory containing YAML files to convert")
    parser.add_argument("output_dir", help="Directory to store converted JSON files")
    
    # Parse arguments
    args = parser.parse_args()

    # Call the function with the provided arguments
    convert_yaml_to_json(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
