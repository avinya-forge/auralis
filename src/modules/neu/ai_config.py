from dataclasses import dataclass


@dataclass
class AIConfig:
    """
    Singleton dataclass holding AI configuration parameters.
    """

    confidence_threshold: float = 0.65

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AIConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self, confidence_threshold: float = 0.65):
        # Prevent re-initialization if already instantiated
        if not hasattr(self, "_initialized"):
            self.confidence_threshold = confidence_threshold
            self._initialized = True
