from mage_ai.io.file import FileIO
from pandas import DataFrame

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_file(df: DataFrame, ff, **kwargs) -> None:
    """
    Template for exporting data to filesystem.

    Docs: https://docs.mage.ai/design/data-loading#fileio
    """
    import os
    cwd = os.getcwd()
    print(cwd)

    filepath = ff['csv']
    FileIO().export(df, filepath)
    import os
    print(os.path.dirname(filepath), df, filepath)