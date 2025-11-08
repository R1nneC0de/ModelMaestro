#!/usr/bin/env python3
"""Wrapper to run the e2e pipeline test with better error handling."""

import sys
import traceback

print("Starting e2e pipeline test...")

try:
    # Import and run the test
    sys.path.insert(0, 'backend')
    from test_e2e_pipeline import test_e2e_pipeline
    import asyncio
    
    print("Running async test...")
    asyncio.run(test_e2e_pipeline())
    print("\nTest completed successfully!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
