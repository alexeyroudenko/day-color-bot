from airflow.decorators import dag
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta
from airflow.models import Variable
from airflow.datasets import Dataset
from airflow.models.dag import DAG
from airflow.models.param import Param
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import pendulum


import logging
logger = logging.getLogger(__name__)


# {os.getcwd()}/data/out

"""
data
holder
"""
collects_folder = "/data/words_collects/"
out_folder = "/data/words/"

tmp_folder = "/tmp/"
out_data_path = f"{tmp_folder}word.txt"
dataset = Dataset(out_data_path)





"""
TODO: make it work
submit words
"""
with DAG (
    dag_id="submit_words",
    catchup=False,
    start_date=days_ago(0), 
    schedule_interval=None, 
    tags=["words"],
    params={
        "words":["1","2","3"]
    },
) as dag_words:
    
    def submit_words(**kwargs):
        words = kwargs['dag_run'].conf['words']
        word = words[0]
        return word
        # with open(out_data_path, "w") as file:
        #         file.write(f"{word}")

    task_submit_words = PythonOperator(
        task_id='submit_words',
        python_callable = submit_words,
        outlets=[dataset],
        dag=dag_words
    )
    
    task_sensor = ExternalTaskSensor(
      task_id="sensor",
      external_dag_id="collect_word",
      external_task_id="task_make_collages",
    )
    
    task_trigger = TriggerDagRunOperator(
        task_id="trigger",
        trigger_dag_id="collect_word",
        conf={"word":dag_words.params['words'][0]},
    )
    
    task_submit_words >> task_trigger >> task_sensor
    




"""

data writin
"""
def receive_word(**kwargs):
    word = kwargs['dag_run'].conf['word']
    with open(out_data_path, "w") as file:
            file.write(f"{word}")

with DAG(
    dag_id="receive_word",
    catchup=False,
    start_date=days_ago(0), 
    schedule_interval=None, 
    tags=["word", "produces"],
    params={
        "word": "42",
        "word_action": "add"
    },
) as dag1:
    # [START task_outlet]
    task_chaos_start = PythonOperator(
        task_id='producer',
        python_callable = receive_word,
        outlets=[dataset]
    )    
    # [END task_outlet]



"""

data reading
"""
with DAG(
    dag_id="collect_word",
    catchup=False,
    start_date=days_ago(0), 
    schedule=[dataset],
    max_active_runs=1,
    tags=["word", "consume"],
) as dag2:

    def collect_word():
        logger.info(f"consume_data from {out_data_path}")
        word = []    
        with open(out_data_path, 'r') as f:
            word = f.read()
            word = word.strip()
        
        from bing_image_downloader import downloader
        downloader.download(word, limit=16,  
                            output_dir=collects_folder, 
                            adult_filter_off=False, 
                            force_replace=True, 
                            timeout=1, 
                            verbose=False)
        
        logger.info(f"consume_data word {word}")
        import glob
        rimages = []
        for img in glob.glob(f"{collects_folder}{word}/*"):
            filename = img.replace("#","%23")
            #tag = str(img).split("/")[2]
            #tag = str(tag)[:-4]
            rimages.append({"filename":filename, "tag":word}) #quote            
        return rimages

    
    # [START task_outlet]
    task_collect_word = PythonOperator(
        task_id='task_collect_word',
        python_callable = collect_word,
        dag=dag2    
    )    
    # [END task_outlet]
    
    
    
    def make_collage(ti, **kwargs):
        rimages = ti.xcom_pull(task_ids='task_collect_word')       
        file_base = "word"
        from PIL import Image, ImageFilter, ImageFile
        import math    
        # filenames = ti.xcom_pull(task_ids='task_init_names')
        # filename_collage = filenames['filename']
        side_count = math.ceil(math.sqrt(len(rimages)))
        if not rimages:
            print('No images for making collage! Please select other directory with images!')
        else:
            w = int(1024/side_count)
            h = int(1024/side_count)
            size = int(w/side_count)
            collage_image = Image.new('RGB', (w, h), (35, 35, 35))
            for i, img_data in enumerate(rimages[0:side_count*side_count]):                
                img_path = img_data['filename']
                word = img_data['tag']
                try:
                    img = Image.open(img_path)                    
                    # img.thumbnail((w,h))
                    s = 113
                    img = img.resize(size=(s, s)).convert('RGB')
                    img.save(img_path, "JPEG")
                    collage_image.paste(img, ((i % side_count) * size, int(i / side_count) * size))    
                    file_base = word
                

                except:
                    
                    ...
            
            import pathlib
            file_names = {}
            file_names['txt'] = pathlib.PurePath(out_folder + file_base + ".txt").as_posix()
            file_names['src'] = pathlib.PurePath(out_folder + file_base + "_src.jpg").as_posix()
            file_names['pal'] = pathlib.PurePath(out_folder + file_base + "_pal.jpg").as_posix()
            file_names['col'] = pathlib.PurePath(out_folder + file_base + "_col.jpg").as_posix()
            file_names['som'] = pathlib.PurePath(out_folder + file_base + "_som.jpg").as_posix()
            file_names['spt'] = pathlib.PurePath(out_folder + file_base + ".jpg").as_posix()
            
            collage_image.save(file_names['src'])

            from som import get_som            
            from som import get_colours
            import numpy as np 
            
            rgb_colours, hex_colors, colors = get_colours(file_names['src'], 10, True, file_names['pal'])
            rgb_colours = rgb_colours[0:7]
    
            np_colors = np.array(rgb_colours)
            raw_data_test = np_colors.T
            get_som(raw_data_test, 1000, file_names['som'], 16)
            
            from PIL import Image, ImageFilter
            srciImage = Image.open(file_names['som'])
            gaussImage = srciImage.filter(ImageFilter.GaussianBlur(32))
            gaussImage.save(file_names['spt'])

            return file_names['spt']
            

    task_make_collages = PythonOperator(
        task_id='task_make_collages',
        python_callable = make_collage,
        provide_context=True,
        dag=dag2
    )
    
    task_collect_word >> task_make_collages 


