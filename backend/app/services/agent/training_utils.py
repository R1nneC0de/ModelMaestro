"""
Training utility functions.

Provides helper functions for training operations.
"""

import hashlib
import json
import sys
from typing import Dict, Any


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        import numpy as np
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def generate_preprocessing_hash(metadata: Dict[str, Any]) -> str:
    """
    Generate hash of preprocessing metadata for provenance.
    
    Args:
        metadata: Preprocessing metadata
        
    Returns:
        SHA256 hash string
    """
    # Convert to stable JSON string with numpy support
    json_str = json.dumps(metadata, sort_keys=True, cls=NumpyEncoder)
    
    # Generate hash
    hash_obj = hashlib.sha256(json_str.encode())
    return hash_obj.hexdigest()


def get_package_versions() -> Dict[str, str]:
    """
    Get versions of key packages used in training.
    
    Returns:
        Dictionary of package names to versions
    """
    packages = {}
    
    try:
        import sklearn
        packages["scikit-learn"] = sklearn.__version__
    except (ImportError, Exception):
        pass
    
    try:
        import xgboost
        packages["xgboost"] = xgboost.__version__
    except (ImportError, Exception):
        pass
    
    try:
        import pandas
        packages["pandas"] = pandas.__version__
    except (ImportError, Exception):
        pass
    
    try:
        import numpy
        packages["numpy"] = numpy.__version__
    except (ImportError, Exception):
        pass
    
    packages["python"] = sys.version.split()[0]
    
    return packages
