#!/usr/bin/env python3

import os
import json
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup, Comment
import time
from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

class CrawlRequest(BaseModel):
    url: str
    output_dir: Optional[str] = 'output'
    show_progress: Optional[bool] = False
    clean_content: Optional[bool] = True
    max_links: Optional[int]
    
# Serve static files from 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Selenium setup
def setup_browser():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

# Normalize URL
def normalize_url(base, url):
    parsed = urlparse(urljoin(base, url.strip()))
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

# Save HTML content to file
def save_html(content, filename):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Error saving HTML file: {e}")

# Clean HTML content
def clean_html(soup):
    for element in soup(["script", "style", "link"]):
        element.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    return soup

# Extract content and links from a page
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

# Get internal links from a page
def get_links(soup, base_url):
    base_domain = urlparse(base_url).netloc
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = normalize_url(base_url, link['href'])
        if urlparse(full_url).netloc == base_domain:
            links.add(full_url)
    return links

# Crawl site
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

# API models
class CrawlRequest(BaseModel):
    url: str
    output_dir: Optional[str] = 'output'
    show_progress: Optional[bool] = False
    clean_content: Optional[bool] = True
    max_links: Optional[int]

class CrawlResponse(BaseModel):
    total_links: int
    pages: List[dict]
    output_directory: str

# API endpoints
@app.post("/crawl", response_model=CrawlResponse)
async def crawl(crawl_request: CrawlRequest):
    # Ensure the output directory exists
    if not os.path.exists(crawl_request.output_dir):
        os.makedirs(crawl_request.output_dir)

    crawled_pages = crawl_site(crawl_request.url, crawl_request.output_dir,
                               crawl_request.show_progress, crawl_request.clean_content,
                               crawl_request.max_links if crawl_request.max_links else None)

    # Create JSON summary
    summary = {
        'total_links': len(crawled_pages),
        'pages': crawled_pages,
        'output_directory': os.path.abspath(crawl_request.output_dir)
    }
    
    summary_path = os.path.join(crawl_request.output_dir, 'summary.json')
    with open(summary_path, 'w') as json_file:
        json.dump(summary, json_file, indent=4)

    return summary

# Serve index.html at root URL
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=open("static/index.html", "r", encoding="utf-8").read())

# Main function to run the server using uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8803)
