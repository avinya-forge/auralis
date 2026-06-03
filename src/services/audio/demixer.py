import os
import subprocess


class Demixer:
    """Demucs wrapper."""

    def __init__(self, model: str = "htdemucs", output_dir: str = "output/stems") -> None:
        self.model = model
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def separate(self, input_file: str) -> str:
        """Separate stems."""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        command = ["demucs", "-n", self.model, "-o", self.output_dir, input_file]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            if "out of memory" in e.stderr.lower():
                raise MemoryError("Demucs failed due to OOM")
            raise RuntimeError(f"Demucs execution error: {e.stderr}")
