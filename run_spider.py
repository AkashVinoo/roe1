from scrapy.crawler import CrawlerProcess
from spider import TDSSpider
import json

def run_spider():
    process = CrawlerProcess({
        'FEEDS': {
            'tds_content.jsonl': {
                'format': 'jsonlines',
                'encoding': 'utf8',
                'overwrite': True
            },
        },
    })
    
    # Run the spider
    process.crawl(TDSSpider)
    process.start()

if __name__ == "__main__":
    print("Starting the TDS course content spider...")
    run_spider()
    print("Spider finished. Data saved to tds_content.jsonl") 