# This function, merge_dataframes(df1, df2), is designed to merge two pandas DataFrames based on a common column ('URL') and then reorder the columns according to a specified sequence.
import pandas as pd

def merge_dataframes(df1, df2):
    # Ensure the columns used for merging have the same name
    df2 = df2.rename(columns={'site': 'URL'})

    # Merge the two dataframes on 'URL'
    merged_df = pd.merge(df1, df2, on='URL', how='outer')

    # Define a new column order (put 'cms' column after 'URL' and then the email columns)
    new_order = ['URL', 'cms', 'Email 1', 'Email 2', 'Email 3', 'Email 4', 'Email 5']

    # Apply the new column order
    merged_df = merged_df.reindex(columns=new_order)

    merged_df.to_csv('merged_output.csv', index=False)