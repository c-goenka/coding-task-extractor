"""Run all tests for the simplified pipeline."""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def run_all_tests():
    """Run all available tests."""
    
    print("="*70)
    print("SIMPLIFIED PIPELINE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    tests_to_run = [
        ("Model Validation", "test_models.py"),
        ("Paper Filtering", "test_filter.py"),
        ("API Key Setup", "test_api_key.py"),
        ("Binary Classification", "test_binary_classifier.py"),
        ("Mock Pipeline Logic", "test_pipeline_mock.py"),
        ("Complete Pipeline", "test_complete_pipeline.py"),
        ("Real Programming Papers", "test_real_programming_papers.py"),
    ]
    
    results = {}
    
    for test_name, test_file in tests_to_run:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 50)
        
        try:
            # Import and run the test
            test_path = Path(__file__).parent / test_file
            
            if test_path.exists():
                # Execute the test file
                exec(open(test_path).read())
                results[test_name] = "✅ PASSED"
                print(f"✅ {test_name} completed successfully")
            else:
                results[test_name] = "⚠️ SKIPPED (file not found)"
                print(f"⚠️ {test_name} skipped - file not found")
                
        except Exception as e:
            results[test_name] = f"❌ FAILED ({str(e)})"
            print(f"❌ {test_name} failed: {e}")
    
    # Print summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        print(f"{result:<20} {test_name}")
    
    # Count results
    passed = sum(1 for r in results.values() if "PASSED" in r)
    failed = sum(1 for r in results.values() if "FAILED" in r)
    skipped = sum(1 for r in results.values() if "SKIPPED" in r)
    total = len(results)
    
    print(f"\n📊 Summary: {passed} passed, {failed} failed, {skipped} skipped out of {total} total")
    
    if failed == 0:
        print("\n🎉 All available tests passed!")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(run_all_tests())