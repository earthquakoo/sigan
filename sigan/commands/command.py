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


def deadline_callback(value: str):
    if value is None:
        return None
    
    value = value.strip()
    args = value.split(" ")
    
    date = args[0]
    if not re.match("^([0-9]){4}/([0-9]){1,2}/([0-9]){1,2}|([0-9]){1,2}/([0-9]){1,2}$", date):
        raise typer.BadParameter("Deadline must be in 'yyyy/mm/dd' or 'mm/dd' format.")
    
    year, month, day = datetime.now().year, None, None
    date_list = list(map(int, date.split('/')))
    if len(date_list) == 3:
        year, month, day = date_list
    elif len(date_list) == 2:
        month, day = date_list
    
    return f"{year}/{month}/{day}"


def alarm_date_callback(value: str):
    if value is None:
        return "09:00"
    
    value = value.strip()
    args = value.split(" ")
    
    date = args[0]
    
    if re.match("^[0-9]{2}:[0-9]{2}$", date):
        return f"{date}"
    
    if not re.match("^([0-9]){4}/([0-9]){1,2}/([0-9]){1,2}|([0-9]){1,2}/([0-9]){1,2}$", date):
        raise typer.BadParameter("Deadline must be in 'yyyy/mm/dd' or 'mm/dd' format.")
    
    year, month, day = datetime.now().year, None, None
    date_list = list(map(int, date.split('/')))
    if len(date_list) == 3:
        year, month, day = date_list
    elif len(date_list) == 2:
        month, day = date_list
    
    if len(args) == 1:
        time = "09:00"
        return year, month, day, time
    
    time = args[1]
    
    if not re.match("^[0-9]{2}:[0-9]{2}$", time):
        raise typer.BadParameter(f"Invalid time: {time}, Time must be in hh:mm format.")
    
    hour, minute = time.split(':')
    if not time_utils.is_valid_hour(int(float(hour))):
        raise typer.BadParameter(f"Invalid hour: {hour}. Hour must be in [00-23].")
    if not time_utils.is_valid_minute(int(float(minute))):
        raise typer.BadParameter(f"Invalid minute: {minute}. Hour must be in [00-59].")
    
    return year, month, day, time


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


def change_alarm_date_callback(value: str):
    if value is None:
        return None
    
    value = value.strip()
    args = value.split(" ")
    
    date = args[0]
    
    if re.match("^[0-9]{2}:[0-9]{2}$", date):
        return f"{date}"
    
    if not re.match("^([0-9]){4}/([0-9]){1,2}/([0-9]){1,2}|([0-9]){1,2}/([0-9]){1,2}$", date):
        raise typer.BadParameter("Deadline must be in 'yyyy/mm/dd' or 'mm/dd' format.")
    
    year, month, day = datetime.now().year, None, None
    date_list = list(map(int, date.split('/')))
    if len(date_list) == 3:
        year, month, day = date_list
    elif len(date_list) == 2:
        month, day = date_list
    
    if len(args) == 1:
        return year, month, day
    
    time = args[1]
    
    if not re.match("^[0-9]{2}:[0-9]{2}$", time):
        raise typer.BadParameter(f"Invalid time: {time}, Time must be in hh:mm format.")
    
    hour, minute = time.split(':')
    if not time_utils.is_valid_hour(int(float(hour))):
        raise typer.BadParameter(f"Invalid hour: {hour}. Hour must be in [00-23].")
    if not time_utils.is_valid_minute(int(float(minute))):
        raise typer.BadParameter(f"Invalid minute: {minute}. Hour must be in [00-59].")
    
    return year, month, day, time



