import shutil
from rich import box
from rich.console import Console
from rich.table import Table, Column
from rich.style import Style
from rich.text import Text
from rich.align import Align

import sigan.utils.general_utils as general_utils
import sigan.constants as constants
from sigan.config import get_config

cfg = get_config()

console = Console()

# def alarm_event_display
def alarm_table_display(alarm_list):
    table = Table(
        Column(header="ID", justify="center", header_style=constants.TABLE_HEADER_COLOR, style=Style(color=constants.TABLE_TEXT_COLOR)),
        Column(header="Content", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_ALARM_CONTENT_COLOR)),
        Column(header="Deadline", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TEXT_COLOR)),
        Column(header="Notification Time", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TEXT_COLOR)),
        Column(header="Interval", justify="right", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TEXT_COLOR)),
        box=box.HORIZONTALS,
        width=100,
        leading=-7
    )
    alarm_id_cache = {}
    for i in range(len(alarm_list)):
        alarm_id_cache[i + 1] = alarm_list[i]['alarm_id']
        table.add_row(str(i + 1),
                      str(alarm_list[i]['content']),
                      str(alarm_list[i]['deadline']),
                      str(alarm_list[i]['alarm_date']),
                      str(alarm_list[i]['interval']),
                      )
        
    
    general_utils.cache_alarm_id(cfg.app_dir, alarm_id_cache)
    
    return table


def center_print(text, type: str = None, wrap: bool = False):
    if type == "success":
        style = Style(
            color=constants.DISPLAY_TERMINAL_COLOR_SUCCESS_TEXT,
            bgcolor=constants.DISPLAY_TERMINAL_COLOR_SUCCESS_BACKGROUND,
        )
    elif type == "detail":
        style = Style(
            color=constants.DISPLAY_TERMINAL_COLOR_ERROR_TEXT,
            bgcolor=constants.DISPLAY_TERMINAL_COLOR_ERROR_BACKGROUND,
        )
        
    if wrap:
        width = shutil.get_terminal_size().columns // 2
    else:
        width = shutil.get_terminal_size().columns
        
    content = Text(text, style=style)
    console.print(Align.center(content, style=style, width=width), height=100)