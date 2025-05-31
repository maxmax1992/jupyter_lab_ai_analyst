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
from whisper_request_utils import get_latest_user_request
from context_utils import get_context_for_agent

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
    parser.add_argument(
        "--telegram_whisper",
        action="store_true",
        help="Enable telegram whisper (default: False)",
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
        max_failures=3,
    )
    logger.debug("Agent initialized successfully")
    return agent


def get_next_user_request(args, processed_requests: set):
    if args.telegram_whisper:
        while True:
            print("waiting for user's request from telegram bot...")
            latest_request = get_latest_user_request()
            if latest_request["id"] not in processed_requests:
                processed_requests.add(latest_request["id"])
                return latest_request["text"]
            time.sleep(1)
    else:
        return input("Enter your request: ")


async def perform_tasks_in_jupyter_lab(
    args,
    jupyter_lab_url: str = "",
    jupyter_lab_extension: str = "/lab/workspaces/auto-Z/tree/eda_notebook.ipynb",
):
    logger.info(
        f"Starting browser automation task in jupyter-lab instance at {jupyter_lab_url}"
    )

    processed_requests = set()
    if args.telegram_whisper:
        processed_requests.add(get_latest_user_request()["id"])

    task_preprompt = get_context_for_agent(jupyter_lab_url, jupyter_lab_extension)
    agent = get_agent(task_preprompt)
    agent.add_new_task("Open the notebook page.")
    await browser_use_query_and_get_history(agent)
    print("task_preprompt: ", task_preprompt)
    while True:
        current_task = get_next_user_request(args, processed_requests)
        agent.add_new_task(current_task)
        await browser_use_query_and_get_history(agent)


if __name__ == "__main__":
    logger.info("Script execution started")

    logger.debug("Executing main task")
    args = setup_args()

    # context manager for automatic cleanup of the jupyter-lab instance
    with jupyter_lab_server() as url:
        print("url: ", url)
        asyncio.run(perform_tasks_in_jupyter_lab(args, jupyter_lab_url=url))

    print("Jupyter-lab has been automatically stopped.")
