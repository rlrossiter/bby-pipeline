import datetime
import json
import logging

import azure.functions as func
from scraper_pipeline.fanout import bestbuy_sku_to_url_fanout


def main(timer: func.TimerRequest, skusblob: str):
    skus = json.loads(skusblob)
    fanout = bestbuy_sku_to_url_fanout.BestBuySkuFanout(skus)

    scrapes = fanout.fanout()

    return json.dumps([s._asdict() for s in scrapes])