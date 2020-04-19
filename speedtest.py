# coding: utf8

import collectd
import os
import subprocess
import json

from pprint import pprint

INTERVAL = 10
SERVERS = []
SPEEDTEST_BIN = '/usr/bin/speedtest'
USER = 'root'

plugin_name = 'speedtest-test'

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def run_speedtest(command):
    collectd.info('run_speedtest: ' + command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.stdout.readlines()
    for o in output:
        collectd.debug('speedtest output: ' + o)
    result = json.loads(output[0])
    return result


def update_collectd(result):
    collectd.debug('speedtest plugin: update data')

    stat = collectd.Values(type="gauge", type_instance="ping")
    stat.plugin = plugin_name
    host = result['server']['host']
    stat.plugin_instance = host
    latency = float(result['ping']['latency'])
    collectd.debug('speedtest plugin latency: ' + str(latency))
    stat.dispatch(values=[latency], interval=INTERVAL)

    stat = collectd.Values(type="gauge", type_instance="download")
    stat.plugin = plugin_name
    stat.plugin_instance = host
    download_mbits = (float(result['download']['bandwidth'])*8) / 1000.0 / 1000.0
    collectd.debug('speedtest plugin download mbits: ' + str(download_mbits))
    stat.dispatch(values=[download_mbits], interval=INTERVAL)

    stat = collectd.Values(type="gauge", type_instance="upload")
    stat.plugin = plugin_name
    stat.plugin_instance = host
    upload_mbits = (float(result['upload']['bandwidth'])*8) / 1000.0 / 1000.0
    collectd.debug('speedtest plugin upload mbits: ' + str(upload_mbits))
    stat.dispatch(values=[upload_mbits], interval=INTERVAL)


def config_func(config):

    # Checking for speedtest binary
    s = which("speedtest")
    s = SPEEDTEST_BIN
    if s is None:
        collectd.error('speedtest plugin: speedtest not found.')
    else:
        global SPEEDTEST_BIN
        SPEEDTEST_BIN = s

    for node in config.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'interval':
            global INTERVAL
            INTERVAL = int(val)

        if key == 'serverid':
            global SERVERS
            SERVERS.append(int(val))
        if key == 'user':
            global USER
            USER = str(val)

    if len(SERVERS) == 0:
        collectd.info('speedtest plugin: No server specified, speedtest will use the best server.')
    
    collectd.register_read(read_func, INTERVAL)

def read_func():
    if len(SERVERS) == 0:
        command = "%s --json" % SPEEDTEST_BIN
        res = run_speedtest(command)
        update_collectd(res)

    else:
        for server in SERVERS:
            command = "sudo -u %s %s --server-id %d --format json" % (USER, SPEEDTEST_BIN, server)
            collectd.debug('%s cmd: %s' % (plugin_name, command))
            res = run_speedtest(command)
            update_collectd(res)

collectd.register_config(config_func)


def main():
     print("SPEEDTEST_BIN: " + SPEEDTEST_BIN)
     cmd = "%s --server-id %d --format json" % (SPEEDTEST_BIN, 3575)
     res = run_speedtest(cmd)
     pprint(res)


if __name__ == "__main__":
    main()

