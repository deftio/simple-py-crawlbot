#!/usr/bin/env python3
# convert a directory of yaml files to json format

import os
import json
import yaml
import argparse
import sys
import logging
from pathlib import Path

# Configure logging
def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler for all logs
    file_handler = logging.FileHandler(
        log_dir / "yaml_to_json.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Console handler for INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

# Initialize logging
logger = setup_logging()

def convert_yaml_to_json(input_dir, output_dir):
    """Convert YAML files to JSON format"""
    try:
        logger.info(f"Starting YAML to JSON conversion from {input_dir} to {output_dir}")
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")
        
        # Process each YAML file
        input_path = Path(input_dir)
        yaml_files = list(input_path.glob("**/*.yaml"))
        logger.info(f"Found {len(yaml_files)} YAML files to process")
        
        for yaml_file in yaml_files:
            try:
                logger.info(f"Processing file: {yaml_file}")
                
                # Read the YAML file
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    yaml_content = yaml.safe_load(f)
                
                # Create output file path
                rel_path = yaml_file.relative_to(input_path)
                output_file = output_path / rel_path.with_suffix('.json')
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write the JSON file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(yaml_content, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Successfully converted and saved: {output_file}")
                
            except Exception as e:
                logger.error(f"Error processing file {yaml_file}: {str(e)}")
                continue
        
        logger.info("YAML to JSON conversion completed")
        
    except Exception as e:
        logger.error(f"Error in convert_yaml_to_json: {str(e)}")
        raise

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
    if len(sys.argv) != 3:
        logger.error("Usage: python yaml_to_json.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    try:
        convert_yaml_to_json(input_dir, output_dir)
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)
