import time
from loguru import logger
from pathlib import Path

#project_path = Path.cwd().parent
project_path = Path.cwd()
log_path = Path(project_path)
# t = time.strftime("%Y_%m_%d_%H_%M_%S")
t = time.strftime("%m_%d_%Y")



class Loggings:
    __instance = None
    loggingFullPath = f"{log_path}\\signal4gmns_log_{t}.log"
    logger.remove(handler_id=None)# console off
    # format_output="{time} |{level}|{message}"
    format_output = "{message}"
    logger.add(sink=loggingFullPath, format=format_output, rotation="500MB", encoding="utf-8", enqueue=True)
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Loggings, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    def info(self, msg, level=1):
        print("--" * level + msg)
        return logger.info("--" * level + msg)

    def debug(self, msg):
        return logger.debug(msg)

    def warning(self, msg):
        return logger.warning(msg)

    def error(self, msg):
        return logger.error(msg)

    def critical(self, msg):
        return logger.critical(msg)

# if __name__ == '__main__':
#     loggings = Loggings()
#     outString = "Hello vol2timing!"
#     loggings.info(outString, 1)
#     loggings.debug(outString)
#     loggings.warning(outString)
#     loggings.error(outString)
#     loggings.critical(outString)
#
#     n1 = "v1.0"
#     n2 = [1, 2, 3]
#     loggings.info(f'The logging system for vol2timing {n1}, prefer {n2} of course!', 1)
