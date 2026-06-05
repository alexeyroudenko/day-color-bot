query_string = "Party"

# from bing_image_downloader import downloader
# downloader.download(query_string, limit=25,  output_dir='dataset', adult_filter_off=True, force_replace=False, timeout=60, verbose=True)

from better_bing_image_downloader import downloader
downloader(query_string, limit=100, output_dir='dataset', adult_filter_off=True, force_replace=True, timeout=60, filter="", verbose=True, badsites= [], name='Image')