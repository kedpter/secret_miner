# -*- coding: utf-8 -*-
'''

Linux + Windows Compatible

install this script under startup menu

sleep until 19:00
exit when 7:00

OPTION GPU
this script is gonna do following things
check if the gpu is using
if it is used, exit program
if not, start miner program

OPTION CPU
start miner program

'''

import click
import sys
import pkg_resources
import os
import subprocess
import configparser
import logging
from urllib.parse import urlparse
import psutil
import time
import re
import datetime
from sys import platform
import signal

package_name = "secret_miner"

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)
log_path = pkg_resources.resource_filename(package_name, 'sminer.log')
logging.basicConfig(filename=log_path, level=logging.DEBUG)

# package info
default_trigger_time = "19:00"
default_exit_time = "7:00"

# user setting
user_cfg = pkg_resources.resource_filename(package_name,
                                           os.path.join('data', 'miner.cfg'))
config = configparser.ConfigParser()
config.optionxform = str
config.read(user_cfg)
# address = config['BitCoin']['MiningAddress']
# username = config['BitCoin']['Username']
# password = config['BitCoin']['Password']

# miner exe path
CPU_MINER = "minerd.exe"
if platform == "darwin":
    CPU_MINER = "minerd"
GPU_NVIDIA_MINER = "ethminer"
cpu_miner_path = pkg_resources.resource_filename(
    package_name, os.path.join('data', 'cpuminer', CPU_MINER))
if platform == "darwin":
    cpu_miner_path = pkg_resources.resource_filename(
        package_name, os.path.join('data', CPU_MINER))
gpu_miner_path = pkg_resources.resource_filename(
    package_name, os.path.join('data', GPU_NVIDIA_MINER))

# for proc in psutil.process_iter():
#     # check whether the process name matches
#     if proc.name() == PROCNAME:
#         proc.kill()


def read_config():
    address = config['BitCoin']['MiningAddress']
    username = config['BitCoin']['Username']
    password = config['BitCoin']['Password']
    device = int(config['BitCoin']['Device'])
    tstart = config['BitCoin']['StartTimeInDay']
    tend = config['BitCoin']['EndTimeInDay']
    return (address, username, password, device, tstart, tend)


class DeviceNotSupportedError(Exception):
    """device is not supported"""


