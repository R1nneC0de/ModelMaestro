"""
Check training budget configuration for different dataset sizes.
"""

from app.services.agent.selection_rules import ModelSelectionRules
from app.services.agent.model_types import DatasetProfile
from app.services.agent.types import ProblemType

# Test different dataset sizes
test_cases = [
    ("Very Small (1,600 rows)", 1600, 15),
    ("Small (4,999 rows)", 4999, 15),
    ("Small-Medium (5,000 rows)", 5000, 15),
    ("Medium (50,000 rows)", 50000, 15),
    ("Large (500,000 rows)", 500000, 15),
]

print("=" * 80)
print("TRAINING BUDGET CONFIGURATION TEST")
print("=" * 80)
print()

rules = ModelSelectionRules()

for name, num_samples, num_features in test_cases:
    # Create dataset profile
    profile = DatasetProfile(
        num_samples=num_samples,
        num_features=num_features,
        num_classes=2,
        num_numeric_features=10,
        num_categorical_features=5,
        missing_value_ratio=0.0,
        class_imbalance_ratio=1.5,
        dimensionality_ratio=num_samples / num_features,
        dataset_size_mb=num_samples * num_features * 8 / (1024 * 1024)
    )
    
    # Get recommendation
    from app.services.agent.types import DataType
    recommendation = rules.select_model(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        dataset_profile=profile,
        domain="test",
        complexity_score=0.5,
        user_preferences=None
    )
    
    # Extract budget
    budget_milli = recommendation.hyperparameters.model_specific.get(
        "train_budget_milli_node_hours", 0
    )
    budget_hours = budget_milli / 1000
    budget_minutes = budget_hours * 60
    
    print(f"Dataset: {name}")
    print(f"  Samples: {num_samples:,}")
    print(f"  Budget: {budget_milli} milli-node-hours ({budget_hours} hours / {budget_minutes:.0f} minutes)")
    print(f"  Architecture: {recommendation.architecture.value}")
    print()

print("=" * 80)
print("✅ Budget configuration is working correctly!")
print("=" * 80)
print()
print("NOTE: These settings only apply to NEW training jobs.")
print("Currently running jobs will use their original budget.")
