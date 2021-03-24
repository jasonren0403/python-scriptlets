from pathlib import *

import requests
from bs4 import BeautifulSoup


class PicExtraction:
    def __init__(self, cvid: list, root_path: PurePath = PurePath(), alternate_name: str = '', test: bool = False):
        self.cvid = cvid
        self.root_path = root_path
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 ' \
                  'Safari/537.36 '
        self.protocol = 'https:'
        self.piclist = {}
        self.session = requests.session()
        self.alternate_name = alternate_name
        self.default_filter = lambda y: not ('class' in y and ('article-card' in y['class'] or
                                                               [x for x in y['class'] if
                                                                x.startswith('cut-off')] is not None))
        self.test = test
        self.piclinks()
        if not self.test:
            self.do_download()
        else:
            print(self.piclist)

    def piclinks(self):
        for cvid in self.cvid:
            req = self.session.get(f'https://www.bilibili.com/read/cv{cvid}', headers={
                'User-Agent': self.ua
            })
            soup = BeautifulSoup(req.content, 'html.parser')
            for cts in soup.find_all(class_='img-box'):  # .img-box>img::attr(data-src)
                print(cts.img.attrs)
                if self.default_filter(cts.img.attrs):
                    if str(cvid) not in self.piclist:
                        self.piclist.update({str(cvid): [cts.img.attrs['data-src']]})
                    else:
                        self.piclist[str(cvid)].append(cts.img.attrs['data-src'])

    def do_download(self):
        if not self.piclist:
            print('No pic in current cv!')
        else:
            import os
            for cvid in self.cvid:
                print(f'[{self.cvid.index(cvid) + 1}/{len(self.cvid)}] downloading cv{cvid}')
                path = self.root_path / str(cvid) if not self.alternate_name else self.root_path / self.alternate_name
                if not os.path.exists(path):
                    os.makedirs(path)
                for pic in self.piclist[str(cvid)]:
                    req = self.session.get(url=self.protocol + pic, headers={
                        'User-Agent': self.ua
                    })
                    picname = pic.split('/')[-1]
                    print(f'[{cvid}] downloading {picname}')
                    if req.status_code == requests.codes.OK:
                        f = open(path / picname, 'wb')
                        f.write(req.content)
                        f.close()
                    else:
                        print(f'Bad status code:{req.status_code}')


if __name__ == '__main__':
    import getopt, sys

    test_only = False
    debug = False
    usage = '''
    Usage: python extract_pics_from_bilibili_cv.py(filename) \n
    -t/--test: test only, do not download files \n
    -h/--help: show this help\n
    -c/--cvs/just list of cv numbers(separate with comma ','): cv you want to extract pictures from\n
    -d/--debug: open debug mode
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "thdc:", ["test", "help", "debug", "cvs="])
        cvid_list = []
        for o, a in opts:
            if o in ("-h", "--help"):
                print(usage)
                sys.exit()
            if o in ("-d", "--debug"):
                debug = True
                print("Debug mode on")
            if o in ("-t", "--test"):
                test_only = True
            if o in ("-c", "cvs"):
                if debug:
                    print(f"cv params:{a}")
                cvid_list = a.split(",")
                if not all(s.isdigit() for s in cvid_list):
                    print("All cvid must be number!")
                    sys.exit()
        if len(opts) == 0:
            cvid_list = args
        if debug:
            print(f"opts:{opts}")
            print(f"args:{args}")
            print(f"{cvid_list}")
        if len(cvid_list) == 0:
            print(usage)
            sys.exit()
        else:
            p = PicExtraction(cvid=cvid_list, test=test_only)

    except getopt.GetoptError:
        print(usage)
    finally:
        sys.exit()
