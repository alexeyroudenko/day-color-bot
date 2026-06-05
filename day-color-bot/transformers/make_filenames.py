from mage_ai.data_cleaner.transformer_actions.base import BaseAction
from mage_ai.data_cleaner.transformer_actions.constants import ActionType, Axis
from mage_ai.data_cleaner.transformer_actions.utils import build_transformer_action
from pandas import DataFrame

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def make_filenames():  
    fnames = {}
    import datetime
    file_base = datetime.datetime.now().strftime('%Y-%m-%d-%H')
    import pathlib
    out_folder = "./data/trends/"              
    fnames['csv'] = pathlib.PurePath(out_folder + file_base + ".csv").as_posix()
    fnames['src'] = pathlib.PurePath(out_folder + file_base + "_src.jpg").as_posix()
    fnames['pal'] = pathlib.PurePath(out_folder + file_base + "_pal.jpg").as_posix()
    fnames['col'] = pathlib.PurePath(out_folder + file_base + "_col.jpg").as_posix()
    fnames['som'] = pathlib.PurePath(out_folder + file_base + "_som.jpg").as_posix()
    fnames['spt'] = pathlib.PurePath(out_folder + file_base + ".jpg").as_posix()
    fnames['new'] = pathlib.PurePath(out_folder + "spot" + ".jpg").as_posix()
    return fnames

@transformer
def execute_transformer_action(df: DataFrame, *args, **kwargs) -> DataFrame:
    return make_filenames()


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
