#!/usr/bin/env python3
# an opensource python web crawler
# see https://github.com/deftio/simple-py-crawlbot

import os
import json
import argparse
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup, Comment
import time

def setup_browser():
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

def normalize_url(base, url):
    parsed = urlparse(urljoin(base, url.strip()))
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def save_html(content, filename):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Error saving HTML file: {e}")

def clean_html(soup):
    for element in soup(["script", "style", "link"]):
        element.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    return soup

def extract_content(driver, url, output_dir, clean_content):
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = soup.title.string if soup.title else 'No_Title'
        filename = f"{title.replace(' ', '_').replace('/', '_')}.html"
        filepath = os.path.join(output_dir, filename)

        if clean_content:
            soup = clean_html(soup)
        save_html(str(soup), filepath)

        return {
            'title': title,
            'file_path': filepath,
            'html_url': url
        }, get_links(soup, url)
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return None, set()

def get_links(soup, base_url):
    base_domain = urlparse(base_url).netloc
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = normalize_url(base_url, link['href'])
        if urlparse(full_url).netloc == base_domain:
            links.add(full_url)
    return links

def crawl_site(start_url, output_dir, show_progress, clean_content, max_links):
    driver = setup_browser()
    visited = set()
    to_visit = {normalize_url(start_url, start_url)}
    all_pages = []

    while to_visit and (max_links is None or len(visited) < max_links):
        current_url = to_visit.pop()
        if current_url in visited:
            continue
        visited.add(current_url)
        page_info, new_links = extract_content(driver, current_url, output_dir, clean_content)
        if page_info:
            all_pages.append(page_info)
        to_visit.update(new_links - visited)
        if show_progress:
            print(f"[{len(all_pages)} saved : {current_url}]")

    driver.quit()
    return all_pages

def main():
    parser = argparse.ArgumentParser(description="Web Crawler for Internal Documentation Site")
    parser.add_argument('--url', required=True, help="The starting URL for the crawler")
    parser.add_argument('--output_dir', default='output', help="Directory where the HTML files will be stored")
    parser.add_argument('--summary_file', default='summary.json', help="Filename for the JSON summary")
    parser.add_argument('--progress', action='store_true', help="Show progress during crawling")
    parser.add_argument('--clean', action='store_true', help="Remove non-informational content from HTML")
    parser.add_argument('--max_links', type=int, help="Maximum number of links to crawl, crawls entire site if omitted")
    args = parser.parse_args()

    # Ensure the output directory exists
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    crawled_pages = crawl_site(args.url, args.output_dir, args.progress, args.clean, args.max_links)
    
    # Create JSON summary
    summary = {
        'total_links': len(crawled_pages),
        'pages': crawled_pages,
        'output_directory': os.path.abspath(args.output_dir)
    }
    
    summary_path = os.path.join(args.output_dir, args.summary_file)
    with open(summary_path, 'w') as json_file:
        json.dump(summary, json_file, indent=4)

if __name__ == "__main__":
    main()
