#!/usr/bin/env python3

import unittest
import sys
import argparse
from unittest import TestLoader, TextTestRunner
from test_spycrawl_api import TestSpyCrawlAPI

def run_tests(verbosity=2):
    """Run all API endpoint tests"""
    # Create a test suite
    loader = TestLoader()
    suite = loader.loadTestsFromTestCase(TestSpyCrawlAPI)
    
    # Run the tests
    runner = TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return True if all tests passed, False otherwise
    return result.wasSuccessful()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run API endpoint tests for SPYCrawl")
    parser.add_argument("--verbosity", "-v", type=int, choices=[0, 1, 2], default=2,
                      help="Verbosity level: 0=quiet, 1=minimal, 2=verbose")
    args = parser.parse_args()
    
    print("Running SPYCrawl API endpoint tests...")
    success = run_tests(args.verbosity)
    
    if success:
        print("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        print("\nSome tests failed. Check the output for details.")
        sys.exit(1)