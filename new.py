import json
import os
import numpy as np
from read_coordinates import read_coordinates, get_serial_port
from sklearn.preprocessing import StandardScaler
from scipy.interpolate import interp1d
from scipy.spatial import procrustes
from scipy.ndimage import gaussian_filter1d
from scipy.stats import zscore

# File to store reference patterns
REFERENCE_FILE = "reference_patterns.json"

def save_reference_pattern(name, shape):
    """Save a reference pattern to a JSON file after processing."""
    if os.path.exists(REFERENCE_FILE):
        with open(REFERENCE_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    shape = preprocess_shape(shape)  # Apply filters before saving
    data[name] = shape.tolist()  # Convert NumPy array to list for JSON storage

    with open(REFERENCE_FILE, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Pattern '{name}' saved successfully.")

def load_reference_patterns():
    """Load reference patterns from a JSON file."""
    if not os.path.exists(REFERENCE_FILE):
        print("No reference patterns found.")
        return {}

    with open(REFERENCE_FILE, "r") as f:
        return json.load(f)

def normalize_shape(shape):
    """Normalize shape coordinates using Z-score normalization (better than Min-Max)."""
    scaler = StandardScaler()
    return scaler.fit_transform(shape)

def resample_shape(shape, target_length=100):
    """Resample the shape to match the target length using linear interpolation."""
    if len(shape) == target_length:
        return shape  # No need to resample

    shape = np.array(shape)
    x, y = shape[:, 0], shape[:, 1]

    new_indices = np.linspace(0, len(shape) - 1, target_length)
    interp_x = interp1d(np.arange(len(x)), x, kind='linear')(new_indices)
    interp_y = interp1d(np.arange(len(y)), y, kind='linear')(new_indices)

    return np.column_stack((interp_x, interp_y))

def gaussian_smooth(shape, sigma=1):
    """Apply Gaussian smoothing to coordinates to remove noise."""
    shape = np.array(shape)
    smoothed_x = gaussian_filter1d(shape[:, 0], sigma=sigma)
    smoothed_y = gaussian_filter1d(shape[:, 1], sigma=sigma)
    return np.column_stack((smoothed_x, smoothed_y))

def remove_outliers(shape, threshold=2.0):
    """Removes points that are statistical outliers using Z-score filtering."""
    shape = np.array(shape)
    
    # Compute Z-scores for X and Y
    z_scores_x = zscore(shape[:, 0])
    z_scores_y = zscore(shape[:, 1])

    # Filter only points with Z-score within the threshold
    filtered = shape[(np.abs(z_scores_x) < threshold) & (np.abs(z_scores_y) < threshold)]
    
    return filtered if len(filtered) > 5 else shape  # Ensure minimum points remain

def preprocess_shape(shape):
    """Apply filtering and smoothing to the shape for better accuracy."""
    shape = remove_outliers(shape)
    shape = gaussian_smooth(shape)
    shape = normalize_shape(shape)
    return resample_shape(shape)

def compute_covariance_coefficient(shape1, shape2):
    """Compute the covariance coefficient after Procrustes alignment, if needed."""
    if len(shape1) != len(shape2):
        print("Shape lengths do not match, skipping Procrustes.")
        return 0, shape1, shape2  # Return 0 similarity if not comparable

    # Perform Procrustes Analysis only if needed
    shape1, shape2, _ = procrustes(shape1, shape2)

    shape1_x, shape1_y = shape1[:, 0], shape1[:, 1]
    shape2_x, shape2_y = shape2[:, 0], shape2[:, 1]

    cov_x = np.cov(shape1_x, shape2_x)[0, 1]
    cov_y = np.cov(shape1_y, shape2_y)[0, 1]

    std_x1, std_x2 = np.std(shape1_x), np.std(shape2_x)
    std_y1, std_y2 = np.std(shape1_y), np.std(shape2_y)

    if std_x1 * std_x2 == 0 or std_y1 * std_y2 == 0:
        return 0, shape1, shape2  # Prevent division by zero

    cov_coeff_x = cov_x / (std_x1 * std_x2)
    cov_coeff_y = cov_y / (std_y1 * std_y2)

    return (cov_coeff_x + cov_coeff_y) / 2, shape1, shape2

def identify_pattern(new_shape):
    """Identify the closest matching pattern from stored references using Procrustes similarity."""
    reference_patterns = load_reference_patterns()
    if not reference_patterns:
        print("No reference patterns found.")
        return None

    # Apply preprocessing filters
    new_shape = preprocess_shape(new_shape)

    best_match = None
    best_similarity = -1

    for name, ref_shape in reference_patterns.items():
        ref_shape = np.array(ref_shape)

        # Preprocess reference shape
        ref_shape = preprocess_shape(ref_shape)

        # Compare using Procrustes alignment and covariance
        similarity, _, _ = compute_covariance_coefficient(ref_shape, new_shape)

        print(f"Similarity with '{name}': {similarity:.4f}")

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = name

    # Only return the match if similarity is high enough
    if best_similarity < 0.75:
        print("Confidence too low. No reliable match found.")
        return None

    return best_match

if __name__ == "__main__":
    serial_port = get_serial_port()

    mode = input("Enter 'store' to save a pattern or 'check' to identify a new pattern: ").strip().lower()

    if mode == "store":
        name = input("Enter a name for the pattern: ").strip()
        print(f"Recording '{name}' pattern...")

        coordinates = read_coordinates(serial_port=serial_port, timeout=5)
        
        if len(coordinates) == 0:
            print("Error: No coordinates received. Check if the sensor is connected properly.")
            exit()

        shape = np.array(coordinates)

        save_reference_pattern(name, shape)

    elif mode == "check":
        print("Scanning new pattern...")
        coordinates = read_coordinates(serial_port=serial_port, timeout=5)

        if len(coordinates) == 0:
            print("Error: No coordinates received. Check if the sensor is connected properly.")
            exit()

        new_shape = np.array(coordinates)
        best_match = identify_pattern(new_shape)

        if best_match:
            print(f"Identified as: {best_match}")
        else:
            print("No matching pattern found.")
