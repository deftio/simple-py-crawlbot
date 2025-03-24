# Usage Examples

This document provides practical examples for using the Simple-Py-Crawlbot tools in various scenarios.

## Basic Website Crawling

### Crawl a Small Website

```bash
python crawler.py --url https://example.com --progress
```

This command will:
- Start crawling from example.com
- Save all HTML files to the default 'output' directory
- Create a summary.json file with metadata
- Show progress during crawling

### Limit Crawling Depth

```bash
python crawler.py --url https://example.com --max_links 20 --progress
```

This command limits the crawler to process only 20 links, useful for testing or crawling large sites incrementally.

### Clean HTML During Crawling

```bash
python crawler.py --url https://example.com --clean --output_dir clean_html
```

This command:
- Crawls example.com
- Removes scripts, styles, and comments from the HTML
- Saves the cleaned files to 'clean_html' directory

## Using the Web Interface

1. Start the web interface:
   ```bash
   python crawler-gui.py
   ```

2. Open `http://127.0.0.1:8803` in your browser

3. Enter the starting URL and configure options:
   - URL: https://example.com
   - Output Directory: mysite
   - Enable "Show Progress" checkbox
   - Enable "Clean Content" checkbox
   - Set Max Links to 50

4. Click "Start Crawling" and monitor the progress

## Processing HTML Files

### Extract Clean Content from HTML Files

```bash
python clean-and-strip.py -input_dir output -output_dir yaml_content
```

This processes all HTML files in the 'output' directory and creates YAML files with clean, structured content in the 'yaml_content' directory.

### Convert YAML to JSON

```bash
python yaml-to-json.py yaml_content json_content
```

This converts all YAML files in 'yaml_content' to JSON format and saves them in 'json_content'.

## Creating Documentation

### Generate a PDF from Processed Files

```bash
python merge-docs-into-pdf.py -d json_content -o documentation.pdf
```

This combines all files in 'json_content' into a single PDF named 'documentation.pdf'.

## Advanced Workflow Examples

### Full Documentation Workflow

```bash
# Create directories for each stage
mkdir -p raw_html clean_yaml json_data

# Step 1: Crawl the website
python crawler.py --url https://example.com --output_dir raw_html --progress --clean

# Step 2: Process HTML to structured YAML
python clean-and-strip.py -input_dir raw_html -output_dir clean_yaml

# Step 3: Convert to JSON format
python yaml-to-json.py clean_yaml json_data

# Step 4: Generate comprehensive PDF
python merge-docs-into-pdf.py -d json_data -o site_documentation.pdf
```

### Crawl Multiple Sites

```bash
# Create separate directories for each site
mkdir -p site1 site2

# Crawl the first site
python crawler.py --url https://site1.example.com --output_dir site1 --progress --clean

# Crawl the second site
python crawler.py --url https://site2.example.com --output_dir site2 --progress --clean

# Process both sites
python clean-and-strip.py -input_dir site1 -output_dir site1_yaml
python clean-and-strip.py -input_dir site2 -output_dir site2_yaml

# Generate separate PDFs
python merge-docs-into-pdf.py -d site1_yaml -o site1_docs.pdf
python merge-docs-into-pdf.py -d site2_yaml -o site2_docs.pdf
```

### Create Automated Documentation Script

You can create a shell script to automate the entire process:

```bash
#!/bin/bash
# File: generate_docs.sh

# Check arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 <url> <output_pdf>"
    exit 1
fi

URL=$1
PDF_NAME=$2
TEMP_DIR="temp_$(date +%s)"

# Create temporary directories
mkdir -p $TEMP_DIR/html $TEMP_DIR/yaml $TEMP_DIR/json

# Run the crawling and processing pipeline
python crawler.py --url $URL --output_dir $TEMP_DIR/html --progress --clean
python clean-and-strip.py -input_dir $TEMP_DIR/html -output_dir $TEMP_DIR/yaml
python yaml-to-json.py $TEMP_DIR/yaml $TEMP_DIR/json
python merge-docs-into-pdf.py -d $TEMP_DIR/json -o $PDF_NAME

# Clean up temporary directories
rm -rf $TEMP_DIR

echo "Documentation generated: $PDF_NAME"
```

Use the script:
```bash
chmod +x generate_docs.sh
./generate_docs.sh https://example.com example_docs.pdf
```