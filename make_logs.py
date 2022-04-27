import logging

logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


def log_to_file(message):
    logging.error(message)
