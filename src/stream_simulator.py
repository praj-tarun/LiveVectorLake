import time
import subprocess
from pathlib import Path

SAMPLES_DIR = Path("data/samples")
INGEST_CLI = Path("src/cli.py")

def main():
    # Accept .txt files in data/samples and also in data/ (for flexibility)
    txt_files = sorted(list(SAMPLES_DIR.glob("*.txt")) + list(Path("data").glob("*.txt")))
    if not txt_files:
        print(f"No .txt files found in {SAMPLES_DIR} or data/. Please add sample documents.")
        return

    print(f"Streaming {len(txt_files)} documents from {SAMPLES_DIR} and data/ ...")
    for i, file in enumerate(txt_files, 1):
        print(f"[{i}/{len(txt_files)}] Ingesting: {file}")
        # Call your CLI ingest command
        result = subprocess.run(
            ["python", str(INGEST_CLI), "ingest", str(file)],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Error:", result.stderr)
        time.sleep(2)  # Simulate streaming delay

    print("Streaming complete.")

if __name__ == "__main__":
    main()
