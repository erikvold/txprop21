# txprop21

Get Bitcoin transaction propagation information for a new transaction. Old transactions are not supported, i.e. created more than 3 hours ago.

## Install

Start by installing `21` client from [21.co](https://21.co) in order to follow the sample usage below.

Installation of `txprop21` is required only if you wish to run the server on your machine.

```
$ sudo apt-get install memcached
$ git clone https://github.com/ayeowch/txprop21.git
$ cd txprop21
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
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

The example below shows that a new transaction with transaction hash 08dcc2.. has been broadcasted by 40.64% (`propagation_level` field) of the reachable nodes in the Bitcoin network when the command was executed. Transaction announced by more than 50% of the reachable nodes should eventually make it into a new block.

The information in the `nodes` field shows how fast the transaction is propagating across the network. In the example below, 50% of the nodes broadcasted the transaction within 902 milliseconds.

You might want to replace the transaction hash with a newly generated transaction, such as transaction that you have just made. You can then use the information to decide legitimacy of the new transaction by looking at how well the transaction is propagating across the Bitcoin network.

```
$ 21 buy http://10.244.227.106:8008/?tx=08dcc2
{
    "propagation": {
        "first_node": {
            "address": "qyukxbbf6gvjbs77.onion",
            "port": 8333
        },
        "last_node": {
            "address": "82.221.133.147",
            "port": 8333
        },
        "nodes": {
            "25%_ms": 414.0,
            "50%_ms": 902.0,
            "75%_ms": 3949.75,
            "count": 1968,
            "max_ms": 30489.0,
            "mean_ms": 3471.3006103763987,
            "min_ms": 41.0
        },
        "propagation_level": 40.64
    },
    "reachable_nodes": 4843,
    "tx_age_ms": 33833,
    "tx_hash": "08dcc2c14dd122b0dc5dcf1156dff0ea6b2c4824f24f6fb22393f7b013995025"
}
```
