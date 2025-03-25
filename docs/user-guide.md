# Simple-Py-Crawlbot User Guide

## Introduction

Simple-Py-Crawlbot is a versatile set of Python tools for web crawling, content extraction, and documentation generation. This guide covers the installation, usage, and workflow integration of all components.

## Installation

### Prerequisites

- Python 3.9+ (Python 3.6+ should work but some dependencies may require newer versions)
- Chrome browser (for Selenium WebDriver)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/deftio/simple-py-crawlbot.git
   cd simple-py-crawlbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Create a virtual environment:
   ```bash
   conda create -n simple-py-crawlbot python=3.10
   conda activate simple-py-crawlbot
   pip install -r requirements.txt
   ```

## Tools

### 1. Web Crawler (crawler.py)

The core tool for crawling websites and saving content locally.

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Starting URL for crawling (required) | - |
| `--output_dir` | Directory to store HTML files | `output` |
| `--summary_file` | Filename for the JSON summary | `summary.json` |
| `--progress` | Show crawling progress | `False` |
| `--clean` | Remove scripts, styles from HTML | `False` |
| `--max_links` | Maximum number of links to crawl | Unlimited |

#### Example Usage

Simple usage:
```bash
python crawler.py --url https://example.com
```

Advanced usage:
```bash
python crawler.py --url https://example.com --output_dir example_site --summary_file site_map.json --progress --clean --max_links 50
```

### 2. Web Interface (crawler-gui.py)

A browser-based GUI for the crawler with the same functionality.

#### Usage

1. Start the server:
   ```bash
   python crawler-gui.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:8803`

3. Fill in the form with the same options as the command-line version

### 3. HTML Cleaner (clean_and_strip.py)

Extracts and cleans text content from HTML files, preserving document structure.

#### Options

| Option | Description |
|--------|-------------|
| `-input_dir` | Directory containing HTML files to process |
| `-output_dir` | Directory where YAML files will be stored |

#### Example Usage

```bash
python clean_and_strip.py -input_dir output -output_dir yaml_output
```

### 4. YAML to JSON Converter (yaml_to_json.py)

Converts YAML files to JSON format.

#### Options

| Parameter | Description |
|-----------|-------------|
| `input_dir` | Directory containing YAML files |
| `output_dir` | Directory for storing JSON files |

#### Example Usage

```bash
python yaml_to_json.py yaml_output json_output
```

### 5. PDF Generator (merge_docs_into_pdf.py)

Combines various document formats into a single PDF.

#### Options

| Option | Description |
|--------|-------------|
| `-d`, `--directory` | Directory containing files to process |
| `-o`, `--output` | Output PDF filename |

#### Example Usage

```bash
python merge_docs_into_pdf.py -d json_output -o documentation.pdf
```

## Complete Workflow Example

This example demonstrates a full workflow from crawling a website to generating a PDF document:

```bash
# Step 1: Crawl a website
python crawler.py --url https://example.com --output_dir raw_html --progress --clean

# Step 2: Clean and extract structured content
python clean_and_strip.py -input_dir raw_html -output_dir clean_yaml

# Step 3: Convert to JSON if needed
python yaml_to_json.py clean_yaml json_data

# Step 4: Generate a comprehensive PDF
python merge_docs_into_pdf.py -d json_data -o example_documentation.pdf
```

## Tips and Troubleshooting

- **Chrome/ChromeDriver Issues**: The crawler uses the `chromedriver-autoinstaller` package which should automatically download the correct ChromeDriver version. If you experience issues, try installing ChromeDriver manually and ensure it's in your PATH.

- **Memory Usage**: For large websites, the crawler may consume significant memory. Use the `--max_links` option to limit crawling.

- **Crawling Speed**: To avoid overloading web servers, the crawler intentionally adds a delay between page requests.

- **Content Types**: The PDF generator handles HTML, Markdown, plain text, YAML, and JSON files differently. Results may vary based on content complexity.

- **Filtered Content**: By default, the `--clean` option removes JavaScript, CSS, and comments from HTML. This improves readability but may affect the rendering of dynamic content.

## Advanced Configuration

For advanced users, several aspects of the tools can be customized:

- Modify the selenium browser options in `setup_browser()` function
- Adjust the delay between page requests by changing the `time.sleep()` value
- Customize the HTML cleaning process in the `clean_html()` function