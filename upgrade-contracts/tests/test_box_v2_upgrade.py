import pytest
from brownie import Box, BoxV2, Contract, ProxyAdmin, TransparentUpgradeableProxy
from scripts.utils import encode_function_data, get_account, upgrade_contract


def test_proxy_delegate_calls_boxv2():
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
    # Assert
    with pytest.raises(AttributeError):
        proxy_box_contract.increment({"from": account})

    # Act
    box_v2_contract = BoxV2.deploy({"from": account})
    proxy_box_v2_contract = Contract.from_abi(
        "BoxV2", proxy_contract.address, box_v2_contract.abi
    )
    upgrade_contract(
        account,
        proxy_contract,
        box_v2_contract.address,
        proxy_admin=proxy_admin,
    )
    proxy_box_v2_contract.increment({"from": account})

    # Assert
    assert proxy_box_v2_contract.retrieve({"from": account}) == 1
