#!/usr/bin/env python3

import os
import json
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup, Comment, NavigableString
import time
from fastapi import FastAPI, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import yaml
from weasyprint import HTML
from PyPDF2 import PdfFileMerger
from markdown2 import markdown
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from contextlib import contextmanager
from datetime import datetime
import uuid
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import helper scripts
try:
    from clean_and_strip import process_html_files
    from yaml_to_json import convert_yaml_to_json
    from merge_docs_into_pdf import convert_files_to_pdf
except ImportError as e:
    print(f"Warning: Some helper scripts could not be imported: {e}")
    print("Some functionality may be limited")

app = FastAPI(
    title="SPYCrawl API",
    description="Web Crawling & Document Processing Suite",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
static_dir = Path("static")
if not static_dir.exists():
    static_dir.mkdir(parents=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# API Models
class CrawlRequest(BaseModel):
    url: str
    output_dir: Optional[str] = 'output'
    show_progress: Optional[bool] = False
    clean_content: Optional[bool] = True
    max_links: Optional[int]

class CleanRequest(BaseModel):
    input_dir: str
    output_dir: str

class ConvertRequest(BaseModel):
    input_dir: str
    output_dir: str

class PDFRequest(BaseModel):
    directory: str
    output: str
    no_merge: Optional[bool] = False

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///crawls.db')
SessionLocal = sessionmaker(bind=engine)

class CrawlJob(Base):
    __tablename__ = 'crawl_jobs'
    
    id = Column(String, primary_key=True)
    start_url = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # pending, running, completed, failed
    output_dir = Column(String)
    total_pages = Column(Integer, default=0)
    total_bytes = Column(Integer, default=0)
    error_message = Column(String)
    pages = Column(JSON)  # Store pages as JSON
    
    def to_dict(self):
        return {
            "id": self.id,
            "start_url": self.start_url,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "output_dir": self.output_dir,
            "total_pages": self.total_pages,
            "total_bytes": self.total_bytes,
            "error_message": self.error_message,
            "pages": self.pages or []
        }

# Create tables
Base.metadata.create_all(engine)

class CrawlManager:
    def __init__(self):
        self.db = SessionLocal()
        
    def create_session(self, url: str) -> CrawlJob:
        job = CrawlJob(
            id=str(uuid.uuid4()),
            start_url=url,
            timestamp=datetime.now(),
            status="pending",
            pages=[]
        )
        self.db.add(job)
        self.db.commit()
        return job
        
    def get_session(self, session_id: str) -> Optional[CrawlJob]:
        return self.db.query(CrawlJob).filter(CrawlJob.id == session_id).first()
        
    def list_sessions(self) -> List[Dict]:
        jobs = self.db.query(CrawlJob).order_by(CrawlJob.timestamp.desc()).all()
        return [job.to_dict() for job in jobs]
        
    def update_session(self, job: CrawlJob):
        self.db.commit()

# Initialize the crawl manager
crawl_manager = CrawlManager()

@contextmanager
def managed_browser():
    """Context manager for browser setup and cleanup"""
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Use webdriver_manager for cross-platform compatibility
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        yield driver
    except WebDriverException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Chrome browser: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error setting up browser: {str(e)}"
        )
    finally:
        if driver:
            driver.quit()

def normalize_url(base, url):
    try:
        parsed = urlparse(urljoin(base, url.strip()))
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid URL format: {str(e)}"
        )

def save_html(content, filename):
    try:
        # Convert to Path object for secure path handling
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding='utf-8')
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving HTML file: {str(e)}"
        )

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
        raise HTTPException(status_code=500, detail=f"Error processing URL {url}: {str(e)}")

def get_links(soup, base_url):
    base_domain = urlparse(base_url).netloc
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = normalize_url(base_url, link['href'])
        if urlparse(full_url).netloc == base_domain:
            links.add(full_url)
    return links

