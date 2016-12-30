# txprop21

Get Bitcoin transaction propagation information for a new transaction. Old transactions are not supported, i.e. created more than 3 hours ago.

## Install

Start by installing `21` client from [21.co](https://21.co) in order to follow the sample usage below.

Installation of `txprop21` is required only if you wish to run the server on your machine.

```
$ sudo apt-get install memcached
$ git clone https://github.com/ayeowch/txprop21.git
$ cd txprop21
$ virtualenv --python=python3 venv
$ source venv/bin/activate
$ pip install -e .
```

## Usage

### Server

To start the server, simply execute the command below.

```
$ ./runserver.sh
```

The server will run as background process with log entries written into access.log. The default log rotation configuration will rotate the log file once it reaches 2MB.

Only one instance of the server will be running at any one time, i.e. executing `./runserver.sh` again will terminate the old instance of the server and start a new one.

Check that the server is running by following the steps below.

```
$ tail access.log
2016-05-21 04:10:38,366 [INFO] 17515.548136099840 _log >>>  * Running on http://0.0.0.0:8008/ (Press CTRL+C to quit)

$ curl localhost:8008
Payment Required
```

Once the server is running, publish it on the [21 Marketplace](https://21.co/mkt/) by executing the command below.

```
$ 21 publish submit manifest.yaml -p 'name="Joe Smith" email="joe@example.com" price="5" host="AUTO" port="8008"'
```

### Client

The example below shows that a new transaction with transaction hash fd8fa4.. has been broadcasted by 83.12% (`propagation_level` field) of the reachable nodes in the Bitcoin network when the command was executed. Transaction announced by more than 50% of the reachable nodes should eventually make it into a new block.

The information in the `nodes` field shows how fast the transaction is propagating across the network. In the example below, 50% of the nodes broadcasted the transaction within 3548 milliseconds.

You might want to replace the transaction hash with a newly generated transaction, such as transaction that you have just made. You can then use the information to decide legitimacy of the new transaction by looking at how well the transaction is propagating across the Bitcoin network.

```
$ 21 buy http://dazzlepod.com:65000/?tx=fd8fa4
{
    "hash": "fd8fa4ec3f37b6d7470686ce3f377ca57a88a8697bc345e00b167929337177c7",
    "propagation": {
        "first_node": {
            "address": "2a01:4f8:191:63b4:5000::1",
            "port": 8333
        },
        "last_node": {
            "address": "71.9.37.148",
            "port": 8333
        },
        "nodes": {
            "25%": 1619,
            "50%": 3548,
            "75%": 6496,
            "count": 4352,
            "max": 14118,
            "mean": 4441,
            "min": 343,
            "std": 3391
        },
        "propagation_level": 83.12
    },
    "reachable_nodes": 5236,
    "timestamp": 1483074576622
}
```
