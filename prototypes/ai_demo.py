#!/usr/bin/env python3
"""
AI Prototype Demo Script for Auralis

This script demonstrates how to integrate Hugging Face models for:
1. Zero-shot Raga Classification (using CLAP)
2. General Music Tagging (Genre, Mood) (using CLAP)
3. Cover Song Identification (using MERT Embeddings)

Prerequisites:
    pip install torch transformers librosa numpy soundfile
"""

import sys

try:
    import librosa
    import numpy as np
    import torch
    from transformers import AutoModel, AutoProcessor, ClapModel, Wav2Vec2FeatureExtractor
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    print(f"Note: {e}. Running in simulation mode.")
    print("To run with actual models: pip install transformers torch librosa numpy soundfile")


class MusicAI:
    def __init__(self):
        self.clap_model = None
        self.clap_processor = None
        self.mert_model = None
        self.mert_processor = None

        if TRANSFORMERS_AVAILABLE:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {self.device}")
        else:
            self.device = "cpu"
            print("Running in simulation mode (no models loaded).")

    def load_clap(self):
        """Load CLAP model for Zero-Shot Classification"""
        if not TRANSFORMERS_AVAILABLE:
            return

        print("Loading CLAP model (laion/clap-htsat-unfused)...")
        try:
            self.clap_processor = AutoProcessor.from_pretrained("laion/clap-htsat-unfused")
            self.clap_model = ClapModel.from_pretrained("laion/clap-htsat-unfused").to(self.device)
            print("CLAP model loaded successfully.")
        except Exception as e:
            print(f"Failed to load CLAP: {e}")

    def load_mert(self):
        """Load MERT model for Music Embeddings"""
        if not TRANSFORMERS_AVAILABLE:
            return

        print("Loading MERT model (m-a-p/MERT-v1-95M)...")
        try:
            self.mert_processor = Wav2Vec2FeatureExtractor.from_pretrained("m-a-p/MERT-v1-95M", trust_remote_code=True)
            self.mert_model = AutoModel.from_pretrained("m-a-p/MERT-v1-95M", trust_remote_code=True).to(self.device)
            print("MERT model loaded successfully.")
        except Exception as e:
            print(f"Failed to load MERT: {e}")

    def classify_zero_shot(self, audio_path, candidate_labels):
        """
        Classify audio using Zero-Shot Learning (CLAP).
        Perfect for Raga identification or arbitrary tagging.
        """
        if not self.clap_model:
            print("CLAP model not loaded. Skipping classification.")
            return {}

        try:
            # Load and resample audio
            audio, sr = librosa.load(audio_path, sr=48000)  # CLAP expects 48kHz

            # Process inputs
            inputs = self.clap_processor(
                text=candidate_labels, audios=audio, return_tensors="pt", padding=True, sampling_rate=48000
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Run inference
            with torch.no_grad():
                outputs = self.clap_model(**inputs)

            # Calculate probabilities
            logits_per_audio = outputs.logits_per_audio  # [1, num_labels]
            probs = logits_per_audio.softmax(dim=1)  # [1, num_labels]

            # Format results
            results = {}
            for i, label in enumerate(candidate_labels):
                results[label] = probs[0][i].item()

            return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

        except Exception as e:
            print(f"Error classifying {audio_path}: {e}")
            return {}

    def get_embedding(self, audio_path):
        """
        Get semantic embedding vector for a song using MERT.
        Useful for Cover Song Identification (Cosine Similarity).
        """
        if not self.mert_model:
            print("MERT model not loaded. Skipping embedding.")
            return None

        try:
            # Load and resample audio
            audio, sr = librosa.load(audio_path, sr=24000)  # MERT expects 24kHz

            # Process inputs
            inputs = self.mert_processor(audio, sampling_rate=24000, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Run inference
            with torch.no_grad():
                outputs = self.mert_model(**inputs, output_hidden_states=True)

            # Aggregate hidden states (e.g., mean of last layer)
            all_layer_hidden_states = torch.stack(outputs.hidden_states).squeeze()
            last_hidden_state = all_layer_hidden_states[-1]  # [seq_len, hidden_dim]
            embedding = last_hidden_state.mean(dim=0).cpu().numpy()  # [hidden_dim]

            return embedding

        except Exception as e:
            print(f"Error getting embedding for {audio_path}: {e}")
            return None


def demo_raga_identification(ai, audio_path):
    print(f"\n--- Identifying Raga for {audio_path} ---")
    ragas = [
        "Indian Classical Raga Bhairav",
        "Indian Classical Raga Yaman",
        "Indian Classical Raga Todi",
        "Indian Classical Raga Darbari",
        "Bollywood Song",
        "Western Pop Music"
    ]
    results = ai.classify_zero_shot(audio_path, ragas)
    for label, score in results.items():
        print(f"{label}: {score:.4f}")


def demo_cover_song_identification(ai, original_path, cover_path):
    print(f"\n--- Comparing Cover Song: {cover_path} vs Original: {original_path} ---")
    emb_orig = ai.get_embedding(original_path)
    emb_cover = ai.get_embedding(cover_path)

    if emb_orig is not None and emb_cover is not None:
        # Cosine Similarity
        similarity = np.dot(emb_orig, emb_cover) / (np.linalg.norm(emb_orig) * np.linalg.norm(emb_cover))
        print(f"Semantic Similarity Score: {similarity:.4f}")
        if similarity > 0.85:
            print("Result: Likely a Cover (High Similarity)")
        else:
            print("Result: Likely Different Song (Low Similarity)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_demo.py <audio_file> [optional: <second_audio_file>]")
        # Creating dummy run for demonstration
        ai = MusicAI()
        # Mocking model loads if transformers missing
        if not TRANSFORMERS_AVAILABLE:
            print("\n[Simulation Mode] Transformers not installed.")
            print("This would output:\n")
            print("--- Identifying Raga for song.mp3 ---")
            print("Indian Classical Raga Bhairav: 0.85")
            print("Indian Classical Raga Yaman: 0.10")
            print("...")
            print("\n--- Comparing Cover Song ---")
            print("Semantic Similarity Score: 0.92")
            print("Result: Likely a Cover")
        sys.exit(0)

    audio_file = sys.argv[1]

    ai = MusicAI()
    ai.load_clap()
    ai.load_mert()

    # Demo 1: Raga ID
    demo_raga_identification(ai, audio_file)

    # Demo 2: Cover Song (if second file provided)
    if len(sys.argv) > 2:
        second_file = sys.argv[2]
        demo_cover_song_identification(ai, audio_file, second_file)
