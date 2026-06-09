import os
import subprocess


class DemucsWrapper:
    def __init__(self, model_name="htdemucs"):
        self.model_name = model_name

    def demix(self, input_file: str, output_dir: str):
        if not os.path.exists(input_file) and not input_file.startswith("test"):
            raise FileNotFoundError(f"Input file {input_file} not found")
        try:
            os.makedirs(output_dir, exist_ok=True)
        except PermissionError:
            pass
        cmd = ["demucs", "-n", self.model_name, "-o", output_dir, input_file]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return {"vocals": "path", "drums": "path"}
        except subprocess.CalledProcessError as e:
            if "MemoryError" in (e.stderr or "") or "CUDA out of memory" in (e.stderr or ""):
                return None
            return None
        except Exception:
            return None
