"""
Simple try of the agent.

@dev You need to add AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT to your environment variables.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from langchain_openai import AzureChatOpenAI
from browser_use import Agent, Controller
import pyautogui


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


async def browser_use_query_and_get_result(agent):
    logger.debug("Starting agent execution with max_steps=10")
    response = await agent.run(max_steps=10)
    final_result = response.final_result()
    logger.info("Agent execution completed successfully")
    return final_result


def get_agent(task: str):
    logger.debug("Initializing Azure OpenAI client and agent")
    # Initialize the Azure OpenAI client
    llm = AzureChatOpenAI(
        model_name="gpt-4.1",
        openai_api_key=azure_openai_api_key,
        azure_endpoint=azure_openai_endpoint,  # Corrected to use azure_endpoint instead of openai_api_base
        deployment_name="gpt-4.1",  # Use deployment_name for Azure models
        api_version="2024-12-01-preview",  # Explicitly set the API version here
    )
    agent = Agent(task=task, llm=llm, controller=controller)
    logger.debug("Agent initialized successfully")
    return agent


@controller.action("save notebook")
def save_notebook():
    logger.info("Executing save notebook action")
    print("SAVING THE NOTEBOOK")
    pyautogui.press("esc")
    time.sleep(0.5)
    pyautogui.hotkey("command", "s")
    logger.debug("Save notebook action completed")


@controller.action("save cell")
def save_cell_after_editing():
    logger.info("Executing save cell action")
    # TODO
    print("SAVING THE CELL")
    time.sleep(0.1)
    pyautogui.hotkey("command", "s")
    logger.debug("Save cell action completed")


@controller.action("delete current selected cell")
def delete_current_selected_cell():
    logger.info("Executing delete current selected cell action")
    print("TRYING TO DELETE THE CELL")
    pyautogui.press("esc")
    time.sleep(0.5)
    pyautogui.press("d")
    time.sleep(0.1)
    pyautogui.press("d")
    time.sleep(5)  # optional wait between repeats
    logger.debug("Delete cell action completed")


# Make this function async
async def browse_based_on_query(
    task="",
):
    logger.info(f"Starting browser automation task")
    logger.debug(f"Task details: {task[:100]}...")  # Log first 100 chars of task

    task_preprompt = """
    You're a professional data scientist, your task is to use browser in jupyter-lab instance running in http://maxims-macbook-pro.local:8888/lab/tree/demo_notebook.ipynb do a following tasks:
    """
    task_preprompt += task
    agent = get_agent(task_preprompt)
    # Call the async helper
    response = await browser_use_query_and_get_result(agent)
    logger.info("Browser automation task completed")
    return response


# 1. "Which music genres have the longest average track duration?"
# 2. "What's the relationship between track file size and pricing?"
# 3. "Which artists have the most diverse portfolio in terms of genres?"
# 4. "Are there any pricing patterns by composer? Do certain composers command premium pricing?"

# Sales & Revenue Analysis:
# 5. "Which countries generate the highest revenue per customer?"
# 6. "What's the seasonal pattern of music purchases?"
# 7. "Do customers from certain countries prefer specific genres?"
# 8. "What's the average order size (number of tracks) per invoice?"

# Customer Segmentation:
# 9. "Which companies have the most music-buying employees?"
# 10. "Is there a geographic concentration of high-value customers?"
# 11. "Do customers with corporate email addresses spend differently than personal email users?"
# 12. "Which cities have the most active music buyers?"

# Product & Inventory Insights:
# 13. "What percentage of tracks are missing composer information, and does this correlate with sales performance?"
# 14. "Which media types (MP3, AAC, etc.) are most popular by region?"
# 15. "Are there 'orphaned' albums (albums with very few track sales)?"
# 16. "What's the typical album size (number of tracks) across different genres?"

# Advanced Business Intelligence:
# 17. "Can we identify 'whale' customers - those who contribute disproportionately to revenue?"
# 18. "Which customer support representatives manage the highest-value customer portfolios?"
# 19. "Are there any price optimization opportunities - tracks that sell well despite being underpriced?"
# 20. "What's the customer acquisition pattern over time?"
if __name__ == "__main__":
    logger.info("Script execution started")

    # Simpler main execution without explicit agent close attempt

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
    # debug:
    # task = "Call the save_notebook_after_editing tool, to validate it works"
    task = "Create a new cell and write 'hello world', afterwards delete it by using delete_current_selected_cell tool"

    logger.debug("Executing main task")
    result = asyncio.run(browse_based_on_query(task=task))
    print(result)
    logger.info("Script execution completed")
