#!/usr/bin/env python3
"""Display latest test session summary."""

import json
import glob
import os
import sys

def show_latest_session():
    """Show the latest test session summary."""
    files = glob.glob('results/session_*.json')
    
    if not files:
        print('No test sessions found')
        return
    
    latest = max(files, key=os.path.getctime)
    
    try:
        with open(latest) as f:
            data = json.load(f)
            summary = data['summary']
            
            print(f"Session: {summary['session_id']}")
            print(f"Total Tests: {summary['total_tests']}")
            print(f"Passed: {summary['passed_tests']}")
            print(f"Failed: {summary['failed_tests']}")
            print(f"Success Rate: {summary['success_rate']:.1f}%")
            print("Tests by Layer:")
            for layer, count in summary['test_results_by_layer'].items():
                print(f"  {layer.title()}: {count}")
            
            if summary['compliance_results'] > 0:
                print(f"Compliance Results: {summary['compliance_results']}")
                
                # Show compliance details if available
                if 'compliance_results' in data and data['compliance_results']:
                    print("\nCompliance Details:")
                    for comp in data['compliance_results']:
                        print(f"  {comp['domain']}: {comp['compliance_rate']:.1f}% "
                              f"({comp['compliant_objects']}/{comp['total_objects']} compliant)")
            
            print(f"\nSession file: {latest}")
            
    except Exception as e:
        print(f"Error reading session file: {e}")

if __name__ == "__main__":
    show_latest_session()