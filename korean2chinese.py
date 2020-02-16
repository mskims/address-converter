import json

import requests
from bs4 import BeautifulSoup


def get_address_db_from_local():
    with open("address_db/gus.json") as f:
        gus = json.load(f)
    with open("address_db/roads_by_gu.json") as f:
        roads_by_gu = json.load(f)

    return gus, roads_by_gu


def main(update_mode=False):
    gus = fetch_gus()
    roads_by_gu = {}

    for gu_kr, gu_cn in gus.items():
        dongs = fetch_dongs(gu_cn)
        roads = {}

        # "읍,면 없는 도로명 보기" 만 있는 경우
        roads.update(fetch_roads(gu=gu_cn, dong=1))

        if dongs:
            for dong in dongs.values():
                roads.update(fetch_roads(gu=gu_cn, dong=dong))

        roads_by_gu[gu_kr] = roads

        print(f'Completed: {gu_kr}')

    if update_mode:
        # update db
        with open("address_db/gus.json", "w") as f:
            json.dump(gus, f, ensure_ascii=False)
        with open("address_db/roads_by_gu.json", "w") as f:
            json.dump(roads_by_gu, f, ensure_ascii=False)

    return gus, roads_by_gu


def fetch_gus():
    response = fetch({})
    return parse_state(response, table_idx=1)


def fetch_dongs(gu):
    response = fetch({
        'kukun': gu,
    })
    return parse_state(response, table_idx=2)


def fetch_roads(gu, dong):
    response = fetch({
        'kukun': gu,
        'kukunDetailChn': '',
        'kukunDetailKor': '',
        'dong': dong,
    })
    return parse_state(response, table_idx=3)


def fetch(params):
    return requests.get("https://hanja.dict.naver.com/category/address", {
        'sido': '서울特別市',  # 서울 외 지역은 읍, 면이 나뉜 경우가 있는데 어떻게 처리해야할지 모르겠음
        'isNew': '1',
        **params,
    })


def parse_state(response, table_idx):
    result = {}

    bsObj = BeautifulSoup(response.text, 'lxml')
    table = bsObj.find_all('div', {'class': 'address_slted'})[table_idx]

    # for table in tables:
    tds = table.find_all('td')
    for td in tds:
        kr = td.find('span', {'class': 'hangul'})
        cn = td.find('span', {'class': 'hanja2'})

        if not kr or not cn:
            continue
        result[kr.text] = cn.text

    return result


if __name__ == '__main__':
    main(update_mode=True)
