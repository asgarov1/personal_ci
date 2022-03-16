from datetime import datetime


def write_to_log_file(e, log_folder):
    npm_output = e.output.decode("utf-8")
    with open(datetime.now().strftime(f"./{log_folder}/D%m_%dT%H_%M.txt"), "w") as f:
        f.write(npm_output)