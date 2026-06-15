from unittest.mock import PropertyMock, patch


from src.services.ai.inference_engine import NeuralInferenceEngine


def test_neural_inference_benchmark(benchmark):
    """
    Performance benchmark for NeuralInferenceEngine classifiers.
    """
    engine = NeuralInferenceEngine()

    # Enable simulation mode for benchmarking to isolate engine overhead
    with patch(
        "src.services.ai.config.AIConfig.simulation_mode", new_callable=PropertyMock
    ) as mock_sim:
        mock_sim.return_value = True

        def run_mock_inference():
            return engine.run_classification(
                file_path="mock_audio.wav", model_name="mock_model", task="audio-classification"
            )

        # Benchmark the execution
        result = benchmark(run_mock_inference)

        assert len(result) > 0
        assert result[0]["label"] == "simulation"
