import time
import requests
import re


class GoogleTranslate(object):

    def __init__(self, sl='auto', tl='', domainnames=""):
        """
        A python wrapped free and unlimited API for Google Translate.

        :param sl:from Language
        :param tl:to Language
        :param domainnames: google domainnames, for example if domainnames="com" ,the url is "translate.google.com". In China the com domainnames is blocked by GFW,you can use "cn".
        """
        self.sl = sl
        self.tl = tl
        self.hl = tl

        if domainnames == "":
            self.domainnames ="com"
        else:
            self.domainnames = domainnames

        self.TKK = getTKK(domainnames=self.domainnames)

    def _returnintorzero(self, d):
        try:
            temp = int(d)
        except Exception as e:
            temp = 0
        return temp

    def _xr(self, a, b):
        size_b = len(b)
        c = 0
        while c < size_b - 2:
            d = b[c + 2]
            d = ord(d[0]) - 87 if 'a' <= d else int(d)
            d = (a % 0x100000000) >> d if '+' == b[c + 1] else a << d
            a = a + d & 4294967295 if '+' == b[c] else a ^ d
            c += 3
        return a

    def trans(self, text):
        """
        translate text

        :param text: The text to be translate

        :return:
        """
        tk = self._gettk(text)

        timeh = int(time.time() / 3600)
        if self.TKK.split(".")[0] != timeh:
            self.TKK = getTKK(domainnames=self.domainnames)

        data = {
            "client": 'webapp',
            "sl": self.sl,
            "tl": self.tl,
            "hl": self.hl,
            "dt": ['at', 'bd', 'ex', 'ld', 'md', 'qca', 'rw', 'rm', 'ss', 't'],
            "ie": 'UTF-8',
            "oe": 'UTF-8',
            "otf": 1,
            "ssel": 0,
            "tsel": 0,
            "kc": 7,
            "q": text,
            "tk": tk
        }
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br"}

        url = 'https://translate.google.'+self.domainnames+'/translate_a/single'

        jsonres = requests.get(url=url, headers=headers, params=data)

        lines = ''
        try:
            for i in jsonres.json()[0]:
                if i:
                    if i[0]:
                        lines = lines + i[0]
        except Exception as e:
            print("失败语句：")
            print(text)
            print("tk：")
            print(e)
            print('实际返回信息：')
            print(jsonres.text)
            raise Exception(text)
        return lines

    def _gettk(self, a):

        d = self.TKK.split(".")
        b = int(d[0])
        e = []
        for g in range(len(a)):
            l = ord(a[g])
            if 128 > l:
                e.append(l)
            else:
                if 2048 > l:
                    e.append(l >> 6 | 192)
                else:
                    if (55296 == (l & 64512) and g + 1 < len(a) and 56320 == (ord(a[g + 1]) & 64512)):
                        l = 65536 + ((l & 1023) << 10) + (a.charCodeAt(++g) & 1023)
                        e.append(l >> 18 | 240)
                        e.append(l >> 12 & 63 | 128)
                    else:
                        e.append(l >> 12 | 224)
                        e.append(l >> 6 & 63 | 128)
                e.append(l & 63 | 128)

        a = b
        for f in range(len(e)):
            a = a + int(e[f])
            a = self._xr(a, "+-a^+6")
        a = self._xr(a, "+-3^+b+-f");
        a ^= self._returnintorzero(d[1])
        if 0 > a:
            a = (a & 2147483647) + 2147483648
        a %= 1E6
        return str(int(a)) + "." + str(int(a) ^ b)


def getTKK(domainnames=""):
    if domainnames == "":
        url = "https://translate.google.com/"
    else:
        url = "https://translate.google." + domainnames + "/"

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br"}
    googleindexpage = requests.get(url, headers=headers).text

    tkk = re.findall("tkk:'(\d*\.\d*)'", googleindexpage)

    if len(tkk) != 0:
        return tkk[0]
    else:
        return None


if __name__ == '__main__':
    pass
    # # This is an example.
    # translator = GoogleTranslate(domainnames="cn", tl="zh-CN")
    # text_origin = "Guía de servicios notariales y consulares en Bolivia. £100"
    # print(translator.trans(text_origin))
