Customer.io Data Pipelines analytics client for Python.

## Installation

Using pip:

```bash
pip3 install customerio-cdp-analytics
```

or you can install directly from this repo:
```bash
pip3 install git+http://github.com/customerio/cdp-analytics-python
```

## Usage

```python
from customerio_cdp_analytics import analytics

analytics.write_key = 'YOUR_WRITE_KEY'

analytics.track(user_id=4, event='order_complete')
```
