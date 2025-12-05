import pytest
import load_data


# Testing to see if it would raise a value error in our function
# Would not test the passing because it would return the .env file
# Failure test case
def test_get_engine_value_error():

    # Arrange
    engine = 'Other'

    # Act stage of calling the function
    with pytest.raises(ValueError) as ex:
        engine_name = load_data.get_engine(engine)

    # Assert
    assert str(ex.value) == f"{engine} not found in .env file"


# Must be inside the correct folder before the test.
# Must be in group2finalproject folder in terminal.
# Pass test case
def test_list_data_files_pass():
    # Arrange
    files = 'data'

    # Act - calling the function
    file_list = load_data.list_data_files(files)

    # Assert the number of files returned is actually the same amount
    # Makes sure that there are only two files, .json and .csv. If there are more, even if its one of correct file types, this test will fail
    assert len(file_list) == 2

# Failure test case
def test_load_selected_file_out_of_choice():
    # Arrange
    files = 'data'
    
    # Act - calling the function
    file_list = load_data.list_data_files(files)
    index = len(file_list) + 1

    with pytest.raises(IndexError) as ex:
        file_list = load_data.load_selected_file(file_list, index, files)
    
    # Assert the number of files returned is actually the same amount
    assert ex.type is IndexError

# Pass test case where it changes the string to a number value we can use
def test_normalize_damage_cols_pass():
    # Arrange
    # Making a fake dataframe to pass through the test case
    import pandas as pd
    from pandas.testing import assert_frame_equal
    test_list_prop = ['3.50K', '1.50B', '2.50M']
    test_list_crop = ['3.30K', '1.50K', '2.50']
    df = pd.DataFrame(list(zip(test_list_prop,test_list_crop)),
                      columns = ["DAMAGE_PROPERTY", "DAMAGE_CROPS"])
    
    expected = pd.DataFrame({
        "DAMAGE_PROPERTY": [3500,1500000000,2500000],
        "DAMAGE_CROPS": [3300,1500,2.50]})
    
    print(expected)
    # Act
    returned = load_data.normalize_damage_cols(df)
    print(returned)
    # Assert
    assert assert_frame_equal(expected,returned,check_dtype=False) == None


# Pass test case where it returns the rows where all coord columns are null
def test_split_clean_invalid_pass():

    # Arrange
    
    import pandas as pd
    import numpy as np
    test_case = pd.DataFrame({
        "BEGIN_AZIMUTH" : [1,1,np.nan,3],
        "BEGIN_LOCATION" : [2,2,np.nan,5],
        "BEGIN_RANGE":[1,1,np.nan,3],
        "END_RANGE":[1,1,np.nan,3],
        "END_AZIMUTH":[1,1,np.nan,3],
        "BEGIN_LON":[1,1,np.nan,3],
        "BEGIN_LAT":[1,1,np.nan,3],
        "END_LOCATION":[1,1,np.nan,3],
        "END_LON":[1,1,np.nan,3],
        "END_LAT":[1,1,np.nan,3],
    })

    # Act
    _, _, count = load_data.split_clean_invalid(test_case)


    # Assert
    # Only one row was cleanned out
    assert count == 1

# Pass case for filling in the NAN values of certian columns
def test_missing_values_returned_filled():
    import pandas as pd
    import numpy as np
    from pandas.testing import assert_frame_equal
    # Arrange the dataframes of what we are testing,
    # and what we expect to come back
    test_case = pd.DataFrame({
        "MAGNITUDE" : [np.nan,3],
        "DAMAGE_CROPS": [400, np.nan],
        "DAMAGE_PROPERTY" : [np.nan, 200],
        "FLOOD_CAUSE" : ["Large Rain", np.nan],
        "MAGNITUDE_TYPE" : [np.nan, "Very strong"],
    })

    expected = pd.DataFrame({
        "MAGNITUDE" : [0,3],
        "DAMAGE_CROPS": [400, 0],
        "DAMAGE_PROPERTY" : [0, 200],
        "FLOOD_CAUSE" : ["Large Rain", "N/A"],
        "MAGNITUDE_TYPE" : ["N/A", "Very strong"],
    })
    # Act
    returned = load_data.fill_missing_values(test_case)
    # Assert that the NA columns were dealt with
    assert assert_frame_equal(expected,returned,check_dtype=False) == None

# Checking if build_clean_df actually drops the right columns
def test_build_clean_df_drops_unwanted_columns():
    import pandas as pd
    from load_data import build_clean_df, COLS_TO_DROP

    # Arrange: df with a mix of droppable + keepable columns
    df = pd.DataFrame({
        "EVENT_ID": [1, 2],
        "STATE": ["TX", "OK"],
        "TOR_OTHER_WFO": ["X", "Y"],       # should be dropped
        "EPISODE_NARRATIVE": ["a", "b"],   # should be dropped
    })

    # Act
    df_clean = build_clean_df(df)

    # Assert: all COLS_TO_DROP that were present must be gone
    for col in COLS_TO_DROP:
        assert col not in df_clean.columns

    # And original "good" columns must remain
    assert "EVENT_ID" in df_clean.columns
    assert "STATE" in df_clean.columns

# Test analyze_nulls returns correct counts
def test_analyze_nulls_basic():
    import pandas as pd
    import numpy as np
    from load_data import analyze_nulls

    # Arrange
    df = pd.DataFrame({
        "A": [1, np.nan, 3],
        "B": [np.nan, np.nan, 5],
        "C": [7, 8, 9],  # no nulls
    })

    # Act
    remaining_nonzero, total_nulls, rows_with_null = analyze_nulls(df)

    # Assert per-column nulls (only nonzero are returned)
    assert remaining_nonzero["A"] == 1   # one NaN in A
    assert remaining_nonzero["B"] == 2   # two NaNs in B
    assert "C" not in remaining_nonzero  # 0 nulls => excluded

    # Assert totals
    assert total_nulls == 3              # 1 + 2
    assert rows_with_null == 2           # first two rows have NaNs

# Extra edge-case test for normalize_damage_cols
def test_analyze_nulls_basic():
    import pandas as pd
    import numpy as np
    from load_data import analyze_nulls

    # Arrange
    df = pd.DataFrame({
        "A": [1, np.nan, 3],
        "B": [np.nan, np.nan, 5],
        "C": [7, 8, 9],  # no nulls
    })

    # Act
    remaining_nonzero, total_nulls, rows_with_null = analyze_nulls(df)

    # Assert per-column nulls (only nonzero are returned)
    assert remaining_nonzero["A"] == 1   # one NaN in A
    assert remaining_nonzero["B"] == 2   # two NaNs in B
    assert "C" not in remaining_nonzero  # 0 nulls => excluded

    # Assert totals
    assert total_nulls == 3              # 1 + 2
    assert rows_with_null == 2           # first two rows have NaNs
