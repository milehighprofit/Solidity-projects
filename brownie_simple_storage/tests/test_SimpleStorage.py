from brownie import SimpleStorage, accounts

def test_deploy():
    #arrange
    account = accounts[0]
    #act
    simple_storage = SimpleStorage.deploy({'from': account})
    starting_value = simple_storage.retrieve()
    expected_value = 0
    #assert
    assert starting_value==expected_value


def updated_storage():
    #arrange
    account = accounts[0]
    #act
    simple_storage = SimpleStorage.deploy({'from': account})
    expected = 15
    simple_storage.store(expected, {'from': account})
    #assert
    assert expected == simple_storage.retrieve()

