#!/bin/bash
# --- bitzeny mainnet: daa5bef9 (db = 0) ---
/usr/bin/nice -n 19 python -u crawl.py conf/crawl.daa5bef9.conf master > log/crawl.daa5bef9.master.out 2>&1 &
/usr/bin/nice -n 19 python -u crawl.py conf/crawl.daa5bef9.conf slave > log/crawl.daa5bef9.slave.1.out 2>&1 &
/usr/bin/nice -n 19 python -u crawl.py conf/crawl.daa5bef9.conf slave > log/crawl.daa5bef9.slave.2.out 2>&1 &

/usr/bin/nice -n 19 python -u ping.py conf/ping.daa5bef9.conf master > log/ping.daa5bef9.master.out 2>&1 &
/usr/bin/nice -n 19 python -u ping.py conf/ping.daa5bef9.conf slave > log/ping.daa5bef9.slave.1.out 2>&1 &
/usr/bin/nice -n 19 python -u ping.py conf/ping.daa5bef9.conf slave > log/ping.daa5bef9.slave.2.out 2>&1 &
/usr/bin/nice -n 19 python -u ping.py conf/ping.daa5bef9.conf slave > log/ping.daa5bef9.slave.3.out 2>&1 &
/usr/bin/nice -n 19 python -u ping.py conf/ping.daa5bef9.conf slave > log/ping.daa5bef9.slave.4.out 2>&1 &
/usr/bin/nice -n 19 python -u ping.py conf/ping.daa5bef9.conf slave > log/ping.daa5bef9.slave.5.out 2>&1 &
/usr/bin/nice -n 19 python -u ping.py conf/ping.daa5bef9.conf slave > log/ping.daa5bef9.slave.6.out 2>&1 &

/usr/bin/nice -n 19 python -u resolve.py conf/resolve.daa5bef9.conf > log/resolve.daa5bef9.out 2>&1 &

/usr/bin/nice -n 19 python -u export.py conf/export.daa5bef9.conf > log/export.daa5bef9.out 2>&1 &

/usr/bin/nice -n 19 python -u seeder.py conf/seeder.daa5bef9.conf > log/seeder.daa5bef9.out 2>&1 &

/usr/bin/nice -n 19 python -u pcap.py conf/pcap.daa5bef9.conf > log/pcap.daa5bef9.1.out 2>&1 &
/usr/bin/nice -n 19 python -u pcap.py conf/pcap.daa5bef9.conf > log/pcap.daa5bef9.2.out 2>&1 &
/usr/bin/nice -n 19 python -u pcap.py conf/pcap.daa5bef9.conf > log/pcap.daa5bef9.3.out 2>&1 &
