from pathlib import Path
import os
import sys
import urllib.request
import urllib
import imghdr
import posixpath
import re
import logging, sys


class Bing:
    def __init__(self, query, limit, output_dir, adult, timeout, filters=''):
        self.download_count = 0
        self.query = query
        self.output_dir = output_dir
        self.adult = adult
        self.filters = filters

        assert type(limit) == int, "limit must be integer"
        self.limit = limit
        assert type(timeout) == int, "timeout must be integer"
        self.timeout = timeout

        # self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
            'AppleWebKit/537.11 (KHTML, like Gecko) '
            'Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
                
        self.page_counter = 0

    def save_image(self, link, file_path):
        request = urllib.request.Request(link, None, self.headers)
        image = urllib.request.urlopen(request, timeout=self.timeout).read()
        if not imghdr.what(None, image):
            logging.error('[Error]Invalid image, not saving {}'.format(link))
            raise
        with open(file_path, 'wb') as f:
            f.write(image)



    def download_image(self, link, targetFilename):
        self.download_count += 1
        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split('?')[0]
            file_type = filename.split(".")[-1]

            if (file_type.lower() == "gif" or file_type.lower() == "png"):
                self.download_count -= 1
                return

            if file_type.lower() not in ["jpe", "jpeg", "jfif", "exif", "png", "jpg", "gif"]:
                file_type = "jpg"

            # Download the image
            logging.info("[%] Downloading Image #{} from {} to {}".format(self.download_count, link, targetFilename))
            self.save_image(link, "{}/{}/".format(os.getcwd(), self.output_dir) + targetFilename + "." + file_type)
            logging.info("[%] File Downloaded !")

        except Exception as e:
            self.download_count -= 1
            logging.error("[!] Issue getting: {}\n[!] Error:: {}".format(link, e))

    def run(self):
        while (self.download_count < self.limit) & (self.page_counter < 100):
            logging.info('[%] Indexing page: {}'.format(self.page_counter + 1))
                        
            from yandex import get_yandex_img_urls        
            urls = get_yandex_img_urls(urllib.parse.quote_plus(self.query))
            
            print(f"query:{self.query} - url:{urls}")

            # Parse the page source and download pics
            # request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(self.query) \
            #               + '&first=' + str(self.page_counter*self.limit) + '&count=' + str(self.limit) \
            #               + '&adlt=' + self.adult + '&qft=' + self.filters
            # logging.warn('[%] request_url: {}'.format(request_url))
            # request = urllib.request.Request(request_url, None, headers=self.headers)
            # response = urllib.request.urlopen(request)
            # html = response.read().decode('utf8')
            # links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
            # # logging.info(f"{html}")
            # logging.info("[%] Indexed {} Images on Page {}.".format(len(links), self.page_counter + 1))
            #print("===============================================")

            for link in urls:
                if self.download_count < self.limit:
                    import cyrtranslit
                    fname= "img_{}_{}.{}".format(cyrtranslit.to_latin(self.query, "ru"), self.page_counter, self.download_count)
                    self.download_image(link, fname)
                else:
                    logging.info("[%] Done. Downloaded {} images.".format(self.download_count))
                    #print("===============================================")
                    break

            self.page_counter += 1
        return self.download_count
