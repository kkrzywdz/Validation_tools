import logging
import logging.config
from logs import *
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': { 
        '': {  # root logger
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'my.func': { 
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
    } 
}


if __name__ == "__main__":
    # Run once at startup:
    logging.config.dictConfig(LOGGING_CONFIG)
    # Include in each module:
    logger = logging.getLogger(__name__)
    for handler in logger.handlers:
        handler.setLevel('DEBUG')

    Log.info(logger,"Logging info configured")
    Log.debug(logger, "Logging debug configured.")
    Log.warning(logger, "Logging warning configured")
    Log.error(logger,"Logging error configured")
    Log.critical(logger,"Logging critical configured")