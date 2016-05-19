# txprop21

Get transaction propagation information for a new transaction. Old transactions are not supported, i.e. created more than 3 hours ago.

## Install

```
$ git clone https://github.com/ayeowch/txprop21.git
$ cd txprop21
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Usage

The example below shows that a new transaction with transaction hash 7dd2.. has been broadcasted by 40.33% (`propagation_level` field) of the reachable nodes in the Bitcoin network when the command was executed. Transaction announced by more than 50% of the reachable nodes should eventually make it into a new block.

The information in the `nodes` field shows how fast the transaction is propagating across the network. In the example below, 50% of the nodes broadcasted the transaction within 657 milliseconds.

```
$ ./txprop21.py 7dd2a7b3c94dd021f3a4a93ff56a534b0923f574c603974746f331ae565a77d1
{
    "propagation": {
        "first_node": {
            "address": "bpdlwholl7rnkrkw.onion",
            "port": 8333
        },
        "last_node": {
            "address": "46.4.56.4",
            "port": 9333
        },
        "nodes": {
            "25%_ms": 376.75,
            "50%_ms": 657.0,
            "75%_ms": 3674.5,
            "count": 1926,
            "max_ms": 126039.0,
            "mean_ms": 3284.380977130977,
            "min_ms": 168.0
        },
        "propagation_level": 40.33
    },
    "reachable_nodes": 4776,
    "tx_age_ms": 159460,
    "tx_hash": "7dd2a7b3c94dd021f3a4a93ff56a534b0923f574c603974746f331ae565a77d1"
}
```
