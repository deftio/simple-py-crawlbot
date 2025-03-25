#!/usr/bin/env python3

import os
import sys
import logging
from pathlib import Path
from weasyprint import HTML
from PyPDF2 import PdfFileMerger
from markdown2 import markdown
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import yaml

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
        log_dir / "merge_docs_into_pdf.log",
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

def convert_html_to_pdf(source_html, output_filename):
    HTML(source_html).write_pdf(output_filename)

def convert_markdown_to_pdf(markdown_text, output_filename):
    html_text = markdown(markdown_text)
    HTML(string=html_text).write_pdf(output_filename)

def convert_text_to_pdf(text, output_filename):
    c = canvas.Canvas(output_filename, pagesize=letter)
    text_obj = c.beginText(40, 750)
    for line in text.split('\n'):
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.save()

def convert_yaml_to_pdf(yaml_content, output_filename):
    yaml_text = yaml.dump(yaml_content, default_flow_style=False)
    convert_text_to_pdf(yaml_text, output_filename)

def merge_pdfs(pdf_files, output_filename):
    merger = PdfFileMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_filename)
    merger.close()

def convert_files_to_pdf(input_dir, output_path):
    """Convert HTML and Markdown files to PDF and optionally merge them"""
    try:
        logger.info(f"Starting PDF conversion from {input_dir} to {output_path}")
        
        # Create output directory if it doesn't exist
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")
        
        # Process each file
        input_path = Path(input_dir)
        pdf_files = []
        
        # Get all HTML and Markdown files
        html_files = list(input_path.glob("**/*.html"))
        md_files = list(input_path.glob("**/*.md"))
        logger.info(f"Found {len(html_files)} HTML files and {len(md_files)} Markdown files to process")
        
        # Process HTML files
        for html_file in html_files:
            try:
                logger.info(f"Processing HTML file: {html_file}")
                pdf_file = output_dir / html_file.with_suffix('.pdf').name
                
                # Convert HTML to PDF
                HTML(html_file).write_pdf(pdf_file)
                pdf_files.append(pdf_file)
                logger.info(f"Successfully converted HTML to PDF: {pdf_file}")
                
            except Exception as e:
                logger.error(f"Error processing HTML file {html_file}: {str(e)}")
                continue
        
        # Process Markdown files
        for md_file in md_files:
            try:
                logger.info(f"Processing Markdown file: {md_file}")
                pdf_file = output_dir / md_file.with_suffix('.pdf').name
                
                # Convert Markdown to HTML
                with open(md_file, 'r', encoding='utf-8') as f:
                    html_content = markdown(f.read())
                
                # Convert HTML to PDF
                HTML(string=html_content).write_pdf(pdf_file)
                pdf_files.append(pdf_file)
                logger.info(f"Successfully converted Markdown to PDF: {pdf_file}")
                
            except Exception as e:
                logger.error(f"Error processing Markdown file {md_file}: {str(e)}")
                continue
        
        # Merge PDFs if there are multiple files
        if len(pdf_files) > 1:
            try:
                logger.info("Merging PDF files")
                merger = PdfFileMerger()
                for pdf_file in pdf_files:
                    merger.append(str(pdf_file))
                
                # Save merged PDF
                merged_pdf = output_dir / "merged.pdf"
                merger.write(str(merged_pdf))
                merger.close()
                logger.info(f"Successfully merged PDFs into: {merged_pdf}")
                
            except Exception as e:
                logger.error(f"Error merging PDFs: {str(e)}")
        
        logger.info("PDF conversion completed")
        
    except Exception as e:
        logger.error(f"Error in convert_files_to_pdf: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Concatenate various file types into a single PDF file.')
    parser.add_argument('-d', '--directory', type=str, help='Directory containing the files to process')
    parser.add_argument('-o', '--output', type=str, help='Output PDF file name')
    parser.add_argument('--no-merge', action='store_true', help='Create separate PDFs instead of merging')
    
    args = parser.parse_args()

    if not args.directory or not args.output:
        parser.print_help()
    else:
        if args.no_merge:
            output_dir = os.path.splitext(args.output)[0]
            os.makedirs(output_dir, exist_ok=True)
            for filename in os.listdir(args.directory):
                if not filename.endswith(('.html', '.md', '.txt', '.yaml', '.pdf')):
                    continue
                filepath = os.path.join(args.directory, filename)
                output_pdf = os.path.join(output_dir, os.path.splitext(filename)[0] + '.pdf')
                
                if filename.endswith('.html'):
                    convert_html_to_pdf('file://' + os.path.abspath(filepath), output_pdf)
                elif filename.endswith('.md'):
                    with open(filepath, 'r') as file:
                        markdown_content = file.read()
                    convert_markdown_to_pdf(markdown_content, output_pdf)
                elif filename.endswith('.txt') or filename.endswith('.yaml'):
                    with open(filepath, 'r') as file:
                        text_content = file.read()
                    if filename.endswith('.yaml'):
                        convert_yaml_to_pdf(yaml.safe_load(text_content), output_pdf)
                    else:
                        convert_text_to_pdf(text_content, output_pdf)
                elif filename.endswith('.pdf'):
                    from shutil import copyfile
                    copyfile(filepath, output_pdf)
        else:
            convert_files_to_pdf(args.directory, args.output)

if __name__ == '__main__':
    main()
