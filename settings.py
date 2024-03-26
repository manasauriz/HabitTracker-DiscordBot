import os
from dotenv import load_dotenv
import logging
from logging.config import dictConfig

load_dotenv()
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_Loggers": False,
    "formatters":{
        "verbose":{
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "simple":{
            "format": "%(levelname)-10s - %(name)-10s : %(message)s"
        }
    },
    "handlers":{
        "console":{
             'level': "INFO",
             'class': "logging.StreamHandler",
             'formatter': "simple"
        },
        "file":{
            'level': "DEBUG",
             'class': "logging.FileHandler",
             'filename': "info.log",
             'mode': "w",
             'formatter': "verbose"
        }
    },
    "loggers":{
        "bot":{
            'handlers': ["console"],
            'level': "INFO",
            'propagate': False
        },
        "discord":{
            'handlers': ["file"],
            'level': "DEBUG",
            'propagate': False
        }
    }
}

dictConfig(LOGGING_CONFIG)