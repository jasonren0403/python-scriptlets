import logging

import pymysql
import requests
from bs4 import BeautifulSoup

db = {
    "host": "localhost",
    "port": 3306,
    "user": "user",
    "password": "pass",
    "database": "db"
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

logger.info('Start crawling')
logger.info('[1] Getting web page')
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"}
req = requests.get(url='https://ncov.dxy.cn/ncovh5/view/pneumonia', headers=headers, verify=False)
req.encoding = req.apparent_encoding
# print(req.text)

soup = BeautifulSoup(req.text, 'html.parser')
final_data = {}

try:
    import json

    json_text = soup.find('script', {'id': 'getStatisticsService'}).get_text().replace(
        'try { window.getStatisticsService = ',
        '').replace('catch(e){}', '')
    json_text = json_text[:-1]
    # print(json_text)
    data_dict = json.loads(json_text)
    final_data['confirmed'] = int(data_dict['confirmedCount'])
    final_data['suspected'] = int(data_dict['suspectedCount'])
    final_data['cured'] = int(data_dict['curedCount'])
    final_data['dead'] = int(data_dict['deadCount'])
    final_data['last_since'] = data_dict['modifyTime']  # "modifyTime":1581260419000 ms!
except Exception as e:
    logger.error('error in data getting! quit')
    logger.error('current exception: %s' % e)
    logger.error('current data: %s' % req.text)
    quit(-1)
finally:
    logger.info(final_data.__repr__())
    logger.info('[2] Inserting data into database')
    global conn
    try:
        import datetime, time

        conn = pymysql.connect(
            host=db.get('host'),
            port=db.get('port'),
            user=db.get('user'),
            password=db.get('password'),
            database=db.get('database'),
        )
        logger.info('Connected to the database')
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute('select last_since from 2020_pneumonia order by last_since desc')
        ret = cur.fetchone()
        logger.info(ret)  # {'last_since': datetime.datetime(2020, 2, 9, 22, 55)}
        ret_time = ret.get('last_since')
        local_time = datetime.datetime.fromtimestamp(final_data['last_since'] / 1000)
        logger.debug("from database")
        logger.debug(ret_time)
        logger.debug("last_time in web page")
        logger.debug(local_time)
        if ret_time == local_time:
            logger.info("[*]No need to insert!")
        else:
            date_in = datetime.datetime.fromtimestamp(final_data['last_since'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            # print(date_in,type(date_in))
            proved = final_data['confirmed']
            uncertain = final_data['suspected']
            died = final_data['dead']
            cured = final_data['cured']
            sql = "insert into 2020_pneumonia values('%s',%d,%d,%d,%d);" % (date_in, proved, uncertain, died, cured)
            cur.execute(sql)
            conn.commit()
            logger.info("[√]Insert success!")
    finally:
        conn.close()
