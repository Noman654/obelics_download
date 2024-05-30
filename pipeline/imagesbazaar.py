import requests
def get_data(keyword):
    try:
        data = []
        for i in range(1, 3):
            url = f"https://backend.imagesbazaar.com/migration/imagesearch?keyword={keyword}&size=10000&page={i}"

            payload = {}
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Content-Length': '0',
                'Origin': 'https://www.imagesbazaar.com',
                'Referer': 'https://www.imagesbazaar.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()
            data.extend(response.json()['hits']['hits'])

            urls = []
            for d in [row['_source'] for row in data]:
                url_p = d['url'].split('/')
                url = f"https://d3nn873nee648n.cloudfront.net/900x600/{url_p[0]}/{url_p[1]}-{url_p[2]}.jpg"
                urls.append(url)
        return urls

    except Exception as e:
        print("Error occurred", e)

data = get_data('family')
