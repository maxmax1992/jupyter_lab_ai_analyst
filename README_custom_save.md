# Teaching Browser-Use to Save with cmd+s After Editing Cells

This guide shows how to extend browser_use with custom functions and lifecycle hooks to automatically save pages after editing cells using keyboard shortcuts.

## Overview

Browser-use allows you to add custom functions and hooks in two main ways:

1. **Custom Functions** - Extend the agent's capabilities with new actions
2. **Lifecycle Hooks** - Add callbacks that trigger at specific points in the agent's execution

## Custom Functions

### Adding a Simple Save Function

```python
from browser_use import Controller, BrowserContext
from browser_use.agent.views import ActionResult
from pydantic import BaseModel

class SavePageAction(BaseModel):
    """Save the page with cmd+s"""
    pass

def create_custom_controller():
    controller = Controller()

    @controller.registry.action(
        'Save the current page using cmd+s keyboard shortcut',
        param_model=SavePageAction
    )
    async def save_page(params: SavePageAction, browser: BrowserContext):
        page = await browser.get_current_page()
        await page.keyboard.press("Meta+s")  # cmd+s on Mac
        await asyncio.sleep(1)  # Wait for save
        return ActionResult(extracted_content="💾 Saved page with cmd+s", include_in_memory=True)

    return controller
```

### Adding Combined Edit + Save Function

```python
class EditAndSaveAction(BaseModel):
    """Edit a cell and save with cmd+s"""
    index: int = Field(description="Index of the element to edit")
    text: str = Field(description="Text to input")

@controller.registry.action(
    'Edit a cell/element and automatically save with cmd+s',
    param_model=EditAndSaveAction
)
async def edit_and_save(params: EditAndSaveAction, browser: BrowserContext):
    page = await browser.get_current_page()

    # Edit the element
    element_node = await browser.get_dom_element_by_index(params.index)
    await browser._input_text_element_node(element_node, params.text)

    # Save with cmd+s
    await asyncio.sleep(0.5)  # Small delay
    await page.keyboard.press("Meta+s")
    await asyncio.sleep(1)  # Wait for save

    msg = f"⌨️ Edited element {params.index} with '{params.text}' and saved with cmd+s 💾"
    return ActionResult(extracted_content=msg, include_in_memory=True)
```

## Lifecycle Hooks

Hooks allow you to add custom behavior at specific points in the agent's execution:

```python
class AgentHooks:
    def __init__(self):
        self.step_count = 0
        self.save_count = 0

    async def on_new_step(self, state: BrowserState, output: AgentOutput, step_number: int) -> None:
        """Called after each agent step"""
        self.step_count += 1
        print(f"🔄 Hook: Step {step_number} completed")

        # Check if this step involved saving
        for action in output.action:
            action_dict = action.model_dump()
            if any(key in ['save_page', 'edit_and_save'] for key in action_dict.keys() if action_dict[key] is not None):
                self.save_count += 1
                print(f"💾 Hook: Save action detected! Total saves: {self.save_count}")

    async def on_agent_done(self, history: AgentHistoryList) -> None:
        """Called when agent completes all tasks"""
        print(f"✅ Hook: Agent completed! Steps: {self.step_count}, Saves: {self.save_count}")
```

## Using Custom Functions and Hooks

```python
from browser_use import Agent

# Create hooks
hooks = AgentHooks()

# Create agent with custom controller and hooks
agent = Agent(
    task="Your task here",
    llm=your_llm,
    controller=create_custom_controller(),  # Custom controller with save functions
    register_new_step_callback=hooks.on_new_step,  # Step hook
    register_done_callback=hooks.on_agent_done,    # Completion hook
    use_vision=True,
)

# Run the agent
result = await agent.run(max_steps=10)
```

## Complete Examples

### Simple Example (`simple_save_example.py`)

A minimal example showing how to add save functionality:

```bash
python simple_save_example.py
```

### Advanced Example (`custom_save_example.py`)

A comprehensive example with multiple custom functions and hooks:

```bash
python custom_save_example.py
```

## Key Concepts

### 1. Custom Actions Registry

- Use `@controller.registry.action()` decorator to register new functions
- Provide a description and parameter model (Pydantic)
- Functions must return `ActionResult` objects
- Access browser through the `browser: BrowserContext` parameter

### 2. Parameter Models

Define what parameters your custom functions accept:

```python
class MyCustomAction(BaseModel):
    param1: str = Field(description="Description of parameter")
    param2: int = Field(default=5, description="Optional parameter with default")
```

### 3. Keyboard Shortcuts

Use Playwright's keyboard API:

- `Meta+s` for cmd+s on Mac
- `Control+s` for ctrl+s on Windows/Linux
- `page.keyboard.press("Enter")` for single keys
- `page.keyboard.press("Shift+Tab")` for combinations

### 4. Lifecycle Hooks

Available hooks:

- `register_new_step_callback` - Called after each step
- `register_done_callback` - Called when agent completes
- `register_external_agent_status_raise_error_callback` - For external control

## Best Practices

1. **Add delays** after keyboard actions to ensure they're processed
2. **Check element existence** before interacting with them
3. **Use descriptive action names** and parameter descriptions
4. **Include meaningful feedback** in ActionResult messages
5. **Handle errors gracefully** with try/catch blocks

## Practical Use Cases

- **Jupyter Notebooks**: Save after editing code cells
- **Google Sheets**: Auto-save after data entry
- **Google Docs**: Save after text edits
- **Forms**: Save drafts periodically
- **Code Editors**: Auto-save functionality

This approach gives you fine-grained control over when and how your browser_use agent saves work, making it perfect for scenarios where you need to ensure data persistence after making edits.
