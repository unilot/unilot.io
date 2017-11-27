# Unilot

Simple lottery based on ethereum smart contracts.

## Installation

1. Create directory for environment and app

```
cd ~/apps/
virtualenv -p /usr/bin/python3.5 unilot
```

2. Activate environment settings (see [virtualenv docs](https://virtualenv.pypa.io/en/stable/) for more info)

```
source ~/apps/unilot/bin/activate
```

3. Pull code from repo

```
git pull https://github.com/unilot/unilot.io app
```

Result of this command will be pulled code located in `~/apps/unilot/app`

4. Now configure

Go to app dir (`~/apps/unilot/app`)

Copy example settings file and setup required settings.

```
cp unilot/local_settings.py.example unilot/local_settings.py
```

For simple app start you can just setup `secret key` and `database`.

For setting up connection to ethereum node see ethereum configuration.

5. Install requirements

```
pip install -r requirements
```

6. Run migrations

```
python manage.py migrate
```

## Ethereum configuration

_This part might change in future. Keep an eye on updates._

Ethereum related configuration is located in `WEB3_CONFIG` dictionary in
`settings` file.

* `MODE` - _Required_. Node connection mode. It can be via IPC socket file or http.
Values can be: `IPC`, `RPC`. Depending on value different keys might be
required.
* `PATH` - _Default: `None`, required when `MODE` is set to `IPC`_.
Absolute path to IPC socket.
* `IS_TESTNET` - _Default: `False`, optional_. Used only for
`MODE` - `IPC`. Identifies that `IPC` works with testnet (rinkeby).
* `HOST` - _Default: `127.0.0.1`, required when `MODE` is set to `RPC`_.
Host to connect.
* `PORT` - _Default: `8545`, required when `MODE` is set to `RPC`_.
Port to connect.
* `PREFIX` - _Default: `/`, optional_. _Used only for `MODE` - `RPC`_.
* `ETHBASE` - _Required_. Account that is used to run operations in API.
* `ETHBASE_PWD` - _Required_. Password to account (`ETHBASE`) to unlock
for operations that require password.


### Example

This example considers that you use ubuntu 16.04 and have installed
go-ethereum and you are able to run `geth` command in cmd (console).

I recommend to install command like `screen` or open 2 cmd windows/tabs.

If using screen:

```
screen -S eth-node
```

In example geth will be started with `IPC` and `RPC` enabled.
`RPC` uses default port `8545`. Set `--rpcport` option to set custom
port.
`IPC` socket's location is `~/.ethereum/geth.ipc`.
Node will connect to test network and make fast sycnronization
(for details see
[docs](https://github.com/ethereum/go-ethereum/wiki/geth)).

In this example in only api required to operate `unilot` was enabled.

```
geth --rinkeby --fast --cache 1024 --rpc --rpcaddr 127.0.0.1 --rpcapi "eth,personal,web3,net" --ipcpath /home/ethereum/.ethereum/geth.ipc console
```

After start you will see `geth` console where you can operate with
data in the node.
See [docs](https://github.com/ethereum/wiki/wiki/JSON-RPC) for details.

If you use `screen` to detach from session press and hold `Ctrl` and
press `a` then `d`.

To access session again and return to console run:

```
screen -x eth-node
```


**WIP**
