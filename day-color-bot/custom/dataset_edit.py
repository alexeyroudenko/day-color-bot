if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def transform_custom(*args, **kwargs):
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    print(args[0])
    # Specify your custom logic here
    imgs = args[0]
    for img in imgs:
        print(img[0])
        f = open(img[0], encoding="utf8", errors='ignore')
        data = f.read()
        plate = data.split(';')
        print(plate)


    return imgs


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
