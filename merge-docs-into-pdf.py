#!/usr/bin/env python3
# merge-docs-into-pdf.py - Concatenate various file types into a single PDF file
# Usage: merge-docs-into-pdf.py -d <directory> -o <output_pdf>

import os
import argparse
import pdfkit
from PyPDF2 import PdfFileMerger
from markdown2 import markdown
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import yaml
from pdfkit.api import Configuration

def convert_html_to_pdf(source_html, output_filename):
    pdfkit.from_file(source_html, output_filename)

def convert_markdown_to_pdf(markdown_text, output_filename):
    html_text = markdown(markdown_text)
    pdfkit.from_string(html_text, output_filename)

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

def convert_files_to_pdf(directory, final_pdf):
    temp_pdfs = []
    for filename in os.listdir(directory):
        if not filename.endswith(('.html', '.md', '.txt', '.yaml', '.pdf')):
            continue
        filepath = os.path.join(directory, filename)
        temp_pdf_path = os.path.join(directory, 'temp_' + os.path.splitext(filename)[0] + '.pdf')
        if filename.endswith('.html'):
            convert_html_to_pdf(filepath, temp_pdf_path)
        elif filename.endswith('.md'):
            with open(filepath, 'r') as file:
                markdown_content = file.read()
            convert_markdown_to_pdf(markdown_content, temp_pdf_path)
        elif filename.endswith('.txt') or filename.endswith('.yaml'):
            with open(filepath, 'r') as file:
                text_content = file.read()
            if filename.endswith('.yaml'):
                convert_yaml_to_pdf(yaml.safe_load(text_content), temp_pdf_path)
            else:
                convert_text_to_pdf(text_content, temp_pdf_path)
        elif filename.endswith('.pdf'):
            temp_pdfs.append(filepath)
            continue
        temp_pdfs.append(temp_pdf_path)
    
    merge_pdfs(temp_pdfs, final_pdf)
    # Optionally, remove temporary PDF files
    for pdf in temp_pdfs:
        if pdf.startswith('temp_'):
            os.remove(pdf)

def main():
    parser = argparse.ArgumentParser(description='Concatenate various file types into a single PDF file.')
    parser.add_argument('-d', '--directory', type=str, help='Directory containing the files to process')
    parser.add_argument('-o', '--output', type=str, help='Output PDF file name')
    
    args = parser.parse_args()

    if not args.directory or not args.output:
        parser.print_help()
    else:
        convert_files_to_pdf(args.directory, args.output)

if __name__ == '__main__':
    main()
