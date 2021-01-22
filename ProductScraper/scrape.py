import json

import azure.functions as func
from scraper_pipeline.models import scrape
from scraper_pipeline.scrape.plugin import best_buy_processor
from scraper_pipeline.scrape import scraper

def main(msg: func.ServiceBusMessage):
    scrape_json = msg.get_body().decode('utf-8')
    scrape_obj = scrape.Scrape(**json.loads(scrape_json))

    proc = best_buy_processor.BestBuyProcessor()
    scrpr = scraper.Scraper()
    
    status = scrpr.scrape(scrape_obj, proc)

    # Clear out any possible null values
    return json.dumps({k: v for k, v in status._asdict().items() if v})