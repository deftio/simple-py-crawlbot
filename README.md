# Simple Python Website Crawler

## Overview

This is a simple python web crawler which attempts to crawl all the pages of a given url using beautiful soup library and selenium.

It captures each page's HTML content, saves it locally, and provides a JSON summary of the crawled pages. The tool is intended for use in testing and validating site content and structure.

📚 **[Comprehensive documentation available in the docs folder](/docs/user-guide.md)**

### Note:
This is meant to be a simple crawler - if the site you wish to crawl has complex javascript it may not work.  Also please be responsible in crawling sites as it can take much site bandwidth and respect appropriate copyrights and other information.  

The crawler will not attempt to handle logins or firewalls.

## Features

- **Headless Browser Crawling**: Utilizes a headless Chrome browser to navigate and download web pages.
- **Duplicate Handling**: Normalizes URLs to avoid processing and storing duplicate content.
- **Local Storage**: Saves each page as a static HTML file.
- **JSON Summary**: Generates a summary of all processed pages, including titles, file paths, and URLs.
- **Web Interface**: Browser-based GUI for the crawler (crawler-gui.py).
- **Content Extraction**: Clean and extract structured text from HTML files (clean-and-strip.py).
- **Format Conversion**: Convert between YAML and JSON formats (yaml-to-json.py).
- **PDF Generation**: Merge multiple document types into a single PDF (merge-docs-into-pdf.py).

For detailed documentation on all features, see the [documentation folder](/docs/).

## Prerequisites & Installation

Before you run the web crawler, you must install the following:

- Python 3.9 or newer (technically 3.6 should work but some of the deps may soon no longer be supported)
- Selenium
- BeautifulSoup4
- ChromeDriver (make sure it matches your Chrome version and is placed in your PATH)

A separate script : clean_and_strip.py can be used to extract text while preserving the document hierarchy.

You can install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

If you have issues or conflicts with packages try creating a virtual environment with conda or simlar.  Virtual environments isolate the packages for this project from your current python packages and set up.

[How to install Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation)

Then at the command line run this command such as :
```bash
conda create -n simple-py-crawlbot python=3.10
conda activate simple-py-crawlbot
```
use this to deactivate the virtual env:

```bash
conda deactivate
```

## Usage

The crawler takes several cli (command line interface) arguments:

--url: Required. Specifies the starting URL for the crawler.
Example: --url "https://my-website-to-crawl/"

--output-dir: Specifies the directory where the HTML files will be stored. Default is "output".
Example: --output_dir custom_directory

--summary: Specifies the filename for the JSON summary. Default is "summary.json".
Example: --summary custom_summary.json

--progress: Enables progress display during the crawling process. This is a flag; include it to activate.
Example: --progress

--clean: Removes non-informational content (such as scripts and styles) from the HTML files. This is a flag; include it to activate.
Example: --clean

--max_links: Limits the number of links to crawl. If omitted, the crawler processes the entire site.
Example: --max_links 100


Each CLI argument can be used in combination to fine-tune the behavior of the crawler based on the needs of the user. You can customize the input parameters to control various aspects like the extent of crawling, output customization, and content processing.

### Example 
Here is an example using the cli arguments
```bash
python crawler.py --url https://my-website-to-crawl.com --output output_pages --summary_file detailed_summary.json --progress --clean --max_links 50
```

--url https://my-website-to-crawl.com: This sets the starting URL for the crawler to the specified website.

--output_dir output_pages: This directs the script to save all crawled HTML files in a directory named output_pages.

--summary detailed_summary.json: Specifies that the JSON summary of the crawl should be saved with the filename detailed_summary.json.

--progress: Includes a progress flag that enables real-time output showing the progress of the crawl, indicating how many links have been saved and what the current URL being processed is.

--clean: Activates the cleaning function, which will strip non-essential content such as scripts and CSS from the HTML files to focus only on the informational content.

--max_links 50: Limits the crawler to processing a maximum of 50 links from the website, which is useful for keeping the scope of the crawl manageable or for testing purposes.  (if left out it will attempt to crawl the whole site)
 
## Clean and Strip (clean_and_strip.py cli utility)
The script clean_and_script.py is a cli program which takes a directory of html files (such as output from the crawler.py script) and outputs a yaml file for each intput html file which has just the text (no css or styles or html attributes) from the source directory.  Files are stored in yaml format but are human readable.

Usage is as follows:
```bash
clean-and-strip -input_dir input_directory_of_crawled_files  -output_dir output_directory_of_extracted_text
```

## YAML-to-json.py
Also included is yaml-to-json.py which can take a directory of yaml files and convert to json.  Can be used with clean_and_strip.py above

```bash 
yaml-to-json.py -input_dir input_directory_of_crawled_files  -output_dir output_directory_of_extracted_text
```

## Document Merging Tool (Create PDFs)

The `merge-docs-into-pdf.py` script allows you to combine multiple documents of different formats into a single PDF file. This tool supports the following file formats:
- HTML (.html)
- Markdown (.md) 
- Text (.txt)
- YAML (.yaml)
- PDF (.pdf)

### Prerequisites

Skip the package installation if you have already used pip to install requirments for the crawler.py

Install the required Python packages:

```bash
pip install weasyprint PyPDF2 markdown2 reportlab pyyaml
```
or 
```bash
pip install -r requirments.txt
```

### Usage

Run the script using the following command:

```bash
python merge-docs-into-pdf.py -d <directory> -o <output.pdf> [--no-merge]
```

Arguments:
- `-d, --directory`: Directory containing the files to merge
- `-o, --output`: Name of the output PDF file or directory (when using --no-merge)
- `--no-merge`: Optional flag to create separate PDFs instead of merging into one

### Examples

Merge all files into a single PDF:
```bash
python merge-docs-into-pdf.py -d docs/ -o combined_documentation.pdf
```

Create separate PDFs for each file:
```bash
python merge-docs-into-pdf.py -d docs/ -o separate_pdfs/ --no-merge
```

This will:
1. Scan the specified directory for supported files
2. Convert each file to PDF format
3. Either:
   - Merge all PDFs into a single output file (default behavior)
   - Create separate PDFs in the output directory (when using --no-merge)
4. Clean up temporary files automatically

### Notes
- Files are processed in alphabetical order
- Existing PDF files in the directory will be included
- Unsupported file types are automatically skipped
- The script preserves the formatting of the original documents
- When using --no-merge, the output filename becomes the directory name where individual PDFs are saved

## LICENSE
BSD-2
