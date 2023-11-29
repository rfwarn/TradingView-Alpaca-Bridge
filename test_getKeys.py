from getKeys import getKeys
import pytest

def test_get_paper_keys():
    keys = getKeys("paperTrading")   
    assert keys["api_key"] != None
    assert keys["secret_key"] != None
    assert keys["paper"] == True

def test_get_real_keys():
    keys = getKeys("realTrading")
    assert keys["api_key"] != None
    assert keys["secret_key"] != None
    assert keys["paper"] == False

def test_invalid_account():
    with pytest.raises(NameError):
        getKeys("invalid")
        
if __name__ == '__main__':
    test_get_paper_keys()
    test_get_real_keys()
    test_invalid_account()