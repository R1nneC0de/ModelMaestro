"""Test script for the Problem Analyzer with Customer Churn dataset."""

import asyncio
import sys
import csv
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.agent.analyzer import ProblemAnalyzer
from app.services.agent.gemini_client import GeminiClient


async def test_problem_analyzer():
    """Test the problem analyzer with the Customer Churn dataset."""
    
    print("🔍 Testing Problem Analyzer with Customer Churn Dataset\n")
    print("=" * 70)
    
    # Read a sample of the CSV data
    csv_file = "Customer_Churn_data.csv"
    
    if not Path(csv_file).exists():
        print(f"❌ Error: {csv_file} not found")
        return False
    
    # Read first 50 rows as sample (better for analysis)
    sample_size = 50
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        sample_rows = [row for i, row in enumerate(reader) if i < sample_size]
        
        # Get column names
        columns = list(sample_rows[0].keys()) if sample_rows else []
    
    print(f"📊 Dataset: {csv_file}")
    print(f"📈 Columns: {len(columns)}")
    print(f"🔢 Sample rows loaded: {len(sample_rows)} (for better analysis)\n")
    
    # Problem description
    problem_description = """
    I want to predict customer churn for a telecommunications company.
    The dataset contains customer information including demographics, 
    account details, and service usage patterns. The goal is to identify 
    customers who are likely to leave the service so we can take 
    proactive retention measures.
    """
    
    print("📝 Problem Description:")
    print(problem_description.strip())
    print("\n" + "=" * 70 + "\n")
    
    # Initialize analyzer
    print("🤖 Initializing Problem Analyzer with Gemini...")
    analyzer = ProblemAnalyzer()
    
    # Perform analysis
    print("🔬 Analyzing problem...\n")
    
    try:
        analysis = await analyzer.analyze_problem(
            problem_description=problem_description,
            data_sample=sample_rows,
            num_samples=10000,  # We know from the upload
            is_labeled=True,  # Assuming there's a churn label
            data_type_hint="tabular",
            file_extensions=[".csv"]
        )
        
        print("✅ Analysis Complete!\n")
        print("=" * 70)
        print("\n📊 ANALYSIS RESULTS:\n")
        
        print(f"🎯 Problem Type: {analysis.problem_type.value}")
        print(f"📁 Data Type: {analysis.data_type.value}")
        print(f"🏢 Domain: {analysis.domain}")
        print(f"🎲 Confidence: {analysis.confidence:.2%}")
        print(f"⚡ Complexity Score: {analysis.complexity_score:.2f}")
        print(f"🏷️  Is Labeled: {analysis.is_labeled}")
        
        if analysis.num_classes:
            print(f"📊 Number of Classes: {analysis.num_classes}")
        
        if analysis.target_variable:
            print(f"🎯 Target Variable: {analysis.target_variable}")
        
        print(f"\n📏 Suggested Metrics:")
        for metric in analysis.suggested_metrics:
            print(f"   • {metric}")
        
        print(f"\n💡 Reasoning:")
        print(f"   {analysis.reasoning}")
        
        if analysis.additional_insights:
            print(f"\n🔍 Additional Insights:")
            for key, value in analysis.additional_insights.items():
                print(f"   • {key}: {value}")
        
        print("\n" + "=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_problem_analyzer())
    sys.exit(0 if success else 1)
