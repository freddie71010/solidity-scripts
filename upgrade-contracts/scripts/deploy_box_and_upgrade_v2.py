from brownie import Box, BoxV2, Contract, ProxyAdmin, TransparentUpgradeableProxy
from dotenv import load_dotenv

from scripts.utils import (
    encode_function_data,
    get_account,
    print_line,
    upgrade_contract,
    get_publish_source,
)

load_dotenv()


def deploy_box_and_upgrade_v2():
    account = get_account()
    # Deploy Box
    box_contract = Box.deploy({"from": account}, publish_source=get_publish_source())
    print(f"box_contract - retrieve: {box_contract.retrieve()}")

    # Deploy ProxyAdmin
    proxy_admin = ProxyAdmin.deploy(
        {"from": account}, publish_source=get_publish_source()
    )

    # initializer = box_contract.store, 1
    box_encoded_initializer_func = encode_function_data()

    # Deploy TransparentUpgradeableProxy
    proxy_contract = TransparentUpgradeableProxy.deploy(
        box_contract.address,
        proxy_admin.address,
        box_encoded_initializer_func,
        {"from": account, "gas_limit": 1_000_000},
    )

    print_line(f"Proxy deployed to {proxy_contract}")

    proxy_box_contract = Contract.from_abi(
        "Box", proxy_contract.address, box_contract.abi
    )
    proxy_box_contract.store(10, {"from": account})
    print_line(
        f"proxy_box_contract - retrieve: {proxy_box_contract.retrieve()}", char="*"
    )

    # Deploy Box V2
    box_v2_contract = BoxV2.deploy(
        {"from": account}, publish_source=get_publish_source()
    )

    # Upgrade Implementation Contract to new Box V2 address
    upgrade_contract(
        account,
        proxy_contract,
        box_v2_contract.address,
        proxy_admin=proxy_admin,
    )

    proxy_box_v2_contract = Contract.from_abi(
        "BoxV2", proxy_contract.address, box_v2_contract.abi
    )
    proxy_box_v2_contract.increment({"from": account})
    print_line(
        f"proxy_box_v2_contract - retrieve: {proxy_box_v2_contract.retrieve()}",
        char="*",
    )


def main():
    deploy_box_and_upgrade_v2()
