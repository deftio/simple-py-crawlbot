#!/usr/bin/env python3
# an opensource python web crawler
# see https://github.com/deftio/simple-py-crawlbot

import os
import sys
import logging
from pathlib import Path
import yaml
from bs4 import BeautifulSoup, NavigableString, Comment
import argparse

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
        log_dir / "clean_and_strip.log",
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

def clean_html(html_content):
    """Remove script and style elements from HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    for script_or_style in soup(["script", "style", "link"]):
        script_or_style.decompose()  # remove all script and style elements
    return soup

def clean_text(text):
    """Clean text by removing unwanted characters."""
    # Remove unwanted character sequences
    text = text.replace('$', '').replace('/$', '')
    return text.strip()

def should_include_text(text):
    """Determine if the cleaned text should be included based on its length and content."""
    if len(text) == 1 and text in "/":
        return False
    return True

def extract_text(element):
    """Recursively extract and clean textual content from HTML elements, preserving the DOM tree structure."""
    if isinstance(element, NavigableString):
        text = clean_text(element.string)
        if text and should_include_text(text):
            return text  # Return cleaned text directly

    # Concatenate span text with neighbors if the parent is not a span
    accumulated_text = []
    if element.name == "span":
        for child in element.children:
            child_text = extract_text(child)
            if child_text:
                accumulated_text.append(child_text)
        return " ".join(accumulated_text) if accumulated_text else None

    # Process general elements
    if element.name is not None:
        children_text = []
        for child in element.children:
            child_text = extract_text(child)
            if child_text:
                children_text.append(child_text)
        
        if len(children_text) == 1 and isinstance(children_text[0], str):
            return children_text[0]  # Return the single string directly
        else:
            return children_text  # Return a list of cleaned children

    return None  # If there's no text and no significant children, return None

def read_html_file(filepath):
    """Read an HTML file and return its content."""
    with open(filepath, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

def write_yaml(data, output_filepath):
    """Write data to a YAML file."""
    with open(output_filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True, default_flow_style=False)

def process_html_files(input_dir, output_dir):
    """Process all HTML files in the specified directory, converting them to structured YAML files."""
    try:
        logger.info(f"Starting HTML processing from {input_dir} to {output_dir}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
        
        input_path = Path(input_dir)
        html_files = list(input_path.glob("**/*.html"))
        logger.info(f"Found {len(html_files)} HTML files to process")
        
        for html_file in html_files:
            try:
                logger.info(f"Processing file: {html_file}")
                
                html_path = html_file
                output_path = os.path.join(output_dir, html_file.name)
                html_content = read_html_file(html_path)
                soup = clean_html(html_content)
                text_tree = extract_text(soup)
                if text_tree:
                    write_yaml(text_tree, output_path)
                    logger.info(f"Processed {html_file} to {output_path}")
                
            except Exception as e:
                logger.error(f"Error processing file {html_file}: {str(e)}")
                continue
        
        logger.info("HTML processing completed")
        
    except Exception as e:
        logger.error(f"Error in process_html_files: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Convert HTML files to structured YAML preserving cleaned text.")
    parser.add_argument('-input_dir', help="Directory containing HTML files to process.")
    parser.add_argument('-output_dir', help="Directory where YAML files will be stored.")
    args = parser.parse_args()
    process_html_files(args.input_dir, args.output_dir)

if __name__ == '__main__':
    main()
