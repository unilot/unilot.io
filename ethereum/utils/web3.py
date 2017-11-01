from sportloto.settings import WEB3_CONFIG
from web3 import Web3, KeepAliveRPCProvider, IPCProvider
from django.utils.translation import ugettext as _
from os import path
import json


"""
Singleton for web3 object
"""

CONNECTION_MODE_IPC = 'IPC'
CONNECTION_MODE_RPC = 'RPC'

CONFIG = {
        'MODE': CONNECTION_MODE_IPC,
        'PATH': None,
        'IS_TESTNET': False,
        'HOST': '127.0.0.1',
        'PORT': '8545',
        'PREFIX': '/'
    }


def get_config():
    config = CONFIG.copy()
    config.update(WEB3_CONFIG)

    return config


class AppWeb3():
    __web3__ = None


    @staticmethod
    def get_web3():
        """
        :rtype: Web3
        """
        if not AppWeb3.__web3__:
            AppWeb3.__web3__ = AppWeb3.__web3_factory__()

        return AppWeb3.__web3__

    @staticmethod
    def __web3_factory__():
        return Web3(AppWeb3.__build_provider__())

    @staticmethod
    def __build_provider__():
        config = get_config()

        if config['MODE'] == CONNECTION_MODE_RPC:
            provider = KeepAliveRPCProvider(host=config['HOST'], port=config['PORT'], path=config['PREFIX'])
        elif config['MODE'] == CONNECTION_MODE_IPC:
            provider = IPCProvider(ipc_path=config['PATH'], testnet=config['IS_TESTNET'])
        else:
            raise RuntimeError(_('Invalid mode'))

        return provider

class ContractHelper():
    base_path = path.join(
        path.dirname(path.dirname(path.abspath(__file__))),
        'build')
    ABI_FILE_EXT = 'abi'
    BYTECODE_FILE_EXT = 'bytecode'

    @staticmethod
    def get_abi(contract_name):
        """
        :param contract_name: str
        :rtype: list
        """
        file_path = ContractHelper.__build_file_path__(
            ('%s.%s' % (contract_name, ContractHelper.ABI_FILE_EXT)))

        ContractHelper.__check_path__(file_path)

        try:
            with open(file_path, 'r') as abi_text_stream:
                abi = json.load(abi_text_stream)
        except IOError:
            raise RuntimeError(_('Failed to read abi from file "%s"' % (file_path)))

        return abi

    @staticmethod
    def get_bytecode(contract_name):
        """
        :param contract_name: str
        :rtype: str
        """
        file_path = ContractHelper.__build_file_path__(
            ('%s.%s' % (contract_name, ContractHelper.BYTECODE_FILE_EXT)))

        ContractHelper.__check_path__(file_path)

        try:
            with open(file_path, 'r') as bytecode_stream:
                bytecode = bytecode_stream.readline()
        except IOError:
            raise RuntimeError(_('Failed to read bytecode from file "%s"' % (file_path)))

        return bytecode

    @staticmethod
    def getGasPrice():
        config = get_config()
        gasPrize = config['GAS_PRICE']

        return Web3.toWei(gasPrize[0], gasPrize[1])

    @staticmethod
    def getCalculatorContractAddress():
        config = get_config()
        address = config['CALCULATOR_CONTRACT_ADDRESS']

        return address

    @staticmethod
    def __build_file_path__(filename):
        return path.join(
            ContractHelper.base_path,
            filename)

    @staticmethod
    def __check_path__(file_path):
        if not path.exists(file_path):
            raise AttributeError(_('Invalid path. File "%s" doesn\'t exist' % file_path))


class AccountHelper:
    @staticmethod
    def get_base_account():
        config = get_config()
        result = AppWeb3.get_web3().eth.coinbase

        if 'ETHBASE' in config:
            result = config['ETHBASE']

        return result

    @staticmethod
    def unlock_base_account():
        config = get_config()

        if not 'ETHBASE_PWD' in config:
            raise ReferenceError(_('Passphrase for base account is not set int settings WEB3_CONFIG -> ETHBASE_PWD'))

        AppWeb3.get_web3()\
            .personal.unlockAccount(account=AccountHelper.get_base_account(),
                                    passphrase=config['ETHBASE_PWD'])
