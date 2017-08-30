import VZAtollCfg as cfg
import logging
import argparse
import glob
import os
import shutil
import time

basedir = r'\\win.eng.vzwnet.com\Atoll'
userdir = os.path.join(basedir, 'Atoll_Users')
pathloss1 = os.path.join(basedir, 'AtollPathlossData1')
pathloss2 = os.path.join(basedir, 'AtollPathlossData2')

# LOGGER
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

stats = {}

protected_users = ['chanade', 'hadina4']

def remove(path):
    if os.path.isdir(path):
        try:
            os.rmdir(path)
        except (OSError, WindowsError):
            logger.error('Failed to remove directory {}'.format(path))
    else:
        try:
            os.remove(path)
        except (OSError, WindowsError):
            logger.error('Failed to remove file {}'.format(path))

def cleanup(folder, path, months):

    max_age = time.time() - (months * 30 * 24 * 60 * 60)
    for root, dirs, files in os.walk(path, topdown=False):
        for f in files:
            if not f.endswith('.los'):
                continue
            fpath = os.path.join(root, f)
            try:
                stat = os.stat(fpath)
            except (OSError, WindowsError):
                logger.error('Failed to stat file {}'.format(fpath))
                continue
            if stat.st_mtime < max_age:
                remove(fpath)
                stats[folder]['files'] += 1
                stats[folder]['bytes'] += stat.st_size


if __name__ == '__main__':

    #dirs = [ userdir, pathloss1, pathloss2 ]
    dirs = [ userdir ]

    for d in dirs:

        dirName = os.path.basename(os.path.normpath(d))
        logName = '{}_cleanup.log'.format(dirName)
        logFile = os.path.join(basedir, 'AtollData\\Dev\\Log\\{}'.format(logName))
        fileHandler = logging.FileHandler(logFile)
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

        subdirs = [ u for u in sorted(os.listdir(d)) ]

        stats['total'] = {}
        stats['total']['files'] = 0
        stats['total']['bytes'] = 0

        for subdir in subdirs:
            if subdir in protected_users:
                continue
            fullPath = os.path.join(d, subdir)

            stats[subdir] = {}
            stats[subdir]['files'] = 0
            stats[subdir]['bytes'] = 0

            cleanup(subdir, fullPath, 1)
            if stats[subdir]['files'] > 0:
                stats['total']['files'] += stats[subdir]['files']
                stats['total']['bytes'] += stats[subdir]['bytes']
                logger.info('{}: {} files {} bytes'.format(fullPath, stats[subdir]['files'], stats[subdir]['bytes']))
        logger.info('TOTAL: {} files {} bytes'.format(stats['total']['files'], stats['total']['bytes']))
