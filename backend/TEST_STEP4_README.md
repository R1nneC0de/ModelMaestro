# Step 4: Model Selection Agent - Testing Guide

## Quick Start

### Run the test with real Customer Churn data:

```bash
cd backend
python test_step4_with_churn_data.py
```

That's it! The test will automatically:
1. ✅ Find and analyze the Customer_Churn_data.csv file
2. ✅ Profile the dataset (10,000 customers with 15 columns)
3. ✅ Run model selection for 3 different scenarios
4. ✅ Generate Vertex AI training configurations

---

## What Gets Tested

### Dataset Analysis
- **10,000 rows** of customer churn data
- **14 features** (tenure, charges, services, demographics)
- **Target**: Binary classification (Yes/No churn)
- **Class Balance**: 51.5% No Churn, 48.5% Churn

### Model Selection Scenarios

#### 1. Cost-Optimized (Budget: $30)
**Result**: XGBoost - $8, 15 minutes
- Best for tight budgets
- No GPU required
- Good interpretability (0.70)

#### 2. Performance-Optimized (Budget: $100)
**Result**: AutoML Tabular - $19.50, 60 minutes
- Best accuracy/performance
- Tries multiple algorithms automatically
- **Recommended for production**

#### 3. Interpretability-Focused (Budget: $50)
**Result**: AutoML Tabular - $19.50, 60 minutes
- Balance of performance and cost

---

## Test Output

You'll see:
- 📊 Dataset overview and statistics
- 🎯 Target variable distribution
- 🤖 Model recommendations for each scenario
- ⚙️ Hyperparameter configurations
- 🚀 Ready-to-use Vertex AI training configs
- 📋 Side-by-side comparison table

---

## Requirements

All dependencies are already installed if you've set up the project. The test uses:
- Customer_Churn_data.csv (in repo root)
- Step 4 Model Selection Agent
- No API keys needed (rule-based mode)

---

## Troubleshooting

### File Not Found Error
Make sure you're running from the `backend` directory:
```bash
cd backend
python test_step4_with_churn_data.py
```

### Import Errors
The test automatically adds the backend directory to Python path. If you still get import errors, try:
```bash
export PYTHONPATH=/path/to/ModelMaestro/backend:$PYTHONPATH
python test_step4_with_churn_data.py
```

---

## Next Steps

After testing Step 4:
1. Review the model recommendations
2. Choose your preferred scenario (Cost vs Performance)
3. Move to **Step 5**: Training Orchestration
4. Use the generated Vertex AI config to train your model

---

## Files

- `test_step4_with_churn_data.py` - Main test script
- `CHURN_DATA_TEST_RESULTS.md` - Detailed analysis
- `../Customer_Churn_data.csv` - Test dataset
- `STEP4_TEST_RESULTS.md` - General test documentation