@app.command("add", help="[yellow]Add[/yellow] a new alarm", rich_help_panel=":alarm_clock: Alarm Commands")
def add_alarm(
    cnt: str = typer.Argument(..., help="Alarm Content Input."),
    deadline: str = typer.Option(None, "-d", "--deadline", help="Deadline, [yellow]yyyy/mm/dd or mm/dd[/yellow]", callback=deadline_callback),
    alarm_date: str = typer.Option(None, '-t', '--time', help="Alarm sending date or time, [yellow]yyyy/mm/dd or mm/dd or yyyy/mm/dd hh:mm or mm/dd hh:mm, if you enter 'hh:mm' only the interval must be set to mandatory[/yellow]", callback=alarm_date_callback),
    interval: str = typer.Option(None, '-i', '--interval', help="Alarm [yellow]interval[/yellow] setting.", callback=interval_callback),
    before: int = typer.Option(None, "-b", "--before", help="Set alarm sending date deadline[yellow] x days before[/yellow]", callback=before_callback),
    slack_channel: str = typer.Option(None, '-c', '--channel', help="[yellow]Slack Channel[/yellow] Input.", callback=slack_channel_callback)
    ):
    
    if interval:
        # interval을 지정했는데 날짜와 시간이 모두 입력한 경우
        if len(alarm_date) == 4:
            raise typer.BadParameter("The interval cannot be set when a date is entered.")
        
        year, month, day = time_utils.get_date_from_shortcut(interval, alarm_date)
        time = alarm_date
        
        if "everyday" in interval:
            interval = "everyday"
        else:
            interval = 'every ' + ' '.join(interval)
    else:
        # interval을 입력하지 않았는데 시간만 입력한 경우
        if len(alarm_date) == 5:
            raise typer.BadParameter("If you enter time or None, the interval must be set to mandatory.")
        year, month, day, time = alarm_date
    
    notification_time = f"{year}/{month}/{day} {time}:00"
    
    if deadline:
        deadline_year, deadline_month, deadline_day = time_utils.change_deadline_to_date(deadline)
        deadline_datetime = datetime.strptime(f"{deadline_year}/{deadline_month}/{deadline_day} {time}:00", '%Y/%m/%d %H:%M:%S')
        alarm_datetime = datetime.strptime(notification_time, '%Y/%m/%d %H:%M:%S')
        if deadline_datetime < alarm_datetime:
            raise typer.BadParameter("Cannot set alarm later than Deadline.")
        
        confirm_alarm_date = deadline_datetime - timedelta(days=1)
        if confirm_alarm_date < datetime.now():
            confirm_alarm_date = None
        else:
            confirm_alarm_date = str(confirm_alarm_date)
        
        if before:
            confirm_alarm_date = deadline_datetime - timedelta(days=before)
            if confirm_alarm_date < datetime.now():
                raise typer.BadParameter("Reservation cannot be set before today's date.")
            confirm_alarm_date = str(confirm_alarm_date)
    else:
        if before:
            raise typer.BadParameter("To set the after, you must set the deadline first.")
        
        confirm_alarm_date = None
        
    user_info = general_utils.read_team_id(cfg.app_dir)

    alarm_data = {
        "content": cnt,
        "deadline": deadline,
        "alarm_date": notification_time,
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
    alarm_id_cache = general_utils.read_alarm_id(cfg.app_dir)
    alarm_data = { 
        "alarm_id": alarm_id_cache,
        "content": new_cnt,
        "team_id": user_info['team_id']
    }
    
    user_id = slack_api.change_content(alarm_data)
    alarm_list = slack_api.get_all_alarm(user_id)
    alarm_table = display.alarm_table_display(alarm_list)
    console.print(Align.center(alarm_table))


@app.command("chdl", help="[purple]Change[/purple] alarm deadline", rich_help_panel=":alarm_clock: Alarm Commands")
def change_deadline(
    alarm_id: int = typer.Argument(..., help="[yellow]Alarm ID[/yellow] to be [purple]changed[/purple]"),
    deadline: str = typer.Option(..., help="deadline, [yellow]yyyy:mm:dd or mm:dd[/yellow]", callback=deadline_callback),
    ):

    user_info = general_utils.read_team_id(cfg.app_dir)
    alarm_id_cache = general_utils.read_alarm_id(cfg.app_dir, alarm_id)
    if alarm_id_cache is None:
        display.center_print(f"Alarm id {alarm_id} is not found.", type='detail')
        exit(0)
    alarm_data = {
        "alarm_id": alarm_id_cache,
        "deadline": deadline,
        "team_id": user_info['team_id']
    }

    user_id = slack_api.change_deadline(alarm_data)
    alarm_list = slack_api.get_all_alarm(user_id)
    alarm_table = display.alarm_table_display(alarm_list)
    console.print(Align.center(alarm_table))


@app.command("chdate", help="[purple]Change[/purple] alarm date", rich_help_panel=":alarm_clock: Alarm Commands")
def change_date(
    alarm_id: int = typer.Argument(..., help="[yellow]Alarm ID[/yellow] to be [purple]changed[/purple]"),
    date: str = typer.Option(..., help="Alarm sending date or time, [yellow]yyyy/mm/dd or mm/dd or yyyy/mm/dd hh:mm or mm/dd hh:mm", callback=change_alarm_date_callback),
    ):
    
    if len(date) == 3:
        year, month, day = date
        notification_time = f"{year}/{month}/{day}"
    elif len(date) == 4:
        year, month, day, time = date
        notification_time = f"{year}/{month}/{day} {time}:00"  
    elif len(date) == 5:
        time = date
        notification_time = f"{time}"

    alarm_id_cache = general_utils.read_alarm_id(cfg.app_dir, alarm_id)
    if alarm_id_cache is None:
        display.center_print(f"Alarm id {alarm_id} is not found.", type='detail')
        exit(0) 
        
    user_info = general_utils.read_team_id(cfg.app_dir)
    
    alarm_data = {
        "alarm_id": alarm_id_cache,
        "alarm_date": notification_time,
        "team_id": user_info['team_id']
    }
    
    user_id = slack_api.change_date(alarm_data)
    alarm_list = slack_api.get_all_alarm(user_id)
    alarm_table = display.alarm_table_display(alarm_list)
    console.print(Align.center(alarm_table))


@app.command("chinv", help="[purple]Change[/purple] alarm interval", rich_help_panel=":alarm_clock: Alarm Commands")
def change_interval(
    alarm_id: int = typer.Argument(..., help="[yellow]Alarm ID[/yellow] to be [purple]changed[/purple]"),
    interval: str = typer.Option(..., help="[yellow]New interval[yellow]", callback=interval_callback)
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