import requests
import pandas as pd
from urllib.parse import urljoin

class TradeBuddyNSE:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Referer": "https://www.nseindia.com/get-quotes/equity?symbol=SBIN",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.base_url = "https://www.nseindia.com"
        self.ssl_verify = True
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._initialize_session()

    def _initialize_session(self):
        url = urljoin(self.base_url, "/get-quotes/equity")
        response = self.session.get(url, verify=self.ssl_verify)
        if response.status_code == 200:
            print("Session Initialized Successfully")
        else:
            raise Exception(f"Failed to initialize session: {response.status_code} {response.text}")

    def close(self):
        self.session.close()

    def getNSEStockList(self, indexName):
        """ get list of stock with some basic infomations"""
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={indexName}"
        response = self.session.get(url, verify=self.ssl_verify)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['data'][1:])
            df['isin'] = df['meta'].apply(lambda x: x.get('isin') if isinstance(x, dict) else None)
            df['industry'] = df['meta'].apply(lambda x: x.get('industry') if isinstance(x, dict) else None)
            df['companyName'] = df['meta'].apply(lambda x: x.get('companyName') if isinstance(x, dict) else None)
            return df
        else:
            raise Exception(f"Failed to fetch data: {response.status_code} {response.text}")

    def getQuoteInformation(self, StockName):
        """ get single stock infomation """
        url = f"https://www.nseindia.com/api/quote-equity?symbol={StockName}&section=trade_info"
        response = self.session.get(url, verify=self.ssl_verify)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code} {response.text}")