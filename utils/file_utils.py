import yaml


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


def write_file(file_path: str, new_file_content: dict):
    with open(file_path, "w") as file:
        yaml.dump(new_file_content, file)
