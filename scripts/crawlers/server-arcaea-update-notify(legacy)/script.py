import configparser
import logging
import re
import smtplib
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from requests.packages import urllib3

requests.packages.urllib3.disable_warnings()
config = configparser.ConfigParser()
config.read('.localver', encoding='UTF-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def upload_to_cloud(conf: dict):
    global config
    logger = logging.getLogger("com.mgc.uploadapk")
    logger.info(f'Performing cloud update from {conf}')
    secret_id = config.get(section='cos-upload', option='secretid')
    secret_key = config.get(section='cos-upload', option='secretkey')
    region = config.get(section='cos-upload', option='region')
    token = None  # 使用临时密钥需要传入 Token，默认为空，可不填
    scheme = config.get(section='cos-upload', option='scheme')
    bucket = config.get(section='cos-upload', option='bucket')
    try:
        _cos_config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
        client = CosS3Client(_cos_config)
        if not bucket:
            logger.error('Bucket must be specified!')
            return
        file_name_with_token = conf.get('remote_url').split("/")[-1]
        ret = re.search(r"\?token=\w+", file_name_with_token)
        file_name = re.sub(r"\?token=\w+", "", file_name_with_token) if ret else file_name_with_token
        if not client.object_exists(Bucket=bucket, Key=f'arcaea/{file_name}') \
                or not config.get(section='arc-info', option='version_cached') \
                or config.get(section='arc-info', option='version_cached') != config.get(section='arc-info',
                                                                                         option='version'):
            response = client.put_object(
                Bucket=bucket,
                Body=requests.get(url=conf.get('remote_url'), headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"},
                                  verify=False).content,
                Key=f"arcaea/{file_name}"
            )
            logger.info(response)
            logger.info('Upload success')
            config.set(section='arc-info', option='version_cached', value=file_name)
            config.write(open('.localver', 'w'))
        else:
            logger.info('No need to upload')
    except CosServiceError as e:
        logger.error(e.get_digest_msg())


def send_email(ele: dict):
    global config
    if ele['version_local'] != ele['version_string']: return
    logger = logging.getLogger("com.mgc.sendemail")
    sender = config.get(section='notification', option='sender')
    login = config.get(section='notification', option='login_email')
    password = config.get(section='notification', option='login_pw')
    receivers = config.get(section='notification', option='receivers')
    if not sender or not login or not password or not receivers: return
    message = MIMEText(f'Arcaea新版本已经发布！链接：{ele.get("remote_url")}，'
                       f'镜像地址：{ele.get("version_string")}', 'plain',
                       'utf-8')
    message['From'] = sender
    message['To'] = receivers

    subject = 'Arcaea新版本提醒 '
    message['Subject'] = subject

    try:
        smtpObj = smtplib.SMTP('smtp.163.com', 25)
        smtpObj.set_debuglevel(2)
        smtpObj.login(login, password)
        smtpObj.sendmail(sender, receivers, message.as_string())
        logger.info("Send mail success")
        smtpObj.quit()
    except smtplib.SMTPException as e:
        logger.error("Send mail error")
        logger.error(e)


@DeprecationWarning
def getarcupdate(callbacks: callable = None):
    global req
    retries = 0
    logger = logging.getLogger("com.mgc.arcgetupdate")
    url = "https://arcaea.lowiro.com/zh"
    while retries <= 3:
        http_error_raised = False
        try:
            req = requests.get(url=url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"},
                               verify=False)
            if req.status_code in (200, 301, 302):
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            logger.error("Cannot connect to the mainpage. Total retries: {}".format(retries))
            retries += 1
        except requests.exceptions.HTTPError as e:
            logger.error(f"Request error {e.request}->{e.response}")
            return
        except Exception:
            logger.error("Unknown error happened. Retrying... Total retries: {}".format(retries))
            retries += 1
        finally:
            if retries >= 3 or http_error_raised:
                logger.error("Update version operation failed. Try again.")
                return

    soup = BeautifulSoup(req.text, 'html.parser')
    ele = soup.find("a", {
        "onclick": "ga('send', 'event', {eventCategory: 'download_apk', eventAction: 'click', eventLabel: 'welcome', transport: 'beacon'});"}).attrs[
        'href']
    logger.info(f"link from webpage element: {ele}")

    if ele is not None:
        last_part = ele.split("/")[-1]  # arcaea_{ver}.apk?token={token}
        ret = re.search(r"\?token=\w+", last_part)
        if last_part is None or ret is None:
            logger.error('Not a valid download link!')
        else:
            token = last_part[ret.start() + 7:]
            version = re.sub(r"\?token=\w+", "", last_part)

            logger.info("Arcaea version: %s" % version)

            if not config.has_section('arc-info'):
                config.add_section('arc-info')
                config.set('arc-info', 'token', '')
                config.set('arc-info', 'version', '')
                config.write(open('.localver', 'w'))
            version_local = config.get(section='arc-info', option='version')
            version_cached = config.get(section='arc-info', option='version_cached')
            if version_local != version or version_cached != version_local:
                config.set(section='arc-info', option='version', value=version)
                config.set(section='arc-info', option='token', value=token)
                config.write(open('.localver', 'w'))
                for callback in callbacks:
                    callback({'remote_url': ele, 'version_string': version, 'version_local': version_cached})
            else:
                if token != config.get(section="arc-info", option="token"):
                    config.set(section="arc-info", option="token", value=token)
                    config.write(open('.localver', 'w'))
                    logger.info('Main version not updated, but with token renewed. Token: %s,'
                                'Generated Link: https://static-lb.lowiro.com/serve/%s?token=%s' % (
                                    token, version, token))
                else:
                    logger.info('Main version not updated.')
    else:
        logger.error('The webpage content is None! ')
