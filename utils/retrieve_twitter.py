import click
import logging
import sys
import urllib.request
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime

def retrieve_tags():
    current_url = "https://twitter-trends.iamrohit.in"
    response = requests.get(current_url, timeout=5)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    all_tags = soup.findAll('a', class_='tweet')
    tags = []
    for tag in all_tags:
        tags.append(tag.text)
    return tags


@click.command()
# @click.argument("video_dir")
# @click.argument("output_dir")
# @click.option("--video_pipeline_config", default='./configs/video_pipeline.yml')
# @click.option("--osc_config", default='./configs/osc_config.yml')
# @click.option("--save_outputs", is_flag=True)
# @click.option("--save_video", is_flag=True)
def retrieve_twitter(**kwargs) -> None:
    logging.info("init app...")
    tags = retrieve_tags()
    #logging.info(tags)
    formatted = "\n".join(tags)

    now = datetime.now()
    # date_time = now.strftime("../%Y-%m-%d_%H-%M-%S")
    date_time = now.strftime("%Y-%m-%d-%H")
    filename = f"./data/{date_time}_tags.txt"
    with open(filename, "w", encoding="utf-8") as text_file:
        text_file.write(formatted)
    logging.info(f"saved to {filename}")


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        handlers=[
                            logging.FileHandler("./data/app.log"),
                            logging.StreamHandler(sys.stdout)
                        ],
                        # filemode='a',
                        encoding='utf-8',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    retrieve_twitter()