def kill_proc_tree(pid,
                   sig=signal.SIGTERM,
                   include_parent=True,
                   timeout=None,
                   on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callabck function which is
    called as soon as a child terminates.
    """
    if pid == os.getpid():
        raise RuntimeError("I refuse to kill myself")
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        p.send_signal(sig)
    gone, alive = psutil.wait_procs(
        children, timeout=timeout, callback=on_terminate)
    return (gone, alive)


class Runner:
    def __init__(self, dtype):
        self.dtype = dtype
        self.run_miner_cmd = []
        self.process = None
        self.miner = None

    def is_device_free(self):
        if self.dtype == 0:
            # cpu
            # if miner program is running
            # assume cpu busy
            for proc in psutil.process_iter():
                if proc.name() == CPU_MINER:
                    return False
            return True
        elif self.dtype == 1:
            # if nvidia-smi any card utilization % > 60
            # assume gpu busy
            utilz_threhold = 60
            checkutilz_cmd = [
                'nvidia-smi', '--query-gpu=utilization.gpu',
                '--format=csv,noheader'
            ]
            utilzs = subprocess.check_output(checkutilz_cmd)
            for u in utilzs.split():
                # take 99 % to 99,
                ui = int(re.search(r'\d+', u.decode('utf-8')).group())
                if (ui > utilz_threhold):
                    logger.info("gpu is busy")
                    return False
            return True
        else:
            raise DeviceNotSupportedError(
                "unsupported device [cpu or gpu only]")
        return False

    def run_cmd(self, cmd):
        logger.info('+++++++')
        self.miner = subprocess.Popen(cmd)
        logger.info('proc pid: %s', self.miner.pid)

    def run_miner_if_free(self):
        """TODO: docstring"""
        (address, username, password, device, tstart, tend) = read_config()

        if self.dtype == 0:
            self.run_miner_cmd = [
                cpu_miner_path, '-o', address, '-O', '{}:{}'.format(
                    username, password)
            ]
        elif self.dtype == 1:
            # parse address -> scheme + netloc
            r = urlparse(address)

            # scheme://user[:password]@hostname:port
            url = '{}://{}:{}@{}'.format(r.scheme, username, password,
                                         r.netloc)

            # Cuda
            self.run_miner_cmd = [gpu_miner_path, '-P', url, '-U']

        if (len(self.run_miner_cmd) != 0):
            logger.info(' '.join(self.run_miner_cmd))

            # start if resource(cpu or gpu) is free
            if (self.is_device_free()):
                logger.info('start miner in another thread')
                self.run_cmd(self.run_miner_cmd)
                # self.process = multiprocessing.Process(
                #     target=self.run_cmd, args=(self.run_miner_cmd, ))
                # self.process.start()

    def kill_miner_if_exists(self):
        if (not self.is_device_free() and self.miner):
            logger.info("=====miner pid: %s", self.miner.pid)
            self.miner.terminate()
            # self.process.terminate()
            logger.info("kill miner: miner is just killed")
        else:
            logger.info("kill miner: miner not found")
        # cur_proc = None
        # for proc in psutil.process_iter():
        #     if self.dtype == 0 and proc.name() == CPU_MINER:
        #         cur_proc = proc
        #     if self.dtype == 1 and proc.name() == GPU_NVIDIA_MINER:
        #         cur_proc = proc

        # if cur_proc:
        #     proc.kill()
        #     logger.info("kill miner: miner is just killed")
        # else:
        #     logger.info("kill miner: no miner program found")


@click.command()
@click.option('-s', '--save', is_flag=True, help='save config')
@click.option(
    '-t',
    '--test',
    type=click.Choice(['run', 'kill']),
    help='test run_if_device_free and kill_if_miner_exists'
    ', this option is mutually exlusive to --save')
@click.option(
    '-d',
    '--device',
    type=click.Choice(['0', '1']),
    help='device type: cpu[0] gpu[1]')
@click.option('-u', '--namepass', help='user:password')
@click.option('-a', '--address', help='mining address')
@click.option(
    '--tstart', default=default_trigger_time, help='secret mining start time')
@click.option(
    '--tend', default=default_exit_time, help='secret mining end time')
def save_and_test(save, test, device, namepass, address, tstart, tend):
    if test:
        (address, username, password, device, tstart, tend) = read_config()
        r = Runner(int(device))
        if test == 'run':
            logger.info("run_miner_if_free start")
            r.run_miner_if_free()
            logger.info("run_miner_if_free end")
            time.sleep(10)
            logger.info("kill miner if exists start")
            r.kill_miner_if_exists()
        if test == 'kill':
            r.kill_miner_if_exists()
    elif save and device and namepass and address:
        # prepare data
        # parse namepass
        username, password = namepass.split(":", 1)

        try:
            config.add_section('BitCoin')
        except configparser.DuplicateSectionError:
            pass
        config.set('BitCoin', 'MiningAddress', address)
        config.set('BitCoin', 'Username', username)
        config.set('BitCoin', 'Password', password)
        config.set('BitCoin', 'Device', device)
        config.set('BitCoin', 'StartTimeInDay', tstart)
        config.set('BitCoin', 'EndTimeInDay', tend)

        with open(user_cfg, 'w') as f:
            config.write(f)
            logger.info('save config success !')
    else:
        with click.Context(save_and_test) as ctx:
            click.echo(save_and_test.get_help(ctx))


class ConfigTimeError(Exception):
    pass


def get_time_by_cfgtime(now, cfgtime):
    t = None

    try:
        t = datetime.datetime.strptime(cfgtime, "%H:%M")
    except Exception:
        logger.error("time parse error, maybe user config wrong")
        raise ConfigTimeError("time parse error")
        return

    t = now.replace(hour=t.hour, minute=t.minute)
    return t


def main():
    """miner running secretly on cpu or gpu"""
    # # cpu
    # if type == '0':
    #     schedule.every().day.at(script_trigger_time).do(run_cpu_miner)
    #     pass
    # # gpu
    # elif type == '1':

    #     schedule.every().day.at(script_trigger_time).do(run_gpu_miner)
    #     pass

    # schedule.every().day.at(script_exit_time).do(sys.exit)

    # while True:
    #     schedule.run_pending()

    # if no arg, run secret miner
    if (len(sys.argv) == 1):
        while True:
            (address, username, password, device, tstart, tend) = read_config()
            now = datetime.datetime.now()
            start = get_time_by_cfgtime(now, tstart)
            end = get_time_by_cfgtime(now, tend)

            logger.info('start secret miner service')
            logger.info('now: ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            logger.info('start: ' + start.strftime("%Y-%m-%d %H:%M:%S"))
            logger.info('end: ' + end.strftime("%Y-%m-%d %H:%M:%S"))

            r = Runner(device)

            logger.info('Check if the correct time to run miner ?')
            if start > end:
                if now > start or now < end:
                    logger.info('Now is the correct time to run miner')
                    r.run_miner_if_free()
                else:
                    logger.info('Now is the correct time to kill miner')
                    r.kill_miner_if_exists()
            else:
                if now > start and now < end:
                    logger.info('Now is the correct time to run miner')
                    r.run_miner_if_free()
                else:
                    logger.info('Now is the correct time to kill miner')
                    r.kill_miner_if_exists()

            time.sleep(5)
    else:
        save_and_test()
    # # if arg[2] == '-s', save config (format: user:pass@address)
    # if (len(sys.argv) > 2 and sys.argv[1] == '-s'):
    #     user_input = sys.argv[2]
    #     save_and_test(user_input)
    #     pass


if __name__ == "__main__":
    main()
