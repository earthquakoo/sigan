import typer, re
from datetime import datetime, timedelta

from rich.console import Console
from rich.align import Align

import sys
sys.path.append('.')


import sigan.api.api as slack_api
import sigan.utils.general_utils as general_utils
import sigan.utils.time_utils as time_utils
import sigan.utils.display as display
from sigan.config import get_config

cfg = get_config()

console = Console()
app = typer.Typer(rich_markup_mode="rich")


def date_callback(value: str):
    if value is None:
        return None
    
    value = value.strip()
    args = value.split(" ")
    
    date = args[0]
    if not re.match("^([0-9]){4}/([0-9]){2}/([0-9]){2}|([0-9]){2}/([0-9]){2}$", date):
        raise typer.BadParameter("Deadline must be in 'yyyy/mm/dd' or 'mm/dd' format.")
    
    year, month, day = datetime.now().year, None, None
    date_list = list(map(int, date.split('/')))
    if len(date_list) == 3:
        year, month, day = date_list
    elif len(date_list) == 2:
        month, day = date_list
    
    return year, month, day


def time_callback(value: str):  
    value = value.strip()
    args = value.split(" ")
    
    time = args[0]
    
    if not re.match("^[0-9]{2}:[0-9]{2}$", time):
        raise typer.BadParameter(f"Invalid time: {time}, Time must be in hh:mm format.")
    
    hour, minute = time.split(':')
    if not time_utils.is_valid_hour(int(float(hour))):
        raise typer.BadParameter(f"Invalid hour: {hour}. Hour must be in [00-23].")
    if not time_utils.is_valid_minute(int(float(minute))):
        raise typer.BadParameter(f"Invalid minute: {minute}. Hour must be in [00-59].")
    
    return time


def interval_callback(value: str):
    if value is None:
        return None
    
    interval_set = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'everyday'}
    
    value = value.strip()
    args = value.split(" ")
    
    if "everyday" in args and len(args) > 1:
        raise typer.BadParameter("If you set alarms every day, you cannot add other options.")
    
    if not set(args).issubset(interval_set):
        raise typer.BadParameter("A valid notation example for a interval is as shown in 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun' or 'everyday'.")
    
    return args


def before_callback(value: int):
    if value is None:
        return None

    if value <= 0:
        raise typer.BadParameter(f"Invalid offset: {value}. It must be greater than 0.")
    return value


def slack_channel_callback(value: str):
    if value is None:
        return "SiganBot"


@app.command("add", help="[yellow]Add[/yellow] a new alarm", rich_help_panel=":alarm_clock: Alarm Commands")
def add_alarm(
    cnt: str = typer.Argument(..., help="Alarm Content Input."),
    date: str = typer.Option(None, "-d", "--date", help="Alarm sending date, [yellow]yyyy/mm/dd or mm/dd[/yellow]", callback=date_callback),
    time: str = typer.Option(..., '-t', '--time', help="Alarm sending time, [yellow]hh:mm[/yellow]", callback=time_callback),
    interval: str = typer.Option(None, '-i', '--interval', help="Alarm [yellow]interval[/yellow] setting.", callback=interval_callback),
    before: int = typer.Option(None, "-b", "--before", help="Set alarm sending date deadline[yellow] x days before[/yellow]", callback=before_callback),
    slack_channel: str = typer.Option(None, '-c', '--channel', help="[yellow]Slack Channel[/yellow] Input.", callback=slack_channel_callback),
    force: bool = typer.Option(False, '-y', '--yes', help="Don't send a confirmation notification.")
    ):
    
    if time:
        if not interval and not date:
            raise typer.BadParameter("If you enter only the time, you must set the interval or date.")
    
    if interval:
        if date:
            raise typer.BadParameter("The interval cannot be set when a date is entered.")
        
        year, month, day = time_utils.get_date_from_shortcut(interval, time)
        
        if "everyday" in interval:
            interval = "everyday"
        else:
            interval = 'every ' + ' '.join(interval)
    else:
        year, month, day = date
    
    alarm_datetime = datetime.strptime(f"{year}/{month}/{day} {time}:00", '%Y/%m/%d %H:%M:%S')
    
    if date:        
        if not force and not before:            
            confirm_alarm = typer.confirm("Do you want to receive a confirmation alarm one day before the specified date?")
            if confirm_alarm:
                confirm_alarm_date = alarm_datetime - timedelta(days=1)
                if confirm_alarm_date < datetime.now():
                    raise typer.BadParameter("Confirmation alarm cannot be set before today's date.")
                confirm_alarm_date = str(confirm_alarm_date)
            else:
                confirm_alarm_date = None
                    
        if before:
            if force:
                raise typer.BadParameter("You cannot use the before and force commands at the same time.")
            
            confirm_alarm_date = alarm_datetime - timedelta(days=before)
            if confirm_alarm_date < datetime.now():
                raise typer.BadParameter("Confirmation alarm cannot be set before today's date.")
            confirm_alarm_date = str(confirm_alarm_date)
    else:
        if before:
            raise typer.BadParameter("Before can only be set by setting the date.")
        
        confirm_alarm_date = None
    
    
    user_info = general_utils.read_team_id(cfg.app_dir)

    alarm_data = {
        "content": cnt,
        "alarm_date": f"{year}/{month}/{day}",
        "alarm_time": f"{time}",
        "interval": interval,
        "confirm_alarm_date": confirm_alarm_date,
        "slack_channel_name": slack_channel,
        "team_id": user_info['team_id']
    }

    user_id = slack_api.create_alarm(alarm_data)
    alarm_list = slack_api.get_all_alarm(user_id)
    alarm_table = display.alarm_table_display(alarm_list)
    console.print(Align.center(alarm_table))


