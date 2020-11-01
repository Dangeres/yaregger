import requests as req
import base64
import time
from bs4 import BeautifulSoup
import string
import re
import random
import json


RUCAPTCHA_KEY = None #edit that None or str


track = ''
csrf = ''

ses = req.session()

ses.headers.update({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'passport.yandex.ru',
    'Origin': 'https://passport.yandex.ru',
    'Referer': 'https://passport.yandex.ru/registration/',
    # 'Sec-Fetch-Dest': 'empty',
    # 'Sec-Fetch-Mode': 'cors',
    # 'Sec-Fetch-Site': 'same-origin',

    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
})


my_login = "".join(random.choice(string.ascii_letters) for x in range(random.randint(8, 10)))
my_pass = "".join(random.choice(string.ascii_letters + string.digits) for x in range(8))
my_pass += "".join(random.choice(string.digits) for x in range(4))


debug = True

def regexp(text, pattern):
    if not text:
        return None

    found = re.search(pattern, text)

    return found.group(1) if found else None


if debug:
    while True:
        get_first = ses.get('https://passport.yandex.ru/registration/')

        soup = BeautifulSoup(get_first.text, 'html.parser')

        track = soup.find('input', attrs= {'name': 'track_id'})['value']
        csrf = regexp(get_first.text, r'"csrf":"([\w\W]+:[\d]+)"')
        # csrf = soup.find('body')['csrf']

        captcha = ses.post('https://passport.yandex.ru/registration-validations/textcaptcha', data = {
            'track_id': track,
            'csrf_token': csrf,
            'language': 'ru',
            'ocr': True
        })

        try:
            captcha = json.loads(captcha.text)
            if captcha['status'] == 'ok':
                print(captcha['image_url'])

                if RUCAPTCHA_KEY is not None:
                    print('solving... wait.')

                    for _ in range(10):
                        a = req.post('https://rucaptcha.com/in.php', data= {
                            'key': RUCAPTCHA_KEY,
                            'method': 'base64',
                            'body': base64.b64encode(req.get(captcha['image_url']).content)
                        }).text.split('|')

                        if a[0] == 'OK':
                            break
                        else:
                            print(a[0])

                    for _ in range(10):
                        res = req.post('https://rucaptcha.com/res.php', data={
                            'key': RUCAPTCHA_KEY,
                            'action':'get',
                            'id': a[1]
                        }).text.split('|')

                        if res[0] == 'OK':
                            resolve_captcha = res[1]
                            break
                        else:
                            print(res[0])
                            time.sleep(4)

                else:
                    resolve_captcha = input('Captcha resolve: ')

                result_resolve = json.loads(ses.post('https://passport.yandex.ru/registration-validations/checkHuman', data = {
                    'track_id': track,
                    'csrf_token': csrf,
                    'answer': resolve_captcha
                }).text)

                if result_resolve['status'] == 'ok':
                    print(result_resolve)
                    break

            print(captcha)
        except Exception as e:
            pass



result = ses.post('https://passport.yandex.ru/registration-validations/registration-alternative', data = {
    'track_id': track,
    'csrf_token': csrf,
    'firstname': 'Dmitriy',
    'lastname': 'Yablokov',
    'surname': '',
    'login': my_login,
    'password': my_pass,
    'password_confirm': my_pass,
    'hint_question_id': '12',
    'hint_question': 'Фамилия вашего любимого музыканта',
    'hint_question_custom': '',
    'hint_answer': 'Курт',
    'captcha': resolve_captcha,
    'phone': '',
    'phoneCode': '',
    'human-confirmation': 'captcha',
    'from': 'mail',
    'eula_accepted': 'on',
    'type': 'alternative'
})


print(result.text)
print('------')
print('%s:%s' % (my_login, my_pass))
print('------')
print('end')
