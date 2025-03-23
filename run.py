#!/usr/bin/env python3
"""
Simple launcher script for the PerspectiveFix application.
"""
import os
import sys

# Add the src directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

# Import and run the main application
from main import main

if __name__ == "__main__":
    main()
