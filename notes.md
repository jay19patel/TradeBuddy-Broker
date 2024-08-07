

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
  "order_types": "LIMIT",
  "product_type": "CNC",
  "quantity": 10,
  "trigger_price": 120.5,
  "limit_price":120.0,
  "note": "Test",
  "created_by": "MENUAL"
}

```



```json [STOPLIMIT]
{
  "stock_symbol": "SBIIN",
  "stock_isin": "123",
  "order_types": "STOPLIMIT",
  "product_type": "CNC",
  "stoploss_limit_price":100,
  "stoploss_trigger_price":100,
  "target_limit_price":200,
  "target_trigger_price":200,
  "note": "Test",
  "created_by": "MENUAL"
}

```


