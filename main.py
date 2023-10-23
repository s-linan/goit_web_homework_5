import sys
from datetime import datetime, timedelta
import httpx
import asyncio
import platform


class HttpError(Exception):
    pass


async def request(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise HttpError(f"Error status: {r.status_code} for {url}")


async def main(index_day):
    d = datetime.now() - timedelta(days=int(index_day))
    shift = d.strftime("%d.%m.%Y")
    try:
        response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
        return response
    except HttpError as err:
        print(err)
        return None


def output(data, counter, return_list):
    result = {}
    date = (datetime.now() - timedelta(days=counter)).strftime("%d.%m.%Y")
    for i, j in [item for item in data.items()]:
        if type(j) == list:
            for item in j:
                if item.get('currency') == 'USD' or item.get('currency') == 'EUR':
                    result.update({
                        item.get('currency'): {'sale': item.get('saleRateNB'), 'purchase': item.get('purchaseRateNB')}})
    return_list.append({date: result})
    return return_list


if __name__ == '__main__':
    return_list = []
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    i = int(sys.argv[1])
    while i > 0:
        return_list = output(asyncio.run(main(i)), i, return_list)
        i -= 1
    print(return_list)
