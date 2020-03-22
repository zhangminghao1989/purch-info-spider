#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'一个招投标网站信息采集工具'
__author__ = 'Zhang Minghao'

import config_load, logging, os, sys
from logging import handlers
from colorlog import ColoredFormatter

try:
    os.mkdir('log')
except FileExistsError:
    pass

conf = config_load.load_conf()
LOG_LEVEL = conf.get('DEFAULT', 'log_level')
if LOG_LEVEL == 'DEBUG':
    LOG_LEVEL = logging.DEBUG
elif LOG_LEVEL == 'INFO':
    LOG_LEVEL = logging.INFO
elif LOG_LEVEL == 'WARNING':
    LOG_LEVEL = logging.WARNING
elif LOG_LEVEL == 'ERROR':
    LOG_LEVEL = logging.ERROR
elif LOG_LEVEL == 'CRITICAL':
    LOG_LEVEL = logging.CRITICAL
else:
    LOG_LEVEL = logging.WARNING

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
color_formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'white',
        'INFO':     'green',
        'WARNING':  'cyan',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    }
)

# 创建一个日志器logger并设置其日志级别为DEBUG
logger = logging.getLogger('Spider')
logger.setLevel(logging.DEBUG)

# 创建一个流处理器，可直接输出到屏幕，设置其日志级别为LOG_LEVEL
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(LOG_LEVEL)
stdout_handler.setFormatter(color_formatter)
logger.addHandler(stdout_handler)

# 创建一个流处理器，将所有级别日志输出到文件all.log
all_handler = handlers.TimedRotatingFileHandler(filename='./log/all.log', when="D", interval=1, backupCount=5)
all_handler.setLevel(logging.DEBUG)
all_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(all_handler)

# 创建一个流处理器，将WARNING级别日志输出到文件info.log
warning_handler = handlers.TimedRotatingFileHandler(filename='./log/info.log', when="D", interval=1, backupCount=5)
warning_handler.setLevel(logging.INFO)
warning_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(warning_handler)

# 创建一个流处理器，将WARNING级别日志输出到文件warning.log
warning_handler = handlers.TimedRotatingFileHandler(filename='./log/warning.log', when="D", interval=1, backupCount=5)
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(warning_handler)

# 创建一个流处理器，将ERROR级别日志输出到文件error.log
error_handler = handlers.TimedRotatingFileHandler(filename='./log/error.log', when="D", interval=1, backupCount=5)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(error_handler)
def debug(message):
    logger.debug(message)
    return

def info(message):
    logger.info(message)
    return
    
def warning(message):
    logger.warning(message)
    return

def error(message):
    logger.error(message)
    return

def critical(message):
    logger.critical(message)
    return