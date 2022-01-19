from brownie import SimpleStorage, accounts


def test_deploy():
    # Arrange
    account = accounts[0]
    # Act
    simple_storage = SimpleStorage.deploy({"from": account})
    starting_value = simple_storage.retrieve()
    expected_value = 0
    # Assert
    assert starting_value == expected_value


def test_updating_storage():
    # Arrange
    account = accounts[0]
    # Act
    simple_storage = SimpleStorage.deploy({"from": account})
    simple_storage.store(15, {"from": account})
    expected_value = 15
    # Assert
    assert simple_storage.retrieve() == expected_value
