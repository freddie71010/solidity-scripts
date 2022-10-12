import pytest
from brownie import Box, BoxV2, BoxV3, Contract, ProxyAdmin, TransparentUpgradeableProxy
from scripts.utils import encode_function_data, get_account, upgrade_contract


def test_proxy_delegate_calls_boxv3():
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

    # Deploy Box V3
    box_v3_contract = BoxV3.deploy({"from": account})
    # Upgrade Implementation Contract to new Box V3 address
    upgrade_contract(
        account,
        proxy_contract,
        box_v3_contract.address,
        proxy_admin=proxy_admin,
        # *initializer,
    )

    proxy_box_v3_contract = Contract.from_abi(
        "BoxV3", proxy_contract.address, box_v3_contract.abi
    )

    # Act
    proxy_box_v3_contract.emptyNumArray({"from": account})

    # Assert
    assert proxy_box_v3_contract.getNumArray() == []

    # Act
    proxy_box_v3_contract.store(22, {"from": account})
    proxy_box_v3_contract.store(10, {"from": account})
    proxy_box_v3_contract.store(40, {"from": account})
    proxy_box_v3_contract.increment({"from": account})
    proxy_box_v3_contract.increment({"from": account})
    last_resetarray_event = (
        proxy_box_v3_contract.events.ArrayTotalBeforeReset.createFilter(
            fromBlock=0
        ).get_all_entries()[-1]
    )
    array_total = last_resetarray_event.args.total

    # Assert
    assert array_total == (22 + 10 + 40 + 41 + 42)
