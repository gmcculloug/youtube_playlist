#!/usr/bin/env python3
"""
Test runner script for the YouTube Playlist Creator
"""

import sys
import subprocess
import argparse
import os

def run_tests(verbose=False, coverage=False, specific_test=None):
    """Run the test suite"""
    
    # Check if we're in the right directory
    if not os.path.exists('test_create_playlist.py'):
        print("Error: test_create_playlist.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Build the test command
    cmd = ['python', '-m', 'unittest']
    
    if verbose:
        cmd.append('-v')
    
    if specific_test:
        cmd.extend(['-k', specific_test])
    
    if coverage:
        # Use pytest for coverage
        cmd = ['python', '-m', 'pytest', 'test_create_playlist.py']
        if verbose:
            cmd.append('-v')
        if specific_test:
            cmd.extend(['-k', specific_test])
        cmd.extend(['--cov=create_playlist', '--cov=youtube', '--cov=spotify', '--cov-report=html'])
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("-" * 50)
        print("✅ All tests passed!")
        
        if coverage:
            print("📊 Coverage report generated in htmlcov/")
            print("Open htmlcov/index.html in your browser to view the report.")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("-" * 50)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ Error: Python not found in PATH")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run tests for YouTube Playlist Creator')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Run tests in verbose mode')
    parser.add_argument('-c', '--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('-t', '--test', type=str,
                       help='Run specific test by name pattern')
    
    args = parser.parse_args()
    
    success = run_tests(
        verbose=args.verbose,
        coverage=args.coverage,
        specific_test=args.test
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 