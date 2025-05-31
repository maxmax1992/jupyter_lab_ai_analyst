def get_context_for_agent(jupyter_lab_url: str, jupyter_lab_extension: str):
    task_context = """context for you to act in the chrome-browser: I've load chinook database exports previously into this folder where the notebook is. The current link to notebook instance contains following files:
    album_sample.csv       eda_notebook.ipynb (this notebook)   invoiceline_sample.csv
    artist_sample.csv      genre_sample.csv       mediatype_sample.csv
    customer_sample.csv    invoice_sample.csv     track_sample.csv
    """

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
    {task_context}

    Your task is to use browser in jupyter-lab instance running in {jupyter_lab_url}{jupyter_lab_extension},

    Juptyer-lab usage instructions: {jlab_usage_instructions}

    Jupyter-lab controls: {jlab_controls}

    Also you have a helper delete cell and run cell buttons next to each of the cells.
    do a following tasks and try to use the keys and commands as much as possible, everytime you're done with the edition/running of the cell save the notebook:
    """
    return task_preprompt
