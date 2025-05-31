"""
Simple try of the agent.

@dev You need to add AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT to your environment variables.
"""

import os
import sys
import logging
import argparse
import time
import asyncio
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from browser_use import Agent, Controller
from whisper_request_utils import get_latest_user_request
from context_utils import get_context_for_agent
from jupyter_loader import jupyter_lab_server

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
        max_failures=3,
    )
    logger.debug("Agent initialized successfully")
    return agent


def get_next_user_request(args, processed_requests: set):
    if args.telegram_whisper:
        while True:
            print("waiting for user's request from telegram bot...")
            latest_request = get_latest_user_request()
            # Add error handling for None response
            if latest_request is None:
                print(
                    "Failed to get request from telegram bot, retrying in 5 seconds..."
                )
                time.sleep(5)
                continue
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
        # Add error handling for the initial request
        initial_request = get_latest_user_request()
        if initial_request is not None:
            processed_requests.add(initial_request["id"])
        else:
            logger.warning("Could not get initial request from telegram bot")

    task_preprompt = get_context_for_agent(jupyter_lab_url, jupyter_lab_extension)

    # Initial task to open the notebook page
    initial_task = task_preprompt + "\n\nOpen the notebook page."
    agent = get_agent(initial_task)
    await browser_use_query_and_get_history(agent)
    print("task_preprompt: ", task_preprompt)

    while True:
        current_task = get_next_user_request(args, processed_requests)
        # Create a new agent for each user task
        full_task = task_preprompt + "\n\n" + current_task
        agent = get_agent(full_task)
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