@app.command("delete", help="[red]Delete[/red] a alarm", rich_help_panel=":alarm_clock: Alarm Commands")
def delete_alarm(
    alarm_id: int = typer.Argument(..., help="[yellow]Alarm ID[/yellow] to be [red]deleted[/red]"),
    force: bool = typer.Option(False, '-y', '--yes', help="Don't show the confirmation message")
    ):
    
    if not force:
        delete_confirm = typer.confirm(f"Are you sure to delete alarm [{alarm_id}]?")
        if not delete_confirm:
            exit(0)
            
    alarm_id_cache = general_utils.read_alarm_id(cfg.app_dir, alarm_id)
    if alarm_id_cache is None:
        display.center_print(f"Alarm id {alarm_id} is not found.", type='detail')
        exit(0)
    user_info = general_utils.read_team_id(cfg.app_dir)
    alarm_data = {
        "alarm_id": alarm_id_cache,
        "team_id": user_info['team_id']
    }
    
    user_id = slack_api.delete_alarm(alarm_data)
    alarm_list = slack_api.get_all_alarm(user_id)
    alarm_table = display.alarm_table_display(alarm_list)
    console.print(Align.center(alarm_table))


@app.command("show", help="[green]Show[/green] alarm event", rich_help_panel=":alarm_clock: Alarm Commands")
def show_alarm():
    
    user_info = general_utils.read_team_id(cfg.app_dir)
    alarm_data = {
        "team_id": user_info['team_id']
    }
    
    alarm_list = slack_api.get_all_alarm(alarm_data)
    alarm_table = display.alarm_table_display(alarm_list)
    display.center_print("Show Alarm Event", type="success")
    console.print(Align.center(alarm_table))


@app.command("chcnt", help="[purple]Change[/purple] alarm content", rich_help_panel=":alarm_clock: Alarm Commands")
def change_content(
    alarm_id: int = typer.Argument(..., help="[yellow]Alarm ID[/yellow] to be [purple]changed[/purple]"),
    new_cnt: str = typer.Argument(..., help="[yellow]New content[/yellow]"),
    ):
    
    alarm_id_cache = general_utils.read_alarm_id(cfg.app_dir, alarm_id)
    if alarm_id_cache is None:
        display.center_print(f"Alarm id {alarm_id} is not found.", type='detail')
        exit(0)
    
    user_info = general_utils.read_team_id(cfg.app_dir)
    alarm_id_cache = general_utils.read_alarm_id(cfg.app_dir, alarm_id)
    alarm_data = { 
        "alarm_id": alarm_id_cache,
        "content": new_cnt,
        "team_id": user_info['team_id']
    }
    
    user_id = slack_api.change_content(alarm_data)
    alarm_list = slack_api.get_all_alarm(user_id)
    alarm_table = display.alarm_table_display(alarm_list)
    console.print(Align.center(alarm_table))


