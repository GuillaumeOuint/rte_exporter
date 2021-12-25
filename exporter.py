#!/usr/bin/env python
# coding=utf-8
import datetime
import logging
import os 
import requests
import time
import traceback
from prometheus_client import start_http_server, Summary, Gauge

URL = "https://opendata.reseaux-energies.fr/api/records/1.0/search/"
# Env Variables
EXPORTER_PORT = int(os.environ.get('EXPORTER_PORT', 9143))
RUN_INTERVAL = int(os.environ.get('RUN_INTERVAL', 180))

pgauge = {}

def isnt_float(value):
  try:
    float(value)
    return False
  except:
    return True
def isnt_int(value):
  try:
    int(value)
    return False
  except:
    return True
def get_api():
    now = datetime.datetime.utcnow()
    params={
        "dataset": "eco2mix-national-tr",
        "q": "date_heure:[2021-11-03T{}:{}:00Z TO 2021-11-03T{}:{}:00Z]".format(now.hour - 1,now.minute, now.hour,now.minute),
        "sort": "-date_heure",
        "facet": ["nature", "date_heure"],
        "timezone": "Europe/Paris",
        "rows": 100
    }
    res = requests.get(URL, params=params).json()
    return res
    
def update_metrics():
    res = get_api()
    record = {}
    for drd in res["records"]:
        for field in drd["fields"]:
            record[field] = drd["fields"][field]
    for field in record:
        if isnt_float(record[field]) and isnt_int(record[field]) : continue
        if not field in pgauge:
            pgauge[field] = Gauge("rte_"+field, field)
        pgauge[field].set(record[field])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_http_server(EXPORTER_PORT)
    while True:
        try:
            update_metrics()
        except Exception as e:
            print(traceback.format_exc())
        time.sleep(RUN_INTERVAL)