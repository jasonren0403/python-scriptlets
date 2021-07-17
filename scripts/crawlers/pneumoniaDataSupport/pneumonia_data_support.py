#! /usr/bin/python3
# pip install cryptography

import logging

import pymysql
import requests
from bs4 import BeautifulSoup

db = {
    "host": "localhost",
    "port": 3306,
    "user": "user",
    "password": "pass",
    "database": "web"
}

table = "2020_pneumonia"

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"}

URL = "https://ncov.dxy.cn/ncovh5/view/pneumonia"

logging_config = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}


class DataSupport:
    def __init__(self):
        logging.basicConfig(**logging_config)
        logging.captureWarnings(True)
        self.logger = logging.getLogger("data_support_pneumonia")
        self.logger.info(f"debug level:{logging.getLevelName(logging_config.get('level') or logging.INFO)}")
        self.final_data = self.webPage()
        if self.final_data:
            try:
                self.conn = pymysql.connect(
                    host=db.get('host'),
                    port=db.get('port'),
                    user=db.get('user'),
                    password=db.get('password'),
                    database=db.get('database'),
                )
                self.logger.info('Connected to the database')
                if not self.checkDBschema():
                    self.newTable()
                self.dataInsert()
            except pymysql.err.OperationalError as e:
                self.logger.error(e)
                self.logger.error("Connect failed")
                quit(-1)
        else:
            self.conn = None
            self.logger.warning("Empty final data get! retry later~")

    def checkDBschema(self):
        try:
            cur = self.conn.cursor(pymysql.cursors.DictCursor)
            cur.execute("show tables")
            d = cur.fetchall()
            self.logger.debug(f"{d}")
            list_tables = [i.get('Tables_in_web', '') for i in d if d is not None]
            return table in list_tables or False
        except pymysql.err.OperationalError as e:
            self.logger.warning("schema may not exist")
            self.logger.warning(e)
            return False

    def newTable(self):
        self.logger.info("No table detected, creating a new one...")
        try:
            cur = self.conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(f"create table {table} (last_since datetime null,"
                        f"proved int null,"
                        f"uncertain int null,"
                        f"died int null,"
                        f"cured int null);")
            return True
        except pymysql.err.OperationalError as e:
            self.logger.warning(e)
            return False

    def webPage(self):
        self.logger.info('Start crawling')
        self.logger.info('[1] Getting web page')
        req = requests.get(url=URL, headers=headers, verify=False)
        req.encoding = req.apparent_encoding
        soup = BeautifulSoup(req.text, 'html.parser')
        final_data = {}
        import json
        json_text = soup.find(name='script', attrs={'id': 'getStatisticsService'}).string
        json_text = json_text.replace('try { window.getStatisticsService = ', '').replace('catch(e){}', '')
        json_text = json_text[:-1]  # strip last '}'
        # print(json_text)
        try:
            data_dict = json.loads(json_text)
            final_data['confirmed'] = int(data_dict['confirmedCount'])
            final_data['suspected'] = int(data_dict['suspectedCount'])
            final_data['cured'] = int(data_dict['curedCount'])
            final_data['dead'] = int(data_dict['deadCount'])
            final_data['last_since'] = data_dict['modifyTime']  # "modifyTime":1581260419000 ms!
        except Exception as e:
            self.logger.error('error in data getting! quit')
            self.logger.error('current exception: %s' % e)
            self.logger.debug('current data: %s' % req.text)
            quit(-1)
        finally:
            self.logger.info(f"final data:{final_data.__repr__()}")
            return final_data

    def dataInsert(self):
        self.logger.info('[2] Inserting data into database')
        try:
            import datetime, time
            cur = self.conn.cursor(pymysql.cursors.DictCursor)
            cur.execute('select last_since from 2020_pneumonia order by last_since desc')
            ret = cur.fetchone()
            self.logger.info(f"ret:{ret}")  # {'last_since': datetime.datetime(2020, 2, 9, 22, 55)}
            if ret:
                # compare first
                ret_time = ret.get('last_since')
                local_time = datetime.datetime.fromtimestamp(self.final_data['last_since'] / 1000)
                self.logger.debug("from database")
                self.logger.debug(ret_time)
                self.logger.debug("last_time in web page")
                self.logger.debug(local_time)
                if ret_time == local_time:
                    self.logger.info("[*] No need to insert!")
                    quit(-1)
            date_in = datetime.datetime.fromtimestamp(self.final_data['last_since'] / 1000).strftime(
                "%Y-%m-%d %H:%M:%S")
            # print(date_in,type(date_in))
            proved = self.final_data['confirmed']
            uncertain = self.final_data['suspected']
            died = self.final_data['dead']
            cured = self.final_data['cured']
            sql = "insert into 2020_pneumonia values('%s',%d,%d,%d,%d);" % (date_in, proved, uncertain, died, cured)
            cur.execute(sql)
            self.conn.commit()
            self.logger.info("[鈭歖 Insert success!")
        except Exception as e:
            self.logger.warning(e)

    def __del__(self):
        self.logger.info("[*] execute success!")
        if hasattr(self, "conn") and isinstance(self.conn, pymysql.Connection):
            self.conn.close()


if __name__ == '__main__':
    DataSupport()
