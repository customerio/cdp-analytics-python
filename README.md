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
from customerio import analytics

analytics.write_key = 'YOUR_WRITE_KEY'

analytics.track(user_id=4, event='order_complete')
```

## Other Regions

If you're using a [different data center](https://customer.io/docs/accounts-and-workspaces/data-centers/) such as our EU region, you can specify an alternate endpoint:

```python
from customerio import analytics

analytics.write_key = 'YOUR_WRITE_KEY'
analytics.host = 'https://cdp-eu.customer.io'

analytics.track(user_id=4, event='order_complete')
```

## Documentation

The links below contain more detailed documentation on how to use this library:

* [Documentation](https://customer.io/docs/cdp/sources/connections/servers/python/)
* [Specs](https://customer.io/docs/cdp/sources/source-spec/source-events/)
* [PyPi](https://pypi.org/project/customerio-cdp-analytics/)
