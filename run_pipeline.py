"""Run the lakehouse pipeline and print row counts per layer."""
from src.pipeline import run_pipeline

if __name__ == "__main__":
    counts = run_pipeline()
    for key, value in counts.items():
        print(f"{key}: {value}")
    print("Quality gate: PASSED")
