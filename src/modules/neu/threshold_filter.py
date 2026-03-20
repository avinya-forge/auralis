from typing import Dict, List, Any
from src.modules.neu.ai_config import AIConfig

class ThresholdFilter:
    """
    Filters AI tags based on confidence scores defined in AIConfig.
    """
    def __init__(self, config: AIConfig = None):
        self.config = config if config is not None else AIConfig()

    def filter_tags(self, tags: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Drops tags where the confidence is strictly less than the threshold.
        If a tag lacks a 'confidence' key, it is kept.
        """
        threshold = self.config.confidence_threshold
        filtered = []

        for tag in tags:
            # If no confidence is present, we keep the tag by default
            if 'confidence' not in tag:
                filtered.append(tag)
            elif tag['confidence'] >= threshold:
                filtered.append(tag)

        return filtered
