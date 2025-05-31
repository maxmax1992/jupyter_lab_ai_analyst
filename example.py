"""
Simple try of the agent.

@dev You need to add AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT to your environment variables.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv
import subprocess
import time
from contextlib import contextmanager
import asyncio
from langchain_openai import AzureChatOpenAI
from browser_use import Agent, Controller
from browser_use.browser.session import BrowserSession

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
        time.sleep(3)

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


# Set up argument parsing
def setup_args():
    parser = argparse.ArgumentParser(
        description="Browser automation agent for data analysis"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (default: INFO level)",
    )
    return parser.parse_args()


# Set up logging
def setup_logging(debug=False):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


# Parse arguments and setup logging
args = setup_args()
logger = setup_logging(args.debug)

controller = Controller()

# Retrieve Azure-specific environment variables
load_dotenv()
azure_openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
azure_openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

logger.info("Starting browser automation agent")
logger.debug(f"Azure endpoint configured: {azure_openai_endpoint is not None}")

# Create a persistent browser session that stays alive
browser_session = BrowserSession(
    keep_alive=True,  # This keeps the browser alive after the agent finishes
    headless=False,  # Set to True if you want it headless
)


async def browser_use_query_and_get_history(agent: Agent):
    logger.debug("Starting agent execution with max_steps=1000")
    history = await agent.run(max_steps=1000)
    logger.info("Agent execution completed successfully")
    logger.info("Browser will remain open due to keep_alive=True")
    return history


def get_agent(task: str):
    logger.debug("Initializing Azure OpenAI client and agent")
    # Initialize the Azure OpenAI client
    model_name = "gpt-4.1"
    deployment = "gpt-4.1"

    llm = AzureChatOpenAI(
        model_name=model_name,
        openai_api_key=azure_openai_api_key,
        azure_endpoint=azure_openai_endpoint,
        deployment_name=deployment,
        api_version="2024-12-01-preview",
    )
    agent = Agent(
        task=task,
        llm=llm,
        controller=controller,
        browser_session=browser_session,
        max_failures=10000,
    )
    logger.debug("Agent initialized successfully")
    return agent


async def perform_tasks_in_jupyter_lab(
    jupyter_lab_url: str = "",
    jupyter_lab_extension: str = "/lab/workspaces/auto-Z/tree/demo_notebook-Copy1.ipynb",
):
    logger.info(
        f"Starting browser automation task in jupyter-lab instance at {jupyter_lab_url}"
    )

    jlab_controls = """
    COMMAND MODE commands:
    m - change cell type to markdown
    b - create cell below (of code type)
    a - create cell above (of code type)
    j - navigate to the cell below
    k - navigate to the cell above
    d, d - delete the current cell
    EDIT MODE:
    - allows editing the cell content
    Following keys work regardless of the mode:
    ctrl + enter - run the current cell
    cmd + s - save the current cell
    """

    jlab_usage_instructions = """
    Jupyter-lab cells are arranged in a sequence horizontally, first cell is at the top and last cell is at the bottom, you might need to navigate with scroll down or up to see the cell you'd like to edit. The notebook consists of cells that can run normal python in the sequence you ran them, so for example you can use first cells to define variables and functions, then another cells to perform high-level calls.
    There a 2 modes: edit and command mode, to switch to command mode press esc, to switch to edit mode click inside the area of the cell you'd like to edit. If you'd like to create addittional cell you can use the command mode and create a new cell with b (below) or a (above) keys.
    Current mode is shown in the bottom footer of the juypyter-lab instance page. Everytime you generate plot or table you need to save the cell and navigate down to see the output of the cell. You might delete all cells, but the last cell is always there and you can't delete it is expected. Currently selected cell is highlighed with a blue ribbon on the left to it and a blue border around it.
    """

    task_preprompt = f"""
    Your task is to use browser in jupyter-lab instance running in {jupyter_lab_url}{jupyter_lab_extension},

    Juptyer-lab usage instructions: {jlab_usage_instructions}

    Jupyter-lab controls: {jlab_controls}

    Also you have a helper delete cell and run cell buttons next to each of the cells.
    do a following tasks and try to use the keys and commands as much as possible, everytime you're done with the edition of the cell save the task:
    """
    print("task_preprompt: ", task_preprompt)
    agent = get_agent(task_preprompt)
    while True:
        current_task = input("Give me a new task:\n")
        agent.add_new_task(current_task)
        history = await browser_use_query_and_get_history(agent)
        print("final result: ", history.final_result())
        print("---------------------------")


if __name__ == "__main__":
    logger.info("Script execution started")

    task_context = """I've load chinook database exports previously into this folder where the notebook is. The current link to notebook instance contains following files:
    album_sample.csv       demo_notebook.ipynb (this notebook)   invoiceline_sample.csv
    artist_sample.csv      genre_sample.csv       mediatype_sample.csv
    customer_sample.csv    invoice_sample.csv     track_sample.csv
    """

    task_specific = """

    Which music genres have the longest average track duration?

    Save the code after the execution.
    """

    task = task_context + task_specific

    logger.debug("Executing main task")

    # Use context manager (automatically cleans up when done)
    with jupyter_lab_server() as url:
        print("url: ", url)
        # Your agent code here - uncomment when ready to run
        asyncio.run(perform_tasks_in_jupyter_lab(jupyter_lab_url=url))
        # print(result)
        time.sleep(10000000)

    print("Jupyter-lab has been automatically stopped.")
