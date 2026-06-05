import io
import pandas as pd
import requests
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from bs4 import BeautifulSoup



@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    url = 'https://twitter-trends.iamrohit.in'
    response = requests.get(url, timeout=5)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    all_tags = soup.findAll('a', class_='tweet')
    tags = []
    COUNT_TRENDS = 9
    for tag in all_tags[0:COUNT_TRENDS]:
        tags.append(tag.text)
    tags.sort()
    return pd.read_csv(io.StringIO(",".join(tags)), sep=',')


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
