

# Install Pakages

```cmd
python -m venv venv
source venv/bin/activate # for Ubnetu linux
.\venv\Scripts\Activate.ps1 # for Windos
pip install -r requirenments.txt
fastapi dev run.py
```



```json [BUY]

{
  "stock_symbol": "SBIIN",
  "stock_isin": "123",
  "order_side": "BUY",
  "order_types": "MARKET",
  "product_type": "CNC",
  "quantity": 10,
  "order_price": 120,
  "order_note": "Test",
  "created_by": "MENUAL"
}


```




```json [SET STOPLOSS TARGET]

{
  "stock_symbol": "SBIIN",
  "stock_isin": "123",
  "order_side": "BUY",
  "order_types": "MARKET",
  "product_type": "CNC",
  "quantity": 10,
  "order_price": 120,
  "order_note": "Test",
  "created_by": "MENUAL"
}


```