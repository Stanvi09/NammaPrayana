"""Crowd prediction model and baseline evaluator for NammaFlow coach crowding."""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import numpy as np

from backend.app.config import settings
from backend.app.utils.logger import logger


# Stair proximity metadata for 6-coach train configuration at Majestic
STAIR_PROXIMITY_MAP = {
    "C1": "Far from Stairs (Front)",
    "C2": "Adjacent to Stairs (High Traffic)",
    "C3": "Adjacent to Escalator / Stairs",
    "C4": "Moderate Walking Distance",
    "C5": "Far from Stairs",
    "C6": "Far from Stairs (Rear)",
}


class StationAverageBaseline:
    """Baseline model: predicts station-average crowd level regardless of coach position."""

    def predict(self, people_count: int, hour: float) -> str:
        is_rush = (8.0 <= hour <= 11.0) or (17.0 <= hour <= 20.5)
        if people_count > 55:
            return "High"
        elif people_count < 30:
            return "Low"
        return "High" if is_rush else "Medium"


class InterpretableCrowdDecisionTree:
    """Interpretable, tree-based classifier for crowd density.
    
    Trained on ground-truth hand counts. It explicitly splits on:
    - passenger count thresholds
    - staircase proximity / coach position
    - rush-hour temporal context
    
    This provides scientific interpretability required for the paper.
    """

    def __init__(self):
        # Learned decision thresholds from training dataset
        self.rush_high_threshold = 48.0
        self.rush_medium_threshold = 26.0
        self.offpeak_high_threshold = 56.0
        self.offpeak_medium_threshold = 29.0
        self.stair_bias = 6.0

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fits optimal thresholds using grid search over training set to maximize classification accuracy."""
        best_acc = 0.0
        best_params = (self.rush_high_threshold, self.rush_medium_threshold, self.offpeak_high_threshold, self.offpeak_medium_threshold, self.stair_bias)

        # Search grid around nominal values
        rush_high_vals = [44.0, 46.0, 48.0, 50.0, 52.0]
        rush_med_vals = [22.0, 24.0, 26.0, 28.0, 30.0]
        offpeak_high_vals = [52.0, 54.0, 56.0, 58.0]
        offpeak_med_vals = [24.0, 26.0, 28.0, 30.0]
        stair_biases = [4.0, 6.0, 8.0, 10.0]

        inv_map = {0: "Low", 1: "Medium", 2: "High"}
        y_labels = np.array([inv_map[val] for val in y])

        for r_high in rush_high_vals:
            for r_med in rush_med_vals:
                if r_med >= r_high:
                    continue
                for o_high in offpeak_high_vals:
                    for o_med in offpeak_med_vals:
                        if o_med >= o_high:
                            continue
                        for s_bias in stair_biases:
                            self.rush_high_threshold = r_high
                            self.rush_medium_threshold = r_med
                            self.offpeak_high_threshold = o_high
                            self.offpeak_medium_threshold = o_med
                            self.stair_bias = s_bias

                            preds = self.predict(X)
                            acc = np.mean(preds == y_labels)
                            if acc > best_acc:
                                best_acc = acc
                                best_params = (r_high, r_med, o_high, o_med, s_bias)

        (self.rush_high_threshold, self.rush_medium_threshold,
         self.offpeak_high_threshold, self.offpeak_medium_threshold,
         self.stair_bias) = best_params

    def predict_one(self, people_count: float, hour: float, coach_position: int, is_rush: float, stair_dist: float) -> str:
        # Stair adjustment: people bunch near stair coaches (C2, C3)
        stair_adjustment = (self.stair_bias if stair_dist == 0 else (-self.stair_bias if stair_dist >= 2 else 0.0))
        effective_count = people_count + stair_adjustment

        if is_rush:
            if effective_count >= self.rush_high_threshold:
                return "High"
            elif effective_count <= self.rush_medium_threshold:
                return "Low"
            else:
                return "Medium"
        else:
            if effective_count >= self.offpeak_high_threshold:
                return "High"
            elif effective_count <= self.offpeak_medium_threshold:
                return "Low"
            else:
                return "Medium"

    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = []
        for row in X:
            people_count, hour, coach_pos, is_rush, stair_dist, _ = row
            preds.append(self.predict_one(people_count, hour, int(coach_pos), is_rush, stair_dist))
        return np.array(preds)


class CrowdPredictionModel:
    """Trained ML classifier predicting coach crowding level (Low, Medium, High)."""

    CROWD_LABELS = ["Low", "Medium", "High"]

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or settings.CROWD_MODEL_PATH
        self.classifier = InterpretableCrowdDecisionTree()
        self.baseline = StationAverageBaseline()
        self._load_or_initialize()

    def _load_or_initialize(self):
        if self.model_path.exists():
            try:
                with open(self.model_path, "rb") as f:
                    data = pickle.load(f)
                    if "classifier" in data:
                        self.classifier = data["classifier"]
                        logger.info(f"Loaded trained crowd model from {self.model_path}")
                        return
            except Exception as e:
                logger.warning(f"Could not load crowd model from {self.model_path}: {e}")

    def extract_features(self, people_count: int, time_of_day_hour: float, coach_position: int) -> np.ndarray:
        is_rush = 1.0 if ((8.0 <= time_of_day_hour <= 11.0) or (17.0 <= time_of_day_hour <= 20.5)) else 0.0
        stair_distance = min(abs(coach_position - 2), abs(coach_position - 3))
        capacity_ratio = people_count / 80.0

        return np.array([
            float(people_count),
            float(time_of_day_hour),
            float(coach_position),
            float(is_rush),
            float(stair_distance),
            float(capacity_ratio)
        ], dtype=float).reshape(1, -1)

    def predict(self, people_count: int, time_of_day_hour: float, coach_position: int) -> str:
        features = self.extract_features(people_count, time_of_day_hour, coach_position)
        pred = self.classifier.predict(features)[0]
        return str(pred)

    def predict_with_baseline_comparison(
        self,
        people_count: int,
        time_of_day_hour: float,
        coach_position: int
    ) -> Dict[str, Any]:
        model_pred = self.predict(people_count, time_of_day_hour, coach_position)
        baseline_pred = self.baseline.predict(people_count, time_of_day_hour)
        return {
            "model_prediction": model_pred,
            "baseline_prediction": baseline_pred,
            "coach_position": coach_position,
            "people_count": people_count
        }


crowd_model = CrowdPredictionModel()
