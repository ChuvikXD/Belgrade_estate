from bs4 import BeautifulSoup
#https://cityexpert.rs/ru/properties-for-rent/belgrade ЮРЛ ДЛЯ данных
import requests

cookies = {
    '_gcl_au': '1.1.457839220.1778000524',
    '_ga': 'GA1.1.2122046380.1778000525',
    'FPID': 'FPID2.2.FY8M7xmhsmFxfYI%2B7OV7rHugpalq7EDEVqgaja%2FDbIQ%3D.1778000525',
    'FPLC': 'nWPSu5moWRY8jNpNRYKLyIhZuUT8xedFFmyQf94rt2Wu4rKPR2o%2FJnxgsE%2F%2FbievPMvKqaZqs4ntxSogMtgLCu8aF%2FfeE0nD1oIDZ9Zt%2F7upgzOtFtGx7nWaZMLtRg%3D%3D',
    'FPAU': '1.1.457839220.1778000524',
    'cw_conversation': 'eyJhbGciOiJIUzI1NiJ9.eyJzb3VyY2VfaWQiOiJjYzAxYjA0Mi1jM2EzLTQ2NDYtOTBlNS0zMGY5N2ZkZjBlN2UiLCJpbmJveF9pZCI6MSwiZXhwIjoxNzkzNTU0MDg5LCJpYXQiOjE3NzgwMDIwODl9.CFeCt0LPNWlUp8Sx_DVh9ZxUpALPQCklz6zewoQN7fc',
    'g_state': '{"i_l":0,"i_ll":1778003090067,"i_b":"TgHGl2UAFpGpzO0882KZU4wqsgqr8Aq08BGQS5UbSfk","i_e":{"enable_itp_optimization":0},"i_et":1778000524549}',
    'FPGSID': '1.1778002382.1778003090.G-7EWXF6Y9ER.TSLsXkSp_qpkuWVsV2ckUw',
    '_ga_7EWXF6Y9ER': 'GS2.1.s1778000524$o1$g1$t1778003092$j57$l0$h1447543542',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'baggage': 'sentry-environment=cityexpert.rs,sentry-release=cx%4020260505.1,sentry-public_key=ffb1eb2ba593437d9d43915e1a2f2bbe,sentry-trace_id=bea1be8d64ca4b5e8c3e62b74cbc87c4,sentry-transaction=%2Fproperties-for-rent%2Fbelgrade%2F%3Aid%2F%3Aslug%2F,sentry-sampled=true,sentry-sample_rand=0.4661879355232461,sentry-sample_rate=1',
    'dnt': '1',
    'priority': 'u=1, i',
    'referer': 'https://cityexpert.rs/ru/properties-for-rent/belgrade/75791/5-rooms-apartment-tatar-bogdanova-zvezdara',
    'sec-ch-ua': '"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sentry-trace': 'bea1be8d64ca4b5e8c3e62b74cbc87c4-a82e1d0cccdae51c-1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
    # 'cookie': '_gcl_au=1.1.457839220.1778000524; _ga=GA1.1.2122046380.1778000525; FPID=FPID2.2.FY8M7xmhsmFxfYI%2B7OV7rHugpalq7EDEVqgaja%2FDbIQ%3D.1778000525; FPLC=nWPSu5moWRY8jNpNRYKLyIhZuUT8xedFFmyQf94rt2Wu4rKPR2o%2FJnxgsE%2F%2FbievPMvKqaZqs4ntxSogMtgLCu8aF%2FfeE0nD1oIDZ9Zt%2F7upgzOtFtGx7nWaZMLtRg%3D%3D; FPAU=1.1.457839220.1778000524; cw_conversation=eyJhbGciOiJIUzI1NiJ9.eyJzb3VyY2VfaWQiOiJjYzAxYjA0Mi1jM2EzLTQ2NDYtOTBlNS0zMGY5N2ZkZjBlN2UiLCJpbmJveF9pZCI6MSwiZXhwIjoxNzkzNTU0MDg5LCJpYXQiOjE3NzgwMDIwODl9.CFeCt0LPNWlUp8Sx_DVh9ZxUpALPQCklz6zewoQN7fc; g_state={"i_l":0,"i_ll":1778003090067,"i_b":"TgHGl2UAFpGpzO0882KZU4wqsgqr8Aq08BGQS5UbSfk","i_e":{"enable_itp_optimization":0},"i_et":1778000524549}; FPGSID=1.1778002382.1778003090.G-7EWXF6Y9ER.TSLsXkSp_qpkuWVsV2ckUw; _ga_7EWXF6Y9ER=GS2.1.s1778000524$o1$g1$t1778003092$j57$l0$h1447543542',
}

params = {
    'req': '{"serviceType":"p","ptId":[1],"cityId":1,"rentOrSale":"r","currentPage":1,"resultsPerPage":4,"avFrom":false,"underConstruction":false,"minPrice":900,"maxPrice":1500,"minPricePerM":null,"maxPricePerM":null,"minInstallment":null,"maxInstallment":null,"minSize":null,"maxSize":null,"searchSource":"regular","sort":"datedsc","floor":[],"furnished":[],"furnishingArray":[],"heatingArray":[],"parkingArray":[],"petsArray":[],"polygonsArray":["Zvezdara"],"propIds":[],"structure":[],"ceiling":[],"bldgOptsArray":[],"yearOfConstruction":[],"joineryArray":[],"otherArray":[],"bedroomsArray":[],"bathroomArray":[],"renovationArray":[],"minLeaseArray":[],"distanceCenterArray":[],"isSalonac":false,"isNotLastFloor":false,"isNoElevatorButLow":false,"newDevelopment":false,"isFeatured":false,"isLux":false}',
}

response = requests.get('https://cityexpert.rs/api/Search/', params=params, cookies=cookies, headers=headers)
data = response.json()
apartments = data.get('result', [])

for apartment in apartments:
    street = apartment['street']
    area = apartment['size']
    price = apartment['price']
    dist = apartment['municipality']
    id = apartment['propId']
    pricePerM = round(apartment['pricePerSize'], 2)
    distance = apartment['distanceCenterArray']
    if price<=1000 and area>=50:
        print('HOT!')
    print(f'Апартаменты в районе {dist} на {street}, по цене в {price}€\nобщая площадь: {area}м2, цена за м2: {pricePerM}\n')
    print(f'https://cityexpert.rs/ru/properties-for-rent/belgrade/{id}/other-office-space-mijacka-vozdovac')