@app.command("chdate", help="[purple]Change[/purple] alarm date", rich_help_panel=":alarm_clock: Alarm Commands")
def change_date(
    alarm_id: int = typer.Argument(..., help="[yellow]Alarm ID[/yellow] to be [purple]changed[/purple]"),
    date: str = typer.Argument(..., help="Alarm sending date or time, [yellow]yyyy/mm/dd or mm/dd", callback=date_callback),
    ):
    
    year, month, day = date

    alarm_id_cache = general_utils.read_alarm_id(cfg.app_dir, alarm_id)
    if alarm_id_cache is None:
        display.center_print(f"Alarm id {alarm_id} is not found.", type='detail')
        exit(0) 
        
    user_info = general_utils.read_team_id(cfg.app_dir)
    
    alarm_data = {
        "alarm_id": alarm_id_cache,
        "alarm_date": f"{year}/{month}/{day}",
        "team_id": user_info['team_id']
    }
    
    user_id = slack_api.change_date(alarm_data)
    alarm_list = slack_api.get_all_alarm(user_id)
    alarm_table = display.alarm_table_display(alarm_list)
    console.print(Align.center(alarm_table))


@app.command("chtime", help="[purple]Change[/purple] alarm time", rich_help_panel=":alarm_clock: Alarm Commands")
def change_time(
    alarm_id: int = typer.Argument(..., help="[yellow]Alarm ID[/yellow] to be [purple]changed[/purple]"),
    time: str = typer.Argument(..., help="Alarm sending time, [yellow]hh:mm", callback=time_callback),
    ):

    alarm_id_cache = general_utils.read_alarm_id(cfg.app_dir, alarm_id)
    if alarm_id_cache is None:
        display.center_print(f"Alarm id {alarm_id} is not found.", type='detail')
        exit(0) 
        
    user_info = general_utils.read_team_id(cfg.app_dir)
    
    alarm_data = {
        "alarm_id": alarm_id_cache,
        "alarm_time": f"{time}",
        "team_id": user_info['team_id']
    }
    
    user_id = slack_api.change_time(alarm_data)
    alarm_list = slack_api.get_all_alarm(user_id)
    alarm_table = display.alarm_table_display(alarm_list)
    console.print(Align.center(alarm_table))


@app.command("chinv", help="[purple]Change[/purple] alarm interval", rich_help_panel=":alarm_clock: Alarm Commands")
def change_interval(
    alarm_id: int = typer.Argument(..., help="[yellow]Alarm ID[/yellow] to be [purple]changed[/purple]"),
    interval: str = typer.Argument(..., help="[yellow]New interval[yellow]", callback=interval_callback)
    ):
    
    if "everyday" in interval:
        interval = "everyday"
    else:
        interval = 'every ' + ' '.join(interval)
    
    user_info = general_utils.read_team_id(cfg.app_dir)
    alarm_id_cache = general_utils.read_alarm_id(cfg.app_dir, alarm_id)
    if alarm_id_cache is None:
        display.center_print(f"Alarm id {alarm_id} is not found.", type='detail')
        exit(0)
    alarm_data = {
        "alarm_id": alarm_id_cache,
        "interval": interval,
        "team_id": user_info['team_id']
    }

    user_id = slack_api.change_interval(alarm_data)
    alarm_list = slack_api.get_all_alarm(user_id)
    alarm_table = display.alarm_table_display(alarm_list)
    console.print(Align.center(alarm_table))
    
    

@app.command("register", help="[green]Register[/green] slack team id", rich_help_panel=":lock: [bold yellow1]Authentication Commands[/bold yellow1]")
def register():
    is_register = typer.confirm("Do you want to register a new slack team ID?")
    if is_register:
        team_id = typer.prompt("\nEnter slack team id")
        user_data = {
            "team_id": team_id
        }
        user_info = slack_api.register(user_data)
    else:
        exit(0)
    
    general_utils.cache_team_id(cfg.app_dir, user_info)
    # display.center_print("Register successfully!", type="success")