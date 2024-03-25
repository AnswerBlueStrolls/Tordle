from Tordle.utils.characters import replace_all_possible_name

def test_replace_all_possible_name():
    result = replace_all_possible_name("Eichi", "Allen", "E-Eichi-san please fuck Eichi.")
    assert result == "Allen please fuck Allen."