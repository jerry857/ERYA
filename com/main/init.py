# -*- coding: utf-8 -*
import json
import config
users_path = config.users_path
Udict = {
    "clockinLngLat": "108.891172,34.153633",
    "clockinAddress": "陕西省西安市长安区郭杜街道陕西师范大学长安校区文津楼",
    'loginType': '1',
    'roleSelect': 'true',
    "15037671931": {
        'code': 'jxl19970605jxl',
        "ps": "贾鑫磊"
    },
    "15081150997": {
        'code': 'lilisw',
        "ps": "李泽华"
    },
    "18845142702": {
        'code': 'wang6260649',
        "ps": "王文安"
    },
}
if __name__ == '__main__':
    with open(users_path, "w") as f:
        print(Udict)
        json.dump(Udict, f, ensure_ascii=False)
