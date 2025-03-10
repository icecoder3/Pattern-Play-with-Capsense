# Capacitive Sensing Data-based Pattern Recognition System

## Overview
This project implements a pattern recognition system that captures capacitive sensing data from a microcontroller, 
processes it, and compares it with stored patterns for identification. The system normalizes, filters, and analyzes input 
patterns using Procrustes analysis and covariance similarity.

## Features
- **Real-time Data Acquisition** : Reads capacitive sensing data via a serial (COM) port.
- **Pattern Storage and Retrieval** : Saves reference patterns in a JSON file for later comparison.
- **Data Preprocessing** : Applies outlier removal, Gaussian smoothing, normalization, and resampling.
- **Pattern Matching** : Uses Procrustes analysis and covariance coefficient to compare patterns.
- **Robust Similarity Calculation** : Handles variations in size and position.
- **Configurable Matching Threshold** : Allows tuning similarity confidence for accuracy.

## Installation & Setup

### Requirements
- Python 3.x
- NumPy
- SciPy
- scikit-learn
- PySerial

### Installation
```sh
pip install numpy scipy scikit-learn pyserial
```

## Usage

### 1. Storing a New Pattern
```sh
python new.py
```
- Enter 'store' mode and provide a name for the pattern.
- Draw a pattern with the capacitive sensor.
- The system processes and saves it in `reference_patterns.json`.

### 2. Recognizing a Drawn Pattern
```sh
python tictactoe2.py
```
- Choose 'check' mode.
- Draw a pattern, and the system matches it with stored references.
- Outputs the closest match or reports no match found.

## Process Flow

### 1. Data Collection
- Reads capacitive sensing data from the microcontroller via serial communication.
- Converts X, Y coordinates into an array and stores them.

### 2. Data Preprocessing
- **Outlier Removal:** Uses Z-score filtering to remove outliers.
- **Gaussian Smoothing:** Reduces sensor noise.
- **Normalization:** Applies Z-score normalization to standardize data.
- **Resampling:** Interpolates data to a constant number of points (default: 100).

### 3. Pattern Recognition
- Loads stored patterns from `reference_patterns.json`.
- Compares new input with stored patterns using Procrustes analysis.
- Computes covariance coefficient for similarity measurement.

### 4. Decision Making
- If similarity exceeds the threshold (0.75), the system recognizes the pattern.
- Otherwise, it reports "No matching pattern found."

## Methods Used

### 1. Procrustes Analysis
Aligns two shapes by scaling, translating, and rotating them to minimize differences, ensuring robust pattern matching.

### 2. Covariance Coefficient Similarity
- Computes the correlation between aligned X and Y coordinates.
- Generates a similarity score between two shapes.

### 3. Gaussian Smoothing
- Reduces noise and fluctuations in sensor data.
- Uses a Gaussian filter with a predefined smoothing factor.

### 4. Z-score Normalization
- Keeps data within a standardized range.
- Ensures consistency across different pattern sizes.

## Complexity Analysis

### Time Complexity
- **Data Preprocessing** - O(N)
- **Procrustes Alignment** - O(N)
- **Covariance Computation** - O(N)

### Space Complexity
- **JSON Storage** - O(M × N)
- **In-Memory Processing** - O(M × N)

## License
This project is open-source and available under the MIT License.
