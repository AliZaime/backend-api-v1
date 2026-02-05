import logging

logger = logging.getLogger("device_monitoring")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Pour usage dans tous les modules :
# from helpers.logger import logger
