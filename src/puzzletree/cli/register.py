"""Command registration module for dynamically discovering and registering CLI commands."""

import importlib
from pathlib import Path

from typer import Typer

from puzzletree.utils.logging import get_logger_console


def _register_commands(app: Typer, path: Path | None = None) -> None:
    """Dynamically discover and register CLI commands from submodules in the commands directory.

    Scans all subdirectories in the commands directory and registers any that have an 'app'
    attribute defined in their __init__.py file.
    """
    logger, _ = get_logger_console()

    # Get the cli directory path
    cli_dir = Path(__file__).parent / "commands" if path is None else path

    # Find all subdirectories in the commands directory that have __init__.py
    command_modules = [
        d.name for d in cli_dir.iterdir() if d.is_dir() and (d / "__init__.py").exists() and d.name != "__pycache__"
    ]

    registered_commands = set()

    # Import and register commands from each submodule
    for module_name in command_modules:
        logger.debug(f"Importing submodule: {module_name}")

        try:
            # Dynamically import the submodule (its __init__.py will be loaded)
            module = importlib.import_module(f"puzzletree.cli.commands.{module_name}")

            # Check if the module has an 'app' attribute
            if not hasattr(module, "app"):
                logger.debug(f"Submodule '{module_name}' does not have an 'app' attribute. Skipping.")

                continue

            # Get the app from the module
            sub_command = module.app

            if module_name in registered_commands:
                logger.warning(
                    f"Duplicate command name '{module_name}' found in submodule '{module_name}'. Skipping registration.",
                )
                continue

            app.add_typer(sub_command, name=module_name)
            registered_commands.add(module_name)
            logger.debug(f"Registered command '{module_name}' from submodule '{module_name}'")

        except ImportError as e:
            logger.warning(f"Failed to import submodule '{module_name}': {e}. Skipping.")
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning(f"Error processing submodule '{module_name}': {e}. Skipping.")
