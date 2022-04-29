import logging
import pathlib
import re
import time

import cfscrape
import requests
import urllib3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

urllib3.disable_warnings()

PIC_PATH = pathlib.PurePath(__file__).parent / 'pics'
s = requests.session()


def get_urllist(limit=15, _type=None):
    _list = []
    url = "https://konachan.com/post.json"  # type limit

    scraper = cfscrape.create_scraper(s)
    if _type is None:
        data = scraper.get(url, params={"limit": limit})
    else:
        data = scraper.get(url, params={"limit": limit, "type": _type})
    data = data.json()
    log.info(data)
    for d in data:
        _list.append(d["file_url"])
    log.info(_list)
    return _list


def save_pics(pic_list=None, root_path=PIC_PATH):
    has_error = False
    if pic_list is None:
        log.info('No pic available! ')
        return False
    else:
        total = len(pic_list)
        cur_num = 0
        for picurl in pic_list:
            cur_num += 1
            filename = picurl.split('/')[-1]
            filename = re.sub(r'%20', '_', filename)
            scraper = cfscrape.create_scraper(s)
            filename.replace('%28', '(').replace('%29', ')')
            log.info('getting %s' % filename)
            data = scraper.get(url=picurl, stream=True)
            if data.status_code == 200:
                with open(root_path / filename, "wb") as file:
                    length = float(data.headers['content-length'])
                    count = 0
                    count_tmp = 0
                    time1 = time.time()
                    for chunk in data.iter_content(chunk_size=512):
                        if chunk:
                            file.write(chunk)
                            count += len(chunk)
                            if time.time() - time1 > 2:
                                p = count / length * 100
                                speed = (count - count_tmp) / 1024 / 1024 / 2
                                count_tmp = count
                                log.info(
                                    '[' + str(cur_num) + '/' + str(total) + '] ' + filename + ': ' + formatFloat(
                                        p) + '%' + ' Speed: ' + formatFloat(speed) + 'M/S')
                                time1 = time.time()
                    log.info('%s downloaded successfully' % filename)
            else:
                log.error('Error in downloading %s, status code %d. ' % (filename, data.status_code))
                has_error = True
        if not has_error:
            log.info('All pictures downloaded successfully.')
        return True


def formatFloat(num):
    return '{:.2f}'.format(num)


if __name__ == '__main__':
    # print(PIC_PATH)
    save_pics(get_urllist(_type='hololive aqua'))
