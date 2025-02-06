from datetime import datetime


def format_file_name():
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S").split(":")
    seconds = sum(int(x) * 60**i for i, x in enumerate(reversed(timestamp)))
    return f"{now.strftime('%Y-%m-%d')}_{seconds}_questrade_activities.txt"
