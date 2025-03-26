# SPYCrawl API Test Suite

This directory contains a comprehensive test suite for all API endpoints in the SPYCrawl application.

## Overview

The test suite verifies that all API endpoints in `spycrawl.py` are functioning correctly. It tests:

- Basic routing (/ and /pages)
- Crawling functionality (/api/crawl)
- Crawl management (list, get, stop, clear)
- HTML cleaning (/api/clean)
- YAML to JSON conversion (/api/convert)
- PDF generation (/api/pdf)
- File operations (list files, download file)

## Setup

Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

## Running the Tests

To run the full test suite:

```bash
python run_api_tests.py
```

By default, this will run all tests with verbose output. You can change the verbosity level:

```bash
# Quiet mode (only show errors)
python run_api_tests.py -v 0

# Normal mode (show test names and status)
python run_api_tests.py -v 1

# Verbose mode (show detailed output)
python run_api_tests.py -v 2
```

## How It Works

The test suite:

1. Automatically starts the SPYCrawl server in a separate process
2. Creates temporary directories for test files
3. Runs each test sequentially
4. Cleans up temporary files and stops the server when done

## Test Descriptions

- `test_01_root_redirect`: Verifies that the root endpoint redirects to /pages
- `test_02_pages`: Checks that the /pages endpoint returns HTML
- `test_03_crawl_api`: Tests the crawl API endpoint with a simple website
- `test_04_list_crawls`: Verifies that all crawl sessions can be listed
- `test_05_get_crawl`: Tests getting details of a specific crawl session
- `test_06_stop_crawl`: Tests stopping a running crawl job
- `test_07_clean_api`: Tests the HTML cleaning endpoint
- `test_08_convert_api`: Tests the YAML to JSON conversion endpoint
- `test_09_pdf_api`: Tests PDF generation with and without merging
- `test_10_list_files`: Tests listing files in a directory
- `test_11_download_file`: Tests downloading a specific file
- `test_12_clear_crawls`: Tests clearing all crawl sessions

## Extending the Tests

To add new tests, simply add new test methods to the `TestSpyCrawlAPI` class in `test_api_endpoints.py`. Make sure to name methods starting with `test_` for them to be discovered automatically.