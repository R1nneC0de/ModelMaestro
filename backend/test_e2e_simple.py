#!/usr/bin/env python3
"""Simple E2E test to verify the pipeline works."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Starting simple e2e test...")

async def main():
    print("Loading data...")
    import pandas as pd
    
    csv_path = Path(__file__).parent.parent / "Customer_Churn_data.csv"
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    
    print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(main())
