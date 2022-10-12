from brownie import (
    Box,
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
    get_publish_source,
)

load_dotenv()

# Global
account = get_account()


def deploy_box_initializer_ex():
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

    # ============================================================================
    # encoded_function_data is required even if contains 0 parameters
    initializer = box_contract.store, 22
    box_encoded_initializer_func: bytes = encode_function_data(*initializer)
    # ============================================================================

    # Deploy TransparentUpgradeableProxy
    proxy_contract: network.contract.ProjectContract = (
        TransparentUpgradeableProxy.deploy(
            box_contract.address,
            proxy_admin.address,
            box_encoded_initializer_func,
            {"from": account, "gas_limit": 1_000_000},
        )
    )
    print_line(f"Proxy deployed to {proxy_contract}")

    # Make all calls to 'Box' via proxy_box_contract
    proxy_box_contract: network.contract.Contract = Contract.from_abi(
        "Box", proxy_contract.address, box_contract.abi
    )

    # ============================================================================
    # Will print out 22
    print_line(
        f"proxy_box_contract - retrieve: {proxy_box_contract.retrieve()}", char="*"
    )
    # ============================================================================

    proxy_box_contract.store(10, {"from": account})
    print_line(
        f"proxy_box_contract - retrieve: {proxy_box_contract.retrieve()}", char="*"
    )

    return


def main():
    deploy_box_initializer_ex()
