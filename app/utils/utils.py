import yaml, time
from datetime import datetime
from pathlib import Path


def yaml_file_exists(filepath: str) -> bool:
    path = Path(filepath)
    return path.is_file() and path.suffix.lower() in {".yaml", ".yml"}


def append_to_file(filename: str, data: str):
    with open(filename, "a") as file:
        file.write(f"{data}\n")


def open_file(file_path: str):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as exc:
        print(exc)
        return None


def generate_expiry_timestamp(seconds_from_now: int) -> int:
    return int(time.time()) + seconds_from_now


def write_file(file_path: str, new_file_content: dict):
    with open(file_path, "w") as file:
        yaml.dump(new_file_content, file)


def format_file_name():
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S").split(":")
    seconds = sum(int(x) * 60**i for i, x in enumerate(reversed(timestamp)))
    return f"{now.strftime('%Y-%m-%d')}_{seconds}_questrade_activities.txt"
