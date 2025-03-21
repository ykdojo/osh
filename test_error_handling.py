#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock

def test_error_handler():
    """
    Simplified test function that mimics the error handling in recorder.py
    """
    process = MagicMock()
    process.returncode = 1
    
    # Test case 1: Normal error with stderr
    process.stderr = MagicMock()
    process.stderr.read.return_value = b"Some ffmpeg error"
    
    stderr_msg = ""
    if hasattr(process, 'stderr') and process.stderr:
        stderr_msg = process.stderr.read().decode('utf-8')
        
    verbose = True  # Set to True for testing
    if stderr_msg and "Interrupt" not in stderr_msg and "Operation not permitted" not in stderr_msg and verbose:
        print(f"Error during screen recording: {stderr_msg}")
    elif verbose:
        print(f"Error during screen recording (return code: {process.returncode})")
    
    # Test case 2: Interrupt error
    process.stderr.read.return_value = b"Interrupt by user"
    
    stderr_msg = ""
    if hasattr(process, 'stderr') and process.stderr:
        stderr_msg = process.stderr.read().decode('utf-8')
        
    verbose = True  # Set to True for testing
    if stderr_msg and "Interrupt" not in stderr_msg and "Operation not permitted" not in stderr_msg and verbose:
        print(f"Error during screen recording: {stderr_msg}")
    elif verbose:
        print(f"Error during screen recording (return code: {process.returncode})")

if __name__ == "__main__":
    test_error_handler()