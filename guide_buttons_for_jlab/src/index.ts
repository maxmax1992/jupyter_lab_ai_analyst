import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { NotebookActions, INotebookTracker } from '@jupyterlab/notebook';
import { Cell } from '@jupyterlab/cells';

const extension: JupyterFrontEndPlugin<void> = {
  id: 'custom-buttons',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker) => {
    console.log('🚀 JupyterLab extension custom-buttons is activated!');

    // Function to create cell action buttons
    const createCellActions = (cell: Cell, notebookPanel: any) => {
      try {
        console.log('🔧 Creating cell actions for cell:', cell);
        console.log('🔧 Notebook panel structure:', { notebookPanel, sessionContext: notebookPanel?.sessionContext });

        // Check if buttons already exist to avoid duplicates
        if (cell.node.querySelector('.cell-actions')) {
          console.log('⚠️ Cell actions already exist, skipping');
          return;
        }

        // Create container for action buttons
        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'cell-actions';
        actionsContainer.style.cssText = `
          position: absolute;
          top: 10px;
          left: 10px;
          display: flex;
          gap: 8px;
          z-index: 1000;
          opacity: 0.8;
          transition: opacity 0.2s;
          background: rgba(255, 255, 255, 0.9);
          border-radius: 4px;
          padding: 6px;
        `;

        // Create delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.innerHTML = 'DELETE THIS CELL';
        deleteBtn.title = 'Delete Cell';
        deleteBtn.style.cssText = `
          background: #ff4757;
          color: white;
          border: none;
          border-radius: 3px;
          padding: 6px 12px;
          cursor: pointer;
          font-size: 12px;
          font-weight: 500;
          line-height: 1;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        `;
        deleteBtn.onclick = (e) => {
          e.stopPropagation();
          console.log('🗑️ Delete button clicked');
          try {
            // Find the cell index and delete it
            const notebookContent = notebookPanel.content;
            const widgets = notebookContent.widgets;
            const cellIndex = widgets.findIndex((widget: any) => widget === cell);
            console.log('Cell index:', cellIndex);
            if (cellIndex !== -1) {
              notebookContent.activeCellIndex = cellIndex;
              NotebookActions.deleteCells(notebookContent);
            }
          } catch (error) {
            console.error('Error deleting cell:', error);
          }
        };

        // Create run button
        const runBtn = document.createElement('button');
        runBtn.innerHTML = 'RUN THIS CELL';
        runBtn.title = 'Run Cell';
        runBtn.style.cssText = `
          background: #2ed573;
          color: white;
          border: none;
          border-radius: 3px;
          padding: 6px 12px;
          cursor: pointer;
          font-size: 12px;
          font-weight: 500;
          line-height: 1;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        `;
        runBtn.onclick = (e) => {
          e.stopPropagation();
          console.log('▶️ Run button clicked');
          try {
            // Find the cell index and run it
            const notebookContent = notebookPanel.content;
            const widgets = notebookContent.widgets;
            const cellIndex = widgets.findIndex((widget: any) => widget === cell);
            console.log('Cell index:', cellIndex);
            console.log('SessionContext available:', !!notebookPanel.sessionContext);
            if (cellIndex !== -1) {
              // Set the active cell
              notebookContent.activeCellIndex = cellIndex;
              // Run the cell and advance (like Shift+Enter) with proper session context from notebook panel
              const sessionContext = notebookPanel.sessionContext;
              if (sessionContext) {
                NotebookActions.runAndAdvance(notebookContent, sessionContext);
              } else {
                console.error('No session context found on notebook panel');
              }
            }
          } catch (error) {
            console.error('Error running cell:', error);
          }
        };

        actionsContainer.appendChild(deleteBtn);
        actionsContainer.appendChild(runBtn);

        // Set cell positioning for buttons
        cell.node.style.position = 'relative';

        // Add padding to cell content to make space for buttons
        const cellContent = cell.node.querySelector('.jp-Cell-inputWrapper') ||
          cell.node.querySelector('.jp-InputArea') ||
          cell.node.querySelector('.jp-Cell-outputWrapper');
        if (cellContent) {
          (cellContent as HTMLElement).style.paddingTop = '50px';
        }

        // Find the output area and add padding for the buttons
        const outputWrapper = cell.node.querySelector('.jp-Cell-outputWrapper') ||
          cell.node.querySelector('.jp-OutputArea');
        if (outputWrapper) {
          (outputWrapper as HTMLElement).style.position = 'relative';
          (outputWrapper as HTMLElement).style.paddingTop = '50px';
        }

        // Also ensure the actual output content has padding
        const outputArea = cell.node.querySelector('.jp-OutputArea-output') ||
          cell.node.querySelector('.jp-OutputArea-child');
        if (outputArea) {
          (outputArea as HTMLElement).style.paddingTop = '20px';
        }

        // Add padding to any existing output prompts
        const outputPrompts = cell.node.querySelectorAll('.jp-OutputArea-prompt');
        outputPrompts.forEach(prompt => {
          (prompt as HTMLElement).style.paddingTop = '50px';
        });

        // Ensure the cell has proper spacing for overlays
        const cellNode = cell.node as HTMLElement;
        cellNode.style.minHeight = '60px'; // Ensure minimum height for overlays

        // Add hover effects for action containers
        cell.node.addEventListener('mouseenter', () => {
          actionsContainer.style.opacity = '1';
        });
        cell.node.addEventListener('mouseleave', () => {
          actionsContainer.style.opacity = '0.8';
        });

        // Append the action buttons to the cell
        cell.node.appendChild(actionsContainer);
        console.log('✅ Successfully added cell actions to cell');

      } catch (error) {
        console.error('❌ Error creating cell actions:', error);
      }
    };

    // Function to add buttons to all existing cells
    const addButtonsToAllCells = (notebookPanel: any) => {
      try {
        const widgets = notebookPanel.content.widgets;
        console.log('📝 Adding buttons to all cells, cell count:', widgets?.length || 0);
        console.log('📝 Notebook panel structure:', { notebookPanel, content: notebookPanel.content, widgets });

        if (!widgets) {
          console.error('❌ No widgets found in notebook');
          return;
        }

        widgets.forEach((cell: Cell, index: number) => {
          console.log(`Processing cell ${index}:`, cell);
          createCellActions(cell, notebookPanel);
        });

      } catch (error) {
        console.error('❌ Error adding buttons to all cells:', error);
      }
    };

    // When a notebook is added to the tracker
    tracker.widgetAdded.connect((sender, notebookPanel) => {
      console.log('📓 New notebook added:', notebookPanel);

      // Add buttons to existing cells with a small delay
      setTimeout(() => {
        addButtonsToAllCells(notebookPanel);
      }, 500);

      // Listen for new cells being added
      if (notebookPanel.content.model) {
        notebookPanel.content.model.cells.changed.connect(() => {
          console.log('🔄 Cells changed, re-adding buttons');
          setTimeout(() => {
            addButtonsToAllCells(notebookPanel);
          }, 100);
        });
      }
    });

    // Handle already open notebooks
    console.log('🔍 Checking for existing notebooks, count:', tracker.size);
    tracker.forEach(notebookPanel => {
      console.log('📖 Processing existing notebook:', notebookPanel);
      setTimeout(() => {
        addButtonsToAllCells(notebookPanel);
      }, 500);

      if (notebookPanel.content.model) {
        notebookPanel.content.model.cells.changed.connect(() => {
          console.log('🔄 Existing notebook cells changed, re-adding buttons');
          setTimeout(() => {
            addButtonsToAllCells(notebookPanel);
          }, 100);
        });
      }
    });
  },
};

export default extension;