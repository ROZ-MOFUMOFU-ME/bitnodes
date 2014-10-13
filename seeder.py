#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# seeder.py - Exports reachable nodes into a DNS zone file for DNS seeder.
#
# Copyright (c) 2014 Addy Yeow Chin Heng <ayeowch@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Exports reachable nodes into a DNS zone file for DNS seeder.
"""

import glob
import json
import logging
import operator
import os
import random
import redis
import sys
import time
from ConfigParser import ConfigParser

from protocol import DEFAULT_PORT

# Redis connection setup
REDIS_SOCKET = os.environ.get('REDIS_SOCKET', "/tmp/redis.sock")
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
REDIS_CONN = redis.StrictRedis(unix_socket_path=REDIS_SOCKET,
                               password=REDIS_PASSWORD)

SETTINGS = {}


def export_nodes(nodes):
    """
    Exports nodes as A and AAAA records. Nodes are selected from oldest
    (longest uptime) to newest each with unique AS number.
    """
    nodes = sorted(nodes, key=operator.itemgetter(4))[:SETTINGS['nodes']]
    min_height = REDIS_CONN.get('height')
    if min_height is None:
        min_height = SETTINGS['min_height']
    else:
        min_height = int(min_height)
    min_age = SETTINGS['min_age']
    now = int(time.time())
    logging.info("Min. height: {}".format(min_height))
    oldest = now - min(nodes, key=operator.itemgetter(4))[4]
    if oldest < min_age:
        min_age = oldest - (0.01 * oldest)  # Max. 1% newer than oldest
    logging.info("Min. age: {}".format(min_age))
    asns = []
    a_records = []
    aaaa_records = []
    for node in nodes:
        address = node[0]
        port = node[1]
        age = now - node[4]
        height = node[5]
        asn = node[12]
        if (port == DEFAULT_PORT and asn not in asns and
                age >= min_age and height >= min_height):
            if ":" in address:
                aaaa_records.append("@\tIN\tAAAA\t{}".format(address))
            else:
                a_records.append("@\tIN\tA\t{}".format(address))
            asns.append(asn)
    return (a_records, aaaa_records)


def save_zone_file(a_records, aaaa_records):
    """
    Saves A and AAAA records in DNS zone file.
    """
    random.shuffle(a_records)
    random.shuffle(aaaa_records)
    logging.info("A records: {}".format(len(a_records)))
    logging.info("AAAA records: {}".format(len(aaaa_records)))
    a_records = "\n".join(a_records[:SETTINGS['a_records']]) + "\n"
    aaaa_records = "\n".join(aaaa_records[:SETTINGS['aaaa_records']]) + "\n"
    template = open(SETTINGS['template'], "r").read()
    serial = str(int(time.time()))
    logging.debug("Serial: {}".format(serial))
    template = template.replace("1413235952", serial)
    open(SETTINGS['zone_file'], "w").write(template + a_records + aaaa_records)


def cron():
    """
    Periodically fetches latest snapshot to sample nodes for DNS zone file.
    """
    while True:
        time.sleep(5)
        dump = max(glob.iglob("{}/*.json".format(SETTINGS['export_dir'])))
        logging.info("Dump: {}".format(dump))
        nodes = []
        try:
            nodes = json.loads(open(dump, "r").read(), encoding="latin-1")
        except ValueError:
            logging.warning("Write pending")
        if len(nodes) > 0:
            (a_records, aaaa_records) = export_nodes(nodes)
            if len(a_records) > 0 and len(aaaa_records) > 0:
                save_zone_file(a_records, aaaa_records)


def init_settings(argv):
    """
    Populates SETTINGS with key-value pairs from configuration file.
    """
    conf = ConfigParser()
    conf.read(argv[1])
    SETTINGS['logfile'] = conf.get('seeder', 'logfile')
    SETTINGS['debug'] = conf.getboolean('seeder', 'debug')
    SETTINGS['export_dir'] = conf.get('seeder', 'export_dir')
    SETTINGS['nodes'] = conf.getint('seeder', 'nodes')
    SETTINGS['min_height'] = conf.getint('seeder', 'min_height')
    SETTINGS['min_age'] = conf.getint('seeder', 'min_age')
    SETTINGS['zone_file'] = conf.get('seeder', 'zone_file')
    SETTINGS['template'] = conf.get('seeder', 'template')
    SETTINGS['a_records'] = conf.getint('seeder', 'a_records')
    SETTINGS['aaaa_records'] = conf.getint('seeder', 'aaaa_records')


def main(argv):
    if len(argv) < 2 or not os.path.exists(argv[1]):
        print("Usage: seeder.py [config]")
        return 1

    # Initialize global settings
    init_settings(argv)

    # Initialize logger
    loglevel = logging.INFO
    if SETTINGS['debug']:
        loglevel = logging.DEBUG

    logformat = ("%(asctime)s,%(msecs)05.1f %(levelname)s (%(funcName)s) "
                 "%(message)s")
    logging.basicConfig(level=loglevel,
                        format=logformat,
                        filename=SETTINGS['logfile'],
                        filemode='w')
    print("Writing output to {}, press CTRL+C to terminate..".format(
          SETTINGS['logfile']))

    cron()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
