from brownie import (
    Box,
    BoxV2,
    BoxV3,
    Contract,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    network,
)
from dotenv import load_dotenv

from scripts.utils import (
    encode_function_data,
    get_account,
    print_line,
    upgrade_contract,
    get_publish_source,
)

load_dotenv()

# Global
account = get_account()


def deploy_box():
    """
    Deploy contracts:
    Implementation -> Box contract
    ProxyAdmin -> ProxyAdmin contract
    TransparentUpgradeableProxy -> TransparentUpgradeableProxy contract
    """
    # Deploy Box
    box_contract: network.contract.ProjectContract = Box.deploy(
        {"from": account}, publish_source=get_publish_source()
    )
    print(f"box_contract - retrieve: {box_contract.retrieve()}")

    # Deploy ProxyAdmin
    proxy_admin: network.contract.ProjectContract = ProxyAdmin.deploy(
        {"from": account}, publish_source=get_publish_source()
    )

    # encoded_function_data is required even if contains 0 parameters
    box_encoded_initializer_func: bytes = encode_function_data()

    # Deploy TransparentUpgradeableProxy
    proxy_contract: network.contract.ProjectContract = (
        TransparentUpgradeableProxy.deploy(
            box_contract.address,
            proxy_admin.address,
            box_encoded_initializer_func,
            {"from": account, "gas_limit": 1_000_000},
            publish_source=get_publish_source(),
        )
    )
    print_line(f"Proxy deployed to {proxy_contract}")

    # Make all calls to 'Box' via proxy_box_contract
    proxy_box_contract: network.contract.Contract = Contract.from_abi(
        "Box", proxy_contract.address, box_contract.abi
    )

    proxy_box_contract.store(24, {"from": account})
    print_line(
        f"proxy_box_contract - retrieve: {proxy_box_contract.retrieve()}", char="*"
    )
    return


def upgrade_to_boxV2():
    """Upgrade to BoxV2"""

    # Note: 'build/deployments/map.json' - saves info about contract deployments on live networks
    proxy_admin: network.contract.ProjectContract = ProxyAdmin[-1]
    proxy_contract: network.contract.ProjectContract = TransparentUpgradeableProxy[-1]

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
        # *initializer,
    )

    # Make all calls to 'BoxV2' via proxy_box_v2_contract
    proxy_box_v2_contract = Contract.from_abi(
        "BoxV2", proxy_contract.address, box_v2_contract.abi
    )

    proxy_box_v2_contract.increment({"from": account})
    print_line(
        f"proxy_box_v2_contract - retrieve: {proxy_box_v2_contract.retrieve()}",
        char="*",
    )


def upgrade_to_boxV3():
    """Upgrade to BoxV3"""

    # Note: 'build/deployments/map.json' - saves info about contract deployments on live networks
    proxy_admin: network.contract.ProjectContract = ProxyAdmin[-1]
    proxy_contract: network.contract.ProjectContract = TransparentUpgradeableProxy[-1]

    # Deploy Box V3
    box_v3_contract = BoxV3.deploy(
        {"from": account}, publish_source=get_publish_source()
    )

    # Upgrade Implementation Contract to new Box V3 address
    upgrade_contract(
        account,
        proxy_contract,
        box_v3_contract.address,
        proxy_admin=proxy_admin,
        # *initializer,
    )

    # Make all calls to 'BoxV3' via proxy_box_v3_contract
    proxy_box_v3_contract = Contract.from_abi(
        "BoxV3", proxy_contract.address, box_v3_contract.abi
    )

    # Perform actions on smart contract
    print_line(
        f"proxy_box_v3_contract - retrieve: {proxy_box_v3_contract.retrieve()}",
        char="*",
    )
    print_line(
        f"proxy_box_v3_contract - getNumArray: {proxy_box_v3_contract.getNumArray()}",
        char="*",
    )

    # Add values to 's_numArray'
    proxy_box_v3_contract.emptyNumArray({"from": account})
    print(proxy_box_v3_contract.getNumArray())
    proxy_box_v3_contract.store(22, {"from": account})
    print(proxy_box_v3_contract.getNumArray())
    proxy_box_v3_contract.store(10, {"from": account})
    print(proxy_box_v3_contract.getNumArray())
    proxy_box_v3_contract.store(40, {"from": account})
    print(proxy_box_v3_contract.getNumArray())
    proxy_box_v3_contract.increment({"from": account})
    print(proxy_box_v3_contract.getNumArray())
    proxy_box_v3_contract.increment({"from": account})

    # Print out event 'ArrayTotalBeforeReset' since 'ArrayMaxFive' modifier condition has been met.
    try:
        last_resetarray_event = (
            proxy_box_v3_contract.events.ArrayTotalBeforeReset.createFilter(
                fromBlock=0
            ).get_all_entries()[-1]
        )
        print(last_resetarray_event)
        print(f"Array Total Before Reset: {last_resetarray_event.args.total}")
    except Exception as e:
        print("No event found.")


def main():
    deploy_box()
    upgrade_to_boxV2()
    upgrade_to_boxV3()
