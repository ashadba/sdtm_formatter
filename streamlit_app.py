import webapp as wa
import streamlit as st
import pandas as pd
import numpy as np
import functions as fun
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

pd.set_option('display.max_columns', None)

st.title('Arkana Labs - SDTM Data Formatter')



data_df = pd.DataFrame()
with st.sidebar:
    section = st.sidebar.radio('Select an option:  ', ('SDTM Data Mapper', 'Redcap'))

if section == 'SDTM Data Mapper':
    sponsor_data = fun.get_sponsor()
    uploaded_file = st.file_uploader("Upload data file")

    if uploaded_file is not None:
        data_df = fun.read_file(sponsor_data, uploaded_file)
        # Uncomment display_df to test
        #fun.display_df(data_df)
        st.header("Formatting study data \n")
        data_df = fun.format_df(sponsor_data, data_df)
        # Uncomment display_df to test
        #fun.display_df(data_df)
        data_df = fun.concat_renal(sponsor_data, data_df)
        data_df = fun.apply_visit(sponsor_data, data_df)
        # Uncomment display_df to test
        #fun.display_df(data_df)
        data_df = fun.format_rnd(sponsor_data, data_df)
        #st.header("Exported Redcap study data - Ready to merge to SDTM")
        #fun.display_df(data_df)
        st.header("Creating DBSPEC and SDTM dataframes \n")
        sdtm = fun.create_sdtm(sponsor_data, data_df)
        #st.header("Exported study data - formatted for SDTM")
        #fun.display_df(data_df)
        dbspec = fun.create_dbspec(sponsor_data)
        #st.header("Imported DBSPEC")
        #fun.display_df(dbspec)
        # st.header("Exported study data - formatted for SDTM")
        st.header("Melting columns for SDTM \n")
        sdtm = fun.melt_columns(sponsor_data, data_df, dbspec, sdtm)
        #Uncomment display_df to test
        #fun.display_df(sdtm)
        sdtm = fun.add_columns(sponsor_data, sdtm)
        # Uncomment display_df to test
        #fun.display_df(sdtm)
        st.header("Applying filters \n")
        sdtm = fun.apply_filters(sponsor_data, sdtm)
        # Uncomment display_df to test
        #fun.display_df(sdtm)
        sdtm = fun.prepare_for_export(sponsor_data, sdtm)
        # Uncomment display_df to test

        st.header("Formated for SDTM - Ready for export")
        fun.display_df(sdtm)
        csv_file_name = fun.get_file_name(sponsor_data)
        fun.download_sdtm(sponsor_data, sdtm, csv_file_name)


elif section == 'Redcap':
    wa.get_redcap_urls()