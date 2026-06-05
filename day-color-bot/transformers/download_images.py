from mage_ai.data_cleaner.transformer_actions.base import BaseAction
from mage_ai.data_cleaner.transformer_actions.constants import ActionType, Axis
from mage_ai.data_cleaner.transformer_actions.utils import build_transformer_action
from pandas import DataFrame

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import requests
from bs4 import BeautifulSoup
import os


import requests
from bs4 import BeautifulSoup
import os

def download_yandex_image(search_keyword, output_path="downloaded_image.jpg"):
    out_folder = "./data/tags/"
    os.makedirs(out_folder, exist_ok=True)  # Создаем папку, если не существует

    # Формируем URL для поиска изображений в Яндекс
    search_url = f"https://yandex.ru/images/search?text={search_keyword.replace(' ', '+')}"
    
    # Заголовки для имитации браузера
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Search URL: {search_url}")
    
    try:
        # Отправляем запрос
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # Парсим HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Находим изображения (в Яндексе изображения часто в теге img с классом serp-item__thumb)
        image_tags = soup.find_all("img", {"class": "serp-item__thumb"})

        if not image_tags:
            raise Exception("Изображения не найдены")

        for image_tag in image_tags:
            image_url = image_tag.get("src")
            if not image_url:
                continue
                
            print(f"Image URL: {image_url}")

            # Яндекс часто использует относительные URL
            if not image_url.startswith("http"):
                image_url = "https:" + image_url

            try:
                # Скачиваем изображение
                image_response = requests.get(image_url, headers=headers)
                image_response.raise_for_status()

                # Сохраняем изображение
                full_path = os.path.join(out_folder, output_path)
                with open(full_path, "wb") as f:
                    f.write(image_response.content)
                print(f"Image saved to: {full_path}")
                return full_path

            except requests.RequestException as e:
                print(f"Ошибка при скачивании изображения: {e}")
                continue

        raise Exception("Не удалось скачать ни одно изображение")

    except requests.RequestException as e:
        print(f"Ошибка при запросе к Яндексу: {e}")
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def download_bing_image(search_keyword, output_path="downloaded_image.jpg"):
    out_folder = "./data/tags/"

    # Формируем URL для поиска изображений в Bing
    search_url = f"https://www.bing.com/images/search?q={search_keyword.replace(' ', '+')}"
    
    # Заголовки для имитации браузера
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(search_url)
    
    # Отправляем запрос
    response = requests.get(search_url, headers=headers)
    response.raise_for_status()
    
    # Парсим HTML
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Находим первое изображение (тег <img> с классом, связанным с результатами поиска)
    image_tags = soup.find_all("img", {"class": "mimg"})

    is_downloaded = False

    for image_tag in image_tags:

        # if not image_tag or not image_tag.get("src"):
            # raise Exception("Изображение не найдено")
        
        # Получаем URL изображения
        image_url = image_tag["src"]
        print(f"image_url: {image_url}")

        if not image_url.startswith("http"):
            image_url = "https:" + image_url
        else:
            # Скачиваем изображение
            image_response = requests.get(image_url, headers=headers)
            image_response.raise_for_status()

            # Сохраняем изображение
            with open(out_folder+output_path, "wb") as f:
                f.write(image_response.content)
                return f"{out_folder}{output_path}"
                is_downloaded = True

            if is_downloaded == True:
                break
        
    
    return f"{out_folder}{output_path}"



@transformer
def execute_transformer_action(df: DataFrame, *args, **kwargs) -> DataFrame:
    """
    Execute Transformer Action: ActionType.FILTER

    Docs: https://docs.mage.ai/guides/transformer-blocks#filter
    """
    action = build_transformer_action(
        df,
        action_type=ActionType.FILTER,
        axis=Axis.ROW,
        action_code='',  # Specify your filtering code here
    )
    downloadeds = []
    for tag in df:
        # print(f"need dowbnload for {tag}")
        downloaded = download_yandex_image(tag, f"{tag}.jpg")
        downloadeds.append(downloaded)

    return downloadeds, BaseAction(action).execute(df) 


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
