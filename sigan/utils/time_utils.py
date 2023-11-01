from datetime import datetime, timedelta


def is_valid_hour(hour: int):
    if hour < 0 or hour > 23:
        return False
    return True


def is_valid_minute(minute: int):
    if minute < 0 or minute > 59:
        return False
    return True


def get_date_from_shortcut(interval_day: list, time: str):
    alarm_date = f"{datetime.now().year}-{datetime.now().month}-{datetime.now().day} {time}:00"
    alarm_date = datetime.strptime(alarm_date, '%Y-%m-%d %H:%M:%S')

    if "everyday" in interval_day:
        if alarm_date < datetime.now():
            alarm_date += timedelta(days=1)
        return alarm_date.year, alarm_date.month, alarm_date.day
    
    weekday_mapping = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}  
    current_weekday_list = []
    
    current_weekday_num = datetime.now().weekday()
    
    for interval in interval_day:
        day_offset = weekday_mapping[interval] - current_weekday_num
        current_weekday_list.append(day_offset)
    
    # 0에서 가장 가까운 양수부터 음수 순으로 정렬
    current_weekday_list = sorted(current_weekday_list, key=lambda x: (abs(x), -x))

    if current_weekday_list[0] < 0:
        alarm_date += timedelta(days=current_weekday_list[-1]+7)
        return alarm_date.year, alarm_date.month, alarm_date.day
    
    for day_offset in current_weekday_list:        
        if alarm_date + timedelta(days=day_offset) > datetime.now():
            alarm_date += timedelta(days=day_offset)
            return alarm_date.year, alarm_date.month, alarm_date.day
        else:
            date_offset = alarm_date + timedelta(days=7+day_offset)
    
    return date_offset.year, date_offset.month, date_offset.day
