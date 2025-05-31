import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { NotebookActions, INotebookTracker } from '@jupyterlab/notebook';
import { Cell } from '@jupyterlab/cells';

const extension: JupyterFrontEndPlugin<void> = {
  id: 'custom-buttons',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker) => {
    console.log('🚀 JupyterLab extension custom-buttons is activated!');

    // Function to update selection indicators for all cells
    const updateSelectionIndicators = (notebookPanel: any) => {
      try {
        const notebookContent = notebookPanel.content;
        const activeIndex = notebookContent.activeCellIndex;
        const widgets = notebookContent.widgets;

        widgets.forEach((cell: Cell, index: number) => {
          const indicator = cell.node.querySelector('.cell-selection-indicator') as HTMLElement;
          if (indicator) {
            if (index === activeIndex) {
              indicator.textContent = 'CURRENTLY SELECTED CELL => ';
              indicator.style.backgroundColor = '#e3f2fd';
              indicator.style.borderColor = '#2196f3';
              indicator.style.color = '#1565c0';
              indicator.style.fontWeight = 'bold';
            } else {
              indicator.textContent = '';
              indicator.style.backgroundColor = 'transparent';
              indicator.style.borderColor = 'transparent';
              indicator.style.color = '#666';
              indicator.style.fontWeight = 'normal';
            }
          }
        });
      } catch (error) {
        console.error('Error updating selection indicators:', error);
      }
    };

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

        // Create selection indicator container (positioned to the left)
        const selectionIndicator = document.createElement('div');
        selectionIndicator.className = 'cell-selection-indicator';
        selectionIndicator.style.cssText = `
          position: relative;
          float: left;
          width: 220px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: flex-end;
          z-index: 1000;
          font-size: 12px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          border: 1px solid transparent;
          border-radius: 4px;
          padding: 4px 8px;
          margin-right: 10px;
          margin-top: 10px;
          transition: all 0.2s ease;
          background: transparent;
          color: #666;
          font-weight: normal;
          box-sizing: border-box;
        `;

        // Create a wrapper for the selection indicator and cell content
        const cellWrapper = document.createElement('div');
        cellWrapper.className = 'cell-content-wrapper';
        cellWrapper.style.cssText = `
          display: flex;
          align-items: flex-start;
          width: 100%;
          min-height: 60px;
        `;

        // Create container for the main cell content
        const cellContentContainer = document.createElement('div');
        cellContentContainer.className = 'cell-main-content';
        cellContentContainer.style.cssText = `
          flex: 1;
          position: relative;
        `;

        // Move all existing cell content into the new container
        const cellChildren = Array.from(cell.node.children);
        cellChildren.forEach(child => {
          if (!child.classList.contains('cell-selection-indicator') &&
            !child.classList.contains('cell-content-wrapper')) {
            cellContentContainer.appendChild(child);
          }
        });

        // Make cell container use flexbox layout
        cell.node.style.position = 'relative';
        cell.node.style.display = 'flex';
        cell.node.style.alignItems = 'flex-start';

        // Add the selection indicator and content container to wrapper
        cellWrapper.appendChild(selectionIndicator);
        cellWrapper.appendChild(cellContentContainer);

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
              // Run the cell with proper session context from notebook panel
              const sessionContext = notebookPanel.sessionContext;
              if (sessionContext) {
                NotebookActions.run(notebookContent, sessionContext);
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

        // Add the action buttons to the cell content container
        cellContentContainer.appendChild(actionsContainer);

        // Add padding to cell content to make space for buttons
        const cellContent = cellContentContainer.querySelector('.jp-Cell-inputWrapper') ||
          cellContentContainer.querySelector('.jp-InputArea') ||
          cellContentContainer.querySelector('.jp-Cell-outputWrapper');
        if (cellContent) {
          (cellContent as HTMLElement).style.paddingTop = '50px';
        }

        // Find the output area and add padding for the description
        const outputWrapper = cellContentContainer.querySelector('.jp-Cell-outputWrapper') ||
          cellContentContainer.querySelector('.jp-OutputArea');
        if (outputWrapper) {
          (outputWrapper as HTMLElement).style.position = 'relative';
          (outputWrapper as HTMLElement).style.paddingTop = '50px';
        }

        // Also ensure the actual output content has padding
        const outputArea = cellContentContainer.querySelector('.jp-OutputArea-output') ||
          cellContentContainer.querySelector('.jp-OutputArea-child');
        if (outputArea) {
          (outputArea as HTMLElement).style.paddingTop = '20px';
        }

        // Add padding to any existing output prompts
        const outputPrompts = cellContentContainer.querySelectorAll('.jp-OutputArea-prompt');
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

        // Append the wrapper to the cell
        cell.node.appendChild(cellWrapper);
        console.log('✅ Successfully added cell actions to cell');

        // Update selection indicators after adding elements
        setTimeout(() => updateSelectionIndicators(notebookPanel), 50);

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

        // Update selection indicators after all cells are processed
        setTimeout(() => updateSelectionIndicators(notebookPanel), 100);
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

      // Listen for active cell changes
      notebookPanel.content.activeCellChanged.connect(() => {
        console.log('🎯 Active cell changed');
        updateSelectionIndicators(notebookPanel);
      });

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

      // Listen for active cell changes on existing notebooks
      notebookPanel.content.activeCellChanged.connect(() => {
        console.log('🎯 Active cell changed in existing notebook');
        updateSelectionIndicators(notebookPanel);
      });

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