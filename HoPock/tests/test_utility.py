from utility import clean_recipe_strings, get_first_word, split_first_word


def test_clean_recipe_strings_keeps_space_between_fraction_and_unit():
    values = ["½ tsp sugar", "1/2 cup milk", "3 tbsp oil"]

    cleaned = clean_recipe_strings(values)

    assert cleaned == ["1/2 tsp sugar", "1/2 c milk", "3 tbsp oil"]


def test_clean_recipe_strings_handles_variants_generically():
    values = ["¼ cups flour", "2tsp salt", "1½ oz pepper"]

    cleaned = clean_recipe_strings(values)

    assert cleaned == ["1/4 c flour", "2 tsp salt", "1 1/2 oz pepper"]


def test_split_first_word_preserves_quoted_phrase_as_one_token():
    assert split_first_word('"--input <file>" The configuration input file') == (
        "--input <file>",
        "The configuration input file",
    )


def test_get_first_word_returns_quoted_phrase_without_quotes():
    assert get_first_word('"--input <file>" The configuration input file') == (
        "--input <file>"
    )
