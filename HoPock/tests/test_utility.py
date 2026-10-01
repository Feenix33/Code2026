from utility import clean_recipe_strings


def test_clean_recipe_strings_keeps_space_between_fraction_and_unit():
    values = ["½ tsp sugar", "1/2 cup milk", "3 tbsp oil"]

    cleaned = clean_recipe_strings(values)

    assert cleaned == ["1/2 tsp sugar", "1/2 c milk", "3 tbsp oil"]


def test_clean_recipe_strings_handles_variants_generically():
    values = ["¼ cups flour", "2tsp salt", "1½ oz pepper"]

    cleaned = clean_recipe_strings(values)

    assert cleaned == ["1/4 c flour", "2 tsp salt", "1 1/2 oz pepper"]
