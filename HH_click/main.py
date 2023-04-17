import requests
import re
from multiprocessing import Pool
import pdb

def send_req(item):
    check = item[4].post('https://hh.ru/applicant/vacancy_response/popup', data={"incomplete": False, "vacancy_id":int(item[0]), "resume_hash": f"{item[1]}","ignore_postponed": True, "_xsrf":f"{item[2]}", "letter": f"{item[3]}", "lux": True, "withoutTest": "no", "hhtmFromLabel": "undefined", "hhtmSourceLabel": "undefined"})

    print(check.status_code, item[0])
    if check.status_code != 200:
        if check.json()['error' ] == 'negotiations-limit-exceeded':
            return False


if __name__ == "__main__":
    n = 0
    req = requests.Session()

    """
    Привет! Чтобы скрипт заработал надо заполнить несколько полей, иначе HH не пустит запросы
    Введи сюда сво куки. Важно быть залогиненым на HH. Проще всего это сделав скопировав все как HAR . Дальше нас инетерсует все что после 'Cookie:' до следующего поля с ':' (это может быть 'X-hhtmFrom:') или что-то другое. Главное забрать все после кук
    """
    
    # SAVE REQ AS CURL
    x = """_xsrf=7cd14fa385fee8ad492c229428e18c00; hhuid=1oovfjes3xPwzF\u0021KPtQ\u0021DQ--; __ddg1_=KIfcQl3wGAd0TSljpAWY; region_clarified=NOT_SET; crypted_hhuid=2C45C62FC4F4C8AAF720DC9F202AEF8D122988F92840EB7C526924BE651195E4; iap.uid=ab72ab54234f405586289a7ee5cf24c1; hhul=f04fe448c90f9bb5b6ba0c1fc55035c6a9bc0c4b7dac08bd128521854afd7c7f; redirect_host=surgut.hh.ru; display=desktop; GMT=5; total_searches=24; regions=147; crypted_id=2EC299F11CE875A8000C16CB7D2738DDA5471C6F722104504734B32F0D03E9F8; hhtoken=AphEiKDxmjBKn1cLhkJrUo1qfoCh; _hi=95187901; hhrole=applicant; device_breakpoint=s; __zzatgib-w-hh=MDA0dC0jViV+FmELHw4/aQsbSl1pCENQGC9LXzAwPmlPYEwSJUoQfjYrIBV5a1gLDxNkc0l1dCltaU8YOVURCxIXRF5cVWl1FRpLSiVueCplJS0xViR8SylEW1V6LB4Xem4mUH8PVy8NPjteLW8PKhMjZHYhP04hC00+KlwVNk0mbjN3RhsJHlksfEspNRMLCVgeQnxuLAg9EWRzSG8vL0MiJmhHXChGDwp+Wh8XfGtVUw89X0EzaWVpcC9gIBIlEU1HGEVkW0I2KBVLcU8cenZffSpBbR5mTF8iRlhNCi4Ve0M8YwxxFU11cjgzGxBhDyMOGFgJDA0yaFF7CT4VHThHKHIzd2UyQGYlZlBZIDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeishEn5wKVIKDlw9Q2llbQwtUlFRS2IPHxo0aQteTA==ss+7+w==; __zzatgib-w-hh=MDA0dC0jViV+FmELHw4/aQsbSl1pCENQGC9LXzAwPmlPYEwSJUoQfjYrIBV5a1gLDxNkc0l1dCltaU8YOVURCxIXRF5cVWl1FRpLSiVueCplJS0xViR8SylEW1V6LB4Xem4mUH8PVy8NPjteLW8PKhMjZHYhP04hC00+KlwVNk0mbjN3RhsJHlksfEspNRMLCVgeQnxuLAg9EWRzSG8vL0MiJmhHXChGDwp+Wh8XfGtVUw89X0EzaWVpcC9gIBIlEU1HGEVkW0I2KBVLcU8cenZffSpBbR5mTF8iRlhNCi4Ve0M8YwxxFU11cjgzGxBhDyMOGFgJDA0yaFF7CT4VHThHKHIzd2UyQGYlZlBZIDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeishEn5wKVIKDlw9Q2llbQwtUlFRS2IPHxo0aQteTA==ss+7+w==; cfidsgib-w-hh=5DTkmn8mcGKpyj3Gv+96rIFGbXDo26FAf9qys/tKc63gRqyCRx5WWyPylDWJNnH/V8sQptZFjPZwQrn/iWTnBqTYInz3jHlHeVDJ7CI+Gl06CT8CWV2jK259stYTUvPB1QOtys5isnk4kSYYYaZ+VGA0wARJhnoTK+q/4vMr; cfidsgib-w-hh=5DTkmn8mcGKpyj3Gv+96rIFGbXDo26FAf9qys/tKc63gRqyCRx5WWyPylDWJNnH/V8sQptZFjPZwQrn/iWTnBqTYInz3jHlHeVDJ7CI+Gl06CT8CWV2jK259stYTUvPB1QOtys5isnk4kSYYYaZ+VGA0wARJhnoTK+q/4vMr; cfidsgib-w-hh=5DTkmn8mcGKpyj3Gv+96rIFGbXDo26FAf9qys/tKc63gRqyCRx5WWyPylDWJNnH/V8sQptZFjPZwQrn/iWTnBqTYInz3jHlHeVDJ7CI+Gl06CT8CWV2jK259stYTUvPB1QOtys5isnk4kSYYYaZ+VGA0wARJhnoTK+q/4vMr; gsscgib-w-hh=3lh2i+6Pw4xKxBVTdmxkWV6oVLFIUYLuIBgj8rP6cqlwV7PZ3ESV9CDs2+rxD4Ryhm4ZRSePyC8CPJ9C8xF+Qz87d8raSSlDdqBgDaYj4t4C0tif1NTTiFBMkPTnnt3bavM2kO+AX08ALUaD0Ga/3rb7EGNnAOPlf1VzJzYWhmp4iS2bFztrXn04ja0HdX9c4CSIStQsjRsk6nxDxecgph3ses9dEaHC99YiZf+7HAjjvIAaLAvfIoAstJAj8UgY4Cg=; gsscgib-w-hh=3lh2i+6Pw4xKxBVTdmxkWV6oVLFIUYLuIBgj8rP6cqlwV7PZ3ESV9CDs2+rxD4Ryhm4ZRSePyC8CPJ9C8xF+Qz87d8raSSlDdqBgDaYj4t4C0tif1NTTiFBMkPTnnt3bavM2kO+AX08ALUaD0Ga/3rb7EGNnAOPlf1VzJzYWhmp4iS2bFztrXn04ja0HdX9c4CSIStQsjRsk6nxDxecgph3ses9dEaHC99YiZf+7HAjjvIAaLAvfIoAstJAj8UgY4Cg=; fgsscgib-w-hh=cJ8S84e6ea91cce428ac3c5a771d3271a2df57d1; fgsscgib-w-hh=cJ8S84e6ea91cce428ac3c5a771d3271a2df57d1"""
    cookies = x

    if cookies == "Вставь сюда свои куки":
        raise Exception("Ты забыл вставить сюда свои куки")

    req.headers = {"Host": "hh.ru", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_8) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15", "Cookie": f"""{cookies}"""}

    """Здесь нам нужно вставить хеш резюме. Оно находиться в разделе https://hh.ru/applicant/resumes . Дальше ты должен перейти в одно из своих резюме и скопировать хеш после ссылки . Как пример https://hh.ru/resume/71010d6fff099f0ef20039ed1f497978653133 . Тут нам нужно забрать 71010d6fff099f0ef20039ed1f497978653133 и вставить в поле ниже"""

    # !!! my
    resume_hash = "3d223c3fff0b88a62b0039ed1f387856794335"

    xsrf_token = re.search("_xsrf=(.*?);", cookies).group(1)

    """Ниже вставляем свое письмо. Советую сделать его максимально обобщенным. Больше об этом в мое треде https://twitter.com/ns0000000001/status/1612456900993650688?s=52&t=X3kUKCZQjFDJbTbg9aQWbw """

    # TODO LETTER
    letter = """Хочу к вам
    В команду
    """

    if letter == "Вставь сюда свое письмо":
        raise Exception("Ты забыл вставить сюда своё письмо")

    """Дальще переходи на страницу HH и в поиске вбиваем то, что вам интересно. После нажимает Enter и копируем ссыку на которую вас перебросило. Пример который получается при вводе 'автоматизация python': https://hh.ru/search/vacancy?text=автоматизация+python&salary=&schedule=remote&ored_clusters=true&enable_snippets=true"""

    # https://surgut.hh.ru/search/vacancy?text=Data+scientist
    search_link = "https://surgut.hh.ru/search/vacancy?text=Data+scientist"

    if search_link == "Вставь сюда свой поисковый запрос":
        raise Exception("Ты забыл вставить сюда свой запрос")

    pool = Pool(processes=70)

    """Важно, что HH позволяет в день откликаться только на 200 вакансий. Поэтому, как только скрипт получит ошибку о привышения лимита, он автоматически отключиться. Если ты все сделал правильно, то ты будешь видеть в консоли такие записи
    400 76870753
    200 76613497
    400 и 200 статусы это ок. Если ты видишь только 403 или 404 проверь, правильно ли ты вставил куки
    """

    while True:
        data = req.get(f"{search_link}&page={n}").text
        links = re.findall('https://hh.ru/vacancy/(\d*)?', data, re.DOTALL)
        send_dict = []
        for link in links:
            send_dict.append((link, resume_hash, xsrf_token, letter, req))
        if links == []:
            break
        check = pool.map(send_req, send_dict)
        if False in check:
            break
        n += 1
    pool.close()
    pool.join()
