#!/usr/bin/env python3
print("1. Script starting...")

import sys
print("2. sys imported")

from pathlib import Path
print("3. Path imported")

sys.path.insert(0, str(Path(__file__).parent))
print("4. Path modified")

try:
    from app.services.agent import ProblemAnalyzer
    print("5. ProblemAnalyzer imported")
except Exception as e:
    print(f"5. ERROR importing ProblemAnalyzer: {e}")
    import traceback
    traceback.print_exc()

print("6. Script completed")