def crawl_site(start_url, output_dir, show_progress, clean_content, max_links):
    """Updated crawl_site function using database storage"""
    session = crawl_manager.create_session(start_url)
    session.output_dir = output_dir
    session.status = "running"
    crawl_manager.update_session(session)
    
    visited = set()
    to_visit = {normalize_url(start_url, start_url)}
    total_bytes = 0
    
    try:
        with managed_browser() as driver:
            while to_visit and (max_links is None or len(visited) < max_links):
                current_url = to_visit.pop()
                if current_url in visited:
                    continue
                    
                visited.add(current_url)
                page_info, new_links = extract_content(driver, current_url, output_dir, clean_content)
                
                if page_info:
                    # Calculate page size
                    file_path = Path(page_info['file_path'])
                    if file_path.exists():
                        total_bytes += file_path.stat().st_size
                    
                    session.pages.append(page_info)
                    session.total_pages = len(session.pages)
                    session.total_bytes = total_bytes
                    crawl_manager.update_session(session)
                    
                to_visit.update(new_links - visited)
                
                if show_progress:
                    print(f"[{session.total_pages} saved : {current_url}]")
        
        session.status = "completed"
        crawl_manager.update_session(session)
        return session
    except Exception as e:
        session.status = "failed"
        session.error_message = str(e)
        crawl_manager.update_session(session)
        raise e

# API Routes
@app.get("/")
async def root():
    """Redirect root to /pages"""
    return RedirectResponse(url="/pages")

@app.get("/pages")
async def pages():
    try:
        index_path = static_dir / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="index.html not found")
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crawls")
async def list_crawls():
    """List all crawl sessions"""
    return crawl_manager.list_sessions()

@app.get("/api/crawls/{session_id}")
async def get_crawl(session_id: str):
    """Get details of a specific crawl session"""
    session = crawl_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Crawl session not found")
    return session.to_dict()

@app.post("/api/crawl")
async def crawl(crawl_request: CrawlRequest):
    """Updated crawl endpoint that returns session information"""
    try:
        if not os.path.exists(crawl_request.output_dir):
            os.makedirs(crawl_request.output_dir)

        session = crawl_site(
            crawl_request.url,
            crawl_request.output_dir,
            crawl_request.show_progress,
            crawl_request.clean_content,
            crawl_request.max_links
        )

        # Save summary to file
        summary = session.to_dict()
        summary_path = os.path.join(crawl_request.output_dir, 'summary.json')
        with open(summary_path, 'w') as json_file:
            json.dump(summary, json_file, indent=4)

        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clean")
async def clean(clean_request: CleanRequest):
    try:
        process_html_files(clean_request.input_dir, clean_request.output_dir)
        return {"message": "HTML files cleaned successfully", "output_dir": clean_request.output_dir}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/convert")
async def convert(convert_request: ConvertRequest):
    try:
        convert_yaml_to_json(convert_request.input_dir, convert_request.output_dir)
        return {"message": "YAML files converted to JSON successfully", "output_dir": convert_request.output_dir}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pdf")
async def generate_pdf(pdf_request: PDFRequest):
    try:
        if pdf_request.no_merge:
            output_dir = os.path.splitext(pdf_request.output)[0]
            os.makedirs(output_dir, exist_ok=True)
            convert_files_to_pdf(pdf_request.directory, output_dir)
            return {"message": "PDFs generated successfully", "output_dir": output_dir}
        else:
            convert_files_to_pdf(pdf_request.directory, pdf_request.output)
            return {"message": "PDF generated successfully", "output_file": pdf_request.output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{directory:path}")
async def list_files(directory: str):
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            raise HTTPException(status_code=404, detail="Directory not found")
        if not dir_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        files = [str(f.relative_to(dir_path)) for f in dir_path.rglob("*") if f.is_file()]
        return {"files": files}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filepath:path}")
async def download_file(filepath: str):
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        return FileResponse(str(file_path))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting SPYCrawl server...")
    print("Access the web interface at http://127.0.0.1:8803")
    print("API documentation available at http://127.0.0.1:8803/docs")
    uvicorn.run("spycrawl:app", host="127.0.0.1", port=8803, reload=True, reload_dirs=["static"]) 