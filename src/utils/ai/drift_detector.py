import logging
from typing import Dict, Union

import numpy as np

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Implements a basic KL-divergence tracker to detect model drift
    in prediction distributions.
    """

    def __init__(self, kl_threshold: float = 0.5):
        self.kl_threshold = kl_threshold
        self.reference_distribution: Dict[str, float] = {}

    def set_reference_distribution(self, distribution: Dict[str, float]) -> None:
        """Sets the baseline distribution of classes."""
        # Normalize just in case
        total = sum(distribution.values())
        if total > 0:
            self.reference_distribution = {k: v / total for k, v in distribution.items()}
        else:
            logger.warning("Attempted to set an empty reference distribution.")
            self.reference_distribution = {}

    def analyze_drift(
        self, current_distribution: Dict[str, float]
    ) -> Dict[str, Union[bool, float]]:
        """
        Calculates KL divergence between current and reference distributions.
        Returns a dictionary with drift detected boolean and the KL score.
        """
        if not self.reference_distribution:
            logger.warning("No reference distribution set. Cannot analyze drift.")
            return {"drift_detected": False, "kl_divergence": 0.0}

        # Align keys
        all_keys = set(self.reference_distribution.keys()).union(set(current_distribution.keys()))

        # Normalize current
        total_curr = sum(current_distribution.values())
        if total_curr == 0:
            logger.error("Current distribution is empty.")
            return {"drift_detected": False, "kl_divergence": 0.0}

        ref_probs = []
        curr_probs = []
        epsilon = 1e-10  # Prevent log(0)

        for key in all_keys:
            ref_val = self.reference_distribution.get(key, 0.0) + epsilon
            curr_val = (current_distribution.get(key, 0.0) / total_curr) + epsilon
            ref_probs.append(ref_val)
            curr_probs.append(curr_val)

        ref_probs_arr = np.array(ref_probs)
        curr_probs_arr = np.array(curr_probs)

        # KL Divergence: sum(P(x) * log(P(x)/Q(x)))
        # Here we assume current (P) diverging from reference (Q)
        kl_div = np.sum(curr_probs_arr * np.log(curr_probs_arr / ref_probs_arr))

        is_drifting = bool(kl_div > self.kl_threshold)

        if is_drifting:
            logger.warning(
                f"Model drift detected! KL Divergence: {kl_div:.4f} > {self.kl_threshold}"
            )

        return {"drift_detected": is_drifting, "kl_divergence": float(kl_div)}
