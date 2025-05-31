import os
import time
import subprocess
from contextlib import contextmanager


@contextmanager
def jupyter_lab_server(port=8889):
    """Context manager that starts jupyter-lab and automatically stops it"""
    curr_file_dir = os.path.dirname(os.path.abspath(__file__))
    chinook_db_folder = os.path.join(curr_file_dir, "chinook_exports")

    jupyter_command = [
        "jupyter-lab",
        "--port",
        str(port),
        "--no-browser",
        "--NotebookApp.token=''",
        "--NotebookApp.password=''",
    ]

    process = None
    try:
        print(f"Starting jupyter-lab on port {port}...")
        process = subprocess.Popen(
            jupyter_command,
            cwd=chinook_db_folder,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Give it time to start
        time.sleep(5)

        url = f"http://127.0.0.1:{port}"
        print(f"Jupyter-lab started (PID: {process.pid}) at {url}")

        yield url

    finally:
        # This cleanup happens automatically when exiting the context
        if process and process.poll() is None:
            print(f"Stopping jupyter-lab process (PID: {process.pid})")
            process.terminate()
            try:
                process.wait(timeout=5)
                print("Jupyter-lab stopped successfully")
            except subprocess.TimeoutExpired:
                print("Force killing jupyter-lab process")
                process.kill()
                process.wait()
