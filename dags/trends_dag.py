from airflow.decorators import dag
from airflow.operators.python_operator import PythonOperator
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.python_operator import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago
from airflow import Dataset, DAG, task
from docker.types import Mount
from datetime import datetime, timedelta



"""
data
holder
"""

out_folder = "/data/trends/"
collect_folder = f"/data/trends_collects/"
dataset_path = f"/data/###/trends.txt"
dataset = Dataset(dataset_path)
COUNT_TRENDS = 9
    
"""
fetch
Trends
"""    
with DAG(
    dag_id="trends_fetch",
    catchup=False,
    start_date=days_ago(0), 
    schedule_interval=timedelta(minutes=10), 
    max_active_runs=1,
    tags=["trends", 'day'],
) as dag:
    
    
    
    def init_name():
        file_names = {}
        import datetime
        file_base = datetime.datetime.now().strftime('%Y-%m-%d-%H')
        import pathlib               
        file_names['txt'] = pathlib.PurePath(out_folder + file_base + ".txt").as_posix()
        file_names['src'] = pathlib.PurePath(out_folder + file_base + "_src.jpg").as_posix()
        file_names['pal'] = pathlib.PurePath(out_folder + file_base + "_pal.jpg").as_posix()
        file_names['col'] = pathlib.PurePath(out_folder + file_base + "_col.jpg").as_posix()
        file_names['som'] = pathlib.PurePath(out_folder + file_base + "_som.jpg").as_posix()
        file_names['spt'] = pathlib.PurePath(out_folder + file_base + ".jpg").as_posix()
        file_names['new'] = pathlib.PurePath(out_folder + "spot" + ".jpg").as_posix()
        return file_names
    
    task_init_names = PythonOperator(
        task_id='task_init_names',
        python_callable = init_name,
        dag=dag
    )
    
    
    
    def trends_fetch():
        current_url = "https://twitter-trends.iamrohit.in"
        response = requests.get(current_url, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
        all_tags = soup.findAll('a', class_='tweet')
        tags = []
        for tag in all_tags[0:COUNT_TRENDS]:
            tags.append(tag.text)
        tags.sort()
        return tags
    
    task_trends_fetch = PythonOperator(
        task_id='task_trends_fetch',
        python_callable = trends_fetch,
        dag=dag
    )
    




    def load_previous():
        tags = []
        try:
            with open(dataset_path, 'r') as f:
                tagsf = f.readlines()    
                for tag in tagsf:
                    tags.append(tag.strip())
            tags.sort()
        except:
            ...
        
        return tags

    task_load_previous = PythonOperator(
        task_id='task_load_previous',
        python_callable = load_previous,
        dag=dag
    )
    




    def compare_hashtags(ti, **kwargs):
        current_hashtags = ti.xcom_pull(task_ids='task_trends_fetch')
        current_hashtags.sort()
        current_set = set(current_hashtags)
        previous_hashtags = ti.xcom_pull(task_ids='task_load_previous')
        previous_hashtags.sort()
        previous_set = set(previous_hashtags)
        new_hashtags = current_set - previous_set
        removed_hashtags = previous_set - current_set
        return {"new": list(new_hashtags), "removed": list(removed_hashtags)}
    
    task_compare_hashtags = PythonOperator(
        task_id='task_compare_hashtags',
        python_callable=compare_hashtags,
        provide_context=True,
        dag=dag
    )
    




    def save_new(ti, **kwargs):
        tags = ti.xcom_pull(task_ids='task_trends_fetch')
        with open(dataset_path, 'w') as f:
            f.write('\n'.join(tags))
                    
        filenames = ti.xcom_pull(task_ids='task_init_names')
        filename_txt = filenames['txt']           
        with open(filename_txt, 'w') as f:
            f.write('\n'.join(tags))     
        

    task_save_new = PythonOperator(
        task_id='task_save_new',
        python_callable = save_new,
        provide_context=True,
        dag=dag
    )




    def download_images(ti, **kwargs):
        tags = ti.xcom_pull(task_ids='task_trends_fetch')
        for tag in tags:
            tag_folder = f"{collect_folder}{tag}"
            print(f"check download {tag} {tag_folder}")
            try:
                from bing_image_downloader import downloader
                downloader.download(tag, limit=2,  output_dir=collect_folder, adult_filter_off=False, force_replace=True, timeout=1, verbose=False)
            except:
                ...

    task_download_images = PythonOperator(
        task_id='task_download_images',
        python_callable = download_images,
        provide_context=True,
        dag=dag
    )






    def make_collage(ti, **kwargs):
        tags = ti.xcom_pull(task_ids='task_trends_fetch')
        from PIL import Image, ImageFilter, ImageFile
        import math    
        filenames = ti.xcom_pull(task_ids='task_init_names')
        filename_collage = filenames['src']
        side_count = math.ceil(math.sqrt(len(tags)))
        if not tags:
            print('No images for making collage! Please select other directory with images!')
        else:
            w = int(1024/side_count)
            h = int(1024/side_count)
            size = int(w/side_count)
            collage_image = Image.new('RGB', (w, h), (35, 35, 35))
            
            latest_image = None
            
            for i, tag in enumerate(tags[0:side_count*side_count]): 
                img_path = f"{collect_folder}{tag}/Image_1.jpg"
                img = None
                
                try:
                    img = Image.open(img_path)
                    s = 113
                    img = img.resize(size=(s, s)).convert('RGB')
                    latest_image = img
                    img.save(img_path, "JPEG")
                except Exception:    
                    img = latest_image

                if img != None:                         
                    collage_image.paste(img, ((i % side_count) * size, int(i / side_count) * size))    
                    
            collage_image.save(filename_collage)
            
            
            
            from som import get_som, get_colours, plot_colors2            
            
            rgb_colours, hex_colors, colors = get_colours(filename_collage, 8, True, filenames['pal'])
            rgb_colours = rgb_colours[0:7]
 
            bar = plot_colors2(rgb_colours)
            img = Image.fromarray(bar, 'RGB')
            img.save(filenames['col'])

            import numpy as np
            np_colors = np.array(rgb_colours)
            raw_data_test = np_colors.T

            get_som(raw_data_test, 1000, filenames['som'], 16)

            srciImage = Image.open(filenames['som'])
            gaussImage = srciImage.filter(ImageFilter.GaussianBlur(32))
            gaussImage.save(filenames['spt'])
            gaussImage.save(filenames['new'])
        
        
            # get_som(collage_image, 1000, filenames['spt'], 16)
            # from PIL import Image, ImageFilter
            # blurred_image = collage_image.filter(ImageFilter.BoxBlur(radius=2))
            # blurred_image.save(filenames['spt'])            
            # blurred_image.save(filenames['new'])
            # print(f'saved {filenames['spt']}')
            # img = Image.open(filenames['spt'])
            # img.save(filenames['new'])
            return filenames['spt']
            

    task_make_collages = PythonOperator(
        task_id='task_make_collages',
        python_callable = make_collage,
        provide_context=True,
        dag=dag
    )
    
    
    
    task_init_names >> task_trends_fetch >> task_load_previous >> task_compare_hashtags >> task_save_new >> task_download_images >> task_make_collages