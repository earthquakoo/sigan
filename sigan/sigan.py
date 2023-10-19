import typer

import sys
sys.path.append('.')

import sigan.utils.general_utils as general_utils
import sigan.commands.command as command

from sigan.config import get_config


cfg = get_config()

app = typer.Typer(rich_markup_mode='rich', help="Enter [red]sigan <command name> --help[/red] to see more detailed documentations of commands!")
app.registered_commands.extend(command.app.registered_commands)

def version_callback(value: bool):
    if value:
        print(f"{cfg.version}")
        raise typer.Exit()


@app.callback()
def pre_command_callback(ctx: typer.Context, version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True)):
    cmd = ctx.invoked_subcommand
    
    general_utils.config_setup(cfg.app_dir, cfg.config_path)

    if cmd == "add" or cmd == "show" or cmd == "delete" or cmd == "chcnt" or cmd == "chdate" or cmd == "chdl" or cmd == "chinv":
        try:
            user_info = general_utils.read_team_id(cfg.app_dir)
        except FileNotFoundError:
            raise typer.BadParameter("Registration is not complete.")