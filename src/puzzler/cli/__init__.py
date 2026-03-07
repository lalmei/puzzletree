"""fun CLI Application Module.

----------------

This module initializes the CLI for the `puzzler` package using the Typer library.
It serves as the entry point for Puzzle reconstruction experiments and CLI tooling.

Each command is defined in its respective module and registered via Typer to allow
for a modular and extendable CLI application.

Once installed, the `pyproject.toml` defines the entry point as

``` py  title="pyproject.toml"
[project.scripts]
puzzler = "puzzler:app"
```

since in the puzzler `src/puzzler/__init__.py` we have the following import

```python title="puzzler/__init__.py"
from puzzler.cli.cli import app
```

Once installed this allows you to run the CLI directly from the command line using:
```bash
puzzler [COMMAND] [OPTIONS]
```
or

```bash
uv run python -m puzzler.cli [COMMAND] [OPTIONS]
```

This module is designed to be run as a script, and it will automatically
load the appropriate subcommands based on the environment and configuration.
It also provides a help message when no command is specified.


Example:
    python -m puzzler.command.cli train --config config.yaml

Dependencies:
    - Typer: A modern library for building CLI applications, based on Click.
    - Pydantic: For data validation and settings management.
    - Rich: For rich text and beautiful formatting in the terminal.
    - Pydantic-settings: For settings management with Pydantic.

Each subcommand is defined in its own module and registered automatically via dynamic discovery.

**Adding New Commands:**

To add a new CLI command, create a new Python module in the `puzzler/cli/` directory and define a function with a `.command` attribute:

```python
from typer import Context

def my_command(ctx: Context, ...):
    \"\"\"My command description.\"\"\"
    ...

# Mark this function as a CLI command
my_command.command = "my-command"
```

The command will be automatically discovered and registered when the CLI application starts. No manual registration is required.

Subcommands can define a default behavior through the use of a @app.callback() function. This callback is invoked when the subcommand is used without specifying a sub-subcommand.

For example, in the dataset command, the @app.callback() handles dataset loading when no sub-subcommand (like list) is provided. This enables users to run puzzler dataset --name my_dataset directly, without needing to call a secondary command.

If we want to add sub-subcommands (such as list), we define them using the @app.command() decorator. In this case, the callback is still invoked before the sub-subcommand is executed unless invoke_without_command=True is used, allowing for flexible pre-processing or shared setup logic.

Commands:
    - Commands are automatically discovered from modules in the cli directory
"""

from puzzler.cli.main_cli import cli_app as cli

__all__: list[str] = ["cli", "debug_info", "get_version"]
