"""Inference: load model, score transactions, return anomaly scores."""
from pipeline.inference.predictor import load_predictor, predict

__all__ = ["load_predictor", "predict"]
