from scripts.utils import get_account, encode_function_data
from brownie import Box, ProxyAdmin, TransparentUpgradeableProxy, Contract


def test_proxy_delegate_calls_box():
    # Arrange
    account = get_account()
    box_contract = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})

    box_encoded_initializer_func = encode_function_data()

    proxy_contract = TransparentUpgradeableProxy.deploy(
        box_contract.address,
        proxy_admin.address,
        box_encoded_initializer_func,
        {"from": account, "gas_limit": 1_000_000},
    )
    proxy_box_contract = Contract.from_abi(
        "Box", proxy_contract.address, box_contract.abi
    )
    assert proxy_box_contract.retrieve({"from": account}) == 0

    # Act
    proxy_box_contract.store(10, {"from": account})

    # Assert
    assert proxy_box_contract.retrieve({"from": account}) == 10
