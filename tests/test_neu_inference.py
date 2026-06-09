import time


def test_inference_benchmark():
    start = time.time()
    time.sleep(0.05)
    end = time.time()
    assert (end - start) < 0.1, "Inference took too long"
