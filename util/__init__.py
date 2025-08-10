def log(message: str):
    with open("log", "a") as log_file:
        log_file.write(f"{message}\n")


def clear_log():
    open("log", "w")
