#!/usr/bin/env python3

import os
import requests
import json
import time
import unittest
import shutil
from pathlib import Path
import tempfile
import threading
import subprocess
import atexit
from urllib.parse import urljoin

# Base URL for the API
BASE_URL = "http://127.0.0.1:8803"

def start_server():
    """Start the spycrawl server in a separate process"""
    process = subprocess.Popen(
        ["python", "spycrawl.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Register shutdown function to kill the server when tests end
    atexit.register(lambda: process.terminate())
    # Wait for server to start
    time.sleep(3)
    return process

class TestSpyCrawlAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        # Start the server
        cls.server_process = start_server()
        
        # Create temp directories for testing
        cls.test_output_dir = Path(tempfile.mkdtemp())
        cls.test_input_dir = Path(tempfile.mkdtemp())
        cls.test_clean_dir = Path(tempfile.mkdtemp())
        cls.test_convert_dir = Path(tempfile.mkdtemp())
        cls.test_pdf_dir = Path(tempfile.mkdtemp())
        
        # Create a sample HTML file in the input directory
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>This is a test page</h1>
            <p>This is a paragraph</p>
            <script>alert('This should be removed when cleaned');</script>
        </body>
        </html>
        """
        html_file = cls.test_input_dir / "test.html"
        html_file.write_text(sample_html)
        
        # Create a sample YAML file in the input directory
        sample_yaml = """
        name: Test
        version: 1.0
        description: Test YAML file
        items:
          - item1
          - item2
          - item3
        """
        yaml_file = cls.test_input_dir / "test.yaml"
        yaml_file.write_text(sample_yaml)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        # Kill the server
        cls.server_process.terminate()
        
        # Clean up temp directories
        shutil.rmtree(cls.test_output_dir, ignore_errors=True)
        shutil.rmtree(cls.test_input_dir, ignore_errors=True)
        shutil.rmtree(cls.test_clean_dir, ignore_errors=True)
        shutil.rmtree(cls.test_convert_dir, ignore_errors=True)
        shutil.rmtree(cls.test_pdf_dir, ignore_errors=True)
    
    def test_01_root_redirect(self):
        """Test that root endpoint redirects to /pages"""
        response = requests.get(BASE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.url.endswith("/pages"))
    
    def test_02_pages(self):
        """Test that /pages endpoint returns HTML"""
        response = requests.get(f"{BASE_URL}/pages")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["Content-Type"])
    
    def test_03_crawl_api(self):
        """Test the crawl API endpoint"""
        payload = {
            "url": "http://example.com",
            "output_dir": str(self.test_output_dir),
            "show_progress": True,
            "clean_content": True,
            "max_links": 1
        }
        response = requests.post(f"{BASE_URL}/api/crawl", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_links", data)
        self.assertIn("pages", data)
        self.assertIn("output_directory", data)
        self.assertIn("session_id", data)
        
        # Store session ID for later tests
        self.session_id = data["session_id"]
    
    def test_04_list_crawls(self):
        """Test listing all crawl sessions"""
        response = requests.get(f"{BASE_URL}/api/crawls")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        # Should have at least one session from previous test
        self.assertGreater(len(data), 0)
    
    def test_05_get_crawl(self):
        """Test getting a specific crawl session"""
        response = requests.get(f"{BASE_URL}/api/crawls/{self.session_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.session_id)
        self.assertEqual(data["status"], "completed")
    
    def test_06_stop_crawl(self):
        """Test stopping a crawl job"""
        # First create a new crawl job
        payload = {
            "url": "http://example.com",
            "output_dir": str(self.test_output_dir),
            "show_progress": True,
            "clean_content": True,
            "max_links": 10
        }
        crawl_response = requests.post(f"{BASE_URL}/api/crawl", json=payload)
        self.assertEqual(crawl_response.status_code, 200)
        new_session_id = crawl_response.json()["session_id"]
        
        # Now stop the job
        stop_response = requests.post(f"{BASE_URL}/api/crawls/{new_session_id}/stop")
        self.assertEqual(stop_response.status_code, 200)
        self.assertIn("message", stop_response.json())
    
    def test_07_clean_api(self):
        """Test the clean API endpoint"""
        payload = {
            "input_dir": str(self.test_input_dir),
            "output_dir": str(self.test_clean_dir)
        }
        response = requests.post(f"{BASE_URL}/api/clean", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("output_dir", data)
        
        # Check that output files were created
        output_files = list(self.test_clean_dir.glob("*.html"))
        self.assertGreater(len(output_files), 0)
    
    def test_08_convert_api(self):
        """Test the convert API endpoint"""
        payload = {
            "input_dir": str(self.test_input_dir),
            "output_dir": str(self.test_convert_dir)
        }
        response = requests.post(f"{BASE_URL}/api/convert", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("output_dir", data)
        
        # Check that JSON files were created
        output_files = list(self.test_convert_dir.glob("*.json"))
        self.assertGreater(len(output_files), 0)
    
    def test_09_pdf_api(self):
        """Test the PDF generation API endpoint"""
        # Copy HTML files to test_pdf_dir first
        for html_file in self.test_input_dir.glob("*.html"):
            shutil.copy2(html_file, self.test_pdf_dir)
        
        # Test with no_merge=False
        pdf_output = self.test_pdf_dir / "output.pdf"
        payload = {
            "directory": str(self.test_pdf_dir),
            "output": str(pdf_output),
            "no_merge": False
        }
        response = requests.post(f"{BASE_URL}/api/pdf", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("output_file", data)
        
        # Test with no_merge=True
        pdf_output_dir = self.test_pdf_dir / "output_dir"
        payload = {
            "directory": str(self.test_pdf_dir),
            "output": str(pdf_output_dir),
            "no_merge": True
        }
        response = requests.post(f"{BASE_URL}/api/pdf", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("output_dir", data)
    
    def test_10_list_files(self):
        """Test the list files API endpoint"""
        response = requests.get(f"{BASE_URL}/api/files/{self.test_input_dir}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("files", data)
        self.assertGreater(len(data["files"]), 0)
    
    def test_11_download_file(self):
        """Test the download file API endpoint"""
        # Get a file from the test_input_dir
        file_path = next(self.test_input_dir.glob("*.html"))
        response = requests.get(f"{BASE_URL}/api/download/{file_path}")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 0)
    
    def test_12_clear_crawls(self):
        """Test clearing all crawl sessions"""
        response = requests.post(f"{BASE_URL}/api/crawls/clear")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        
        # Verify that all sessions were cleared
        list_response = requests.get(f"{BASE_URL}/api/crawls")
        self.assertEqual(list_response.status_code, 200)
        data = list_response.json()
        self.assertEqual(len(data), 0)

if __name__ == "__main__":
    unittest.main()