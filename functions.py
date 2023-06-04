import streamlit as st
import pandas as pd
import numpy as np
import warnings


def display_df(df):
    # Added astype(str) to resolve df display error when running streamlit
    df = df.astype(str)
    st.write(df)


def remove_non_numberics(s):
    import re
    return re.sub('[^0-9]+', '', s)


def get_sponsor():
    sponsors = ['Roche Remley', 'Roche Majesty']
    sponsors.sort()
    markers = ['LN', 'IGAN', 'Biomarkers']
    marker_choice = 'no'
    sponsor_option = st.selectbox('Which sponsor?', sponsors)

    if (sponsor_option == 'ALXN1210-NEPH-202') | (sponsor_option == 'ALXN1210-NEPH-201'):
        marker_choice = st.selectbox('Which marker?', markers)
    sponsor_data = [sponsor_option, marker_choice]
    return sponsor_data


def read_file(sponsor_data, data_file):
    # data_file = st.file_uploader("Choose the study exported data file (excel format).")

    if data_file is not None:
        if sponsor_data[0] == 'Roche Remley':
            dtype_dic = {'TONUMSEG': str,
                         'GL_PREIS': str,
                         'TONUMSCP': str,
                         'IND_TOSC': str,
                         'CHROINTS': str,
                         'RQPATNUM:': str,
                         'RQCOVID:': str,
                         'RQREQNO': str,
                         }

            df = pd.read_csv(data_file,
                             dtype=dtype_dic,
                             na_filter=False,
                             #keep_default_na=True,
                             parse_dates=["RQLBDAT", 'DTREC', ])

            return df
        elif sponsor_data[0] == 'Roche Majesty':
            df = pd.read_csv(data_file,
                             converters={'Subject': str,
                                         'RQPATNUM:': str,
                                         'RQCOVID:': str,
                                         'TONUMSEG': str,
                                         'GL_PREIS': str,
                                         'TONUMSCP': str,

                                         },

                             parse_dates=["RQLBDAT", 'DTREC', ])
            return df


def format_df(sponsor_data, study_df):
    if sponsor_data[0] == 'Roche Remley':

        # Drop data from data frame that is not completed
        columns = ['requisition_complete', 'lupus_nephritis_complete']

        # Drop incomplete data rows
        index_empty_space = study_df[
            (study_df['lupus_nephritis_complete'] == '') | (study_df['requisition_complete'] == '')].index
        study_df.drop(index_empty_space, inplace=True)
        study_df.reset_index(drop=True, inplace=True)

        # Copy dataframe to prevent slicing
        study_df = study_df.copy()

        # Convert string to int
        study_df[columns] = study_df[columns].astype('Int64')

        # Drop incomplete data rows
        index_not_complete = study_df[
            (study_df['lupus_nephritis_complete'] < 2) | (study_df['requisition_complete'] < 2) | (
                    study_df['lupus_nephritis_complete'] == '')
            | (study_df['requisition_complete'] == '')].index
        study_df.drop(index_not_complete, inplace=True)
        study_df.reset_index(drop=True, inplace=True)

        # Rename columns
        study_df = (study_df.rename(columns=
                                    {'RQPATNUM': 'PATNUM',
                                     'Event Name': 'VISIT',
                                     'RQREQNO': 'ACCSNM',
                                     'RQLBSPEC': 'MISPEC',
                                     'RQLBDAT': 'MCFD',
                                     'EVFREAS01': 'LBLOC_RND',
                                     'EVFRESC2': 'LBLOC_OTHER',
                                     'EVFRESC1': 'ISNRPS_OTHER',
                                     'EVALPERM___0': 'EV_LM',
                                     'EVALPERM___1': 'EV_IF',
                                     'EVALPERM___2': 'EV_EM',
                                     'EVALPERM___4': 'EV_ND',
                                     'LNFREASO01': 'EV_RND',
                                     'LMFREAS0': 'COMPLM_RND',
                                     'IFFREAS1': 'COMPIF_RND',
                                     'EMFREAS0': 'COMPEM_RND',
                                     'PATHNAME': 'MIEVAL',
                                     'DTREC': 'MCFTD',
                                     'RQCOVID': 'MIREFID',
                                     'RENAL': 'LBLOC',

                                     }))

        # Add sponsor study data to df
        study_df["STUDYID"] = "YA42816"
        study_df["MINAM"] = "ARKA"

        # Fill in missing values with empty string
        study_df = study_df.fillna('')

        return study_df

    elif sponsor_data[0] == 'Roche Majesty':
        study_df = (study_df
        .rename(
            columns={'RQPATNUM': 'PATNUM',
                     "Event Name": "VISIT",
                     'RQCOVID:': "MIREFID",
                     "RQREQNO": "ACCSNM",
                     'RQLBSPEC(1)': "MISPEC",
                     'RQLBDAT': "MCFD",
                     'RENAL': "LBLOC",
                     'EVFREAS01': 'LBLOC_RND',
                     'EVFRESC2': "LBLOC_OTHER",
                     'EVALPERM___0': "EV_LM",
                     'EVALPERM___1': "EV_IF",
                     'EVALPERM___2': "EV_EM",
                     'EVALPERM___4': "EV_ND",
                     'LNFREASO01': 'EV_RND',
                     'LMFREAS0': "COMPLM_RND",
                     "IFFREAS1": "COMPIF_RND",
                     "EMFREAS0": 'COMPEM_RND',
                     'PATHNAME': 'MIEVAL',
                     'RQREQNO': 'MIREFID',
                     'DTREC': 'MCFTD',
                     }))

        # Delete data that is not ready to send to sponsor
        # delete null completed data rows
        study_df = study_df.dropna(subset=['requisition_complete', 'membranous_nephropathy_complete'])

        columns = ['membranous_nephropathy_complete', 'requisition_complete']
        study_df = study_df.copy()
        study_df["requisition_complete"] = study_df["requisition_complete"].astype('Int64')
        study_df["membranous_nephropathy_complete"] = study_df["membranous_nephropathy_complete"].astype('Int64')

        study_df = study_df.copy()
        index_not_complete = study_df[
            (study_df['membranous_nephropathy_complete'] < 2) | (study_df['requisition_complete'] < 2) | (
                    study_df['membranous_nephropathy_complete'] == '')
            | (study_df['requisition_complete'] == '')].index
        study_df.drop(index_not_complete, inplace=True)
        study_df.reset_index(drop=True, inplace=True)
        study_df = study_df.drop(columns, axis=1)

        # Add new fields to study_df
        study_df["STUDYID"] = "WA41937"
        study_df["MINAM"] = "ARKA"
        study_df['ACCSNM'] = study_df['MIREFID']

        study_df = study_df.fillna('')
        return study_df


def concat_renal(sponsor_data, study_df):
    # Replace Other value in MIAINTP and ISNRPS
    if sponsor_data[0] == 'Roche Remley':
        study_df = study_df.copy()
        # Replace "Other" with empty string and Concatenate columns
        study_df['LBLOC'] = study_df['LBLOC'].replace('Other', '')
        study_df['LBLOC'] = study_df['LBLOC'] + study_df['LBLOC_OTHER']
        return study_df
    if sponsor_data[0] == 'Roche Majesty':
        return study_df


def get_visit_num(visit):
    if visit == "screening":
        return "SCRN"
    elif visit == 'Screening':
        return "SCRN"
    elif visit == "Unscheduled":
        return "UNSCH"
    elif visit == "unscheduled":
        return 'UNSCH'
    elif visit == "Week 76":
        return "W76"
    elif visit == 'week 76':
        return 'W76'
    elif visit == 'week_76':
        return 'W76'
    elif visit == 'Week_76':
        return 'W76'
    elif visit == "Week 104":
        return "W104"
    elif visit == 'week 104':
        return 'W104'
    elif visit == 'week_104':
        return 'W104'
    elif visit == 'Week_104':
        return 'W104'
    else:
        return "Error"


def apply_visit(sponsor_data, study_df):
    study_df = study_df.copy()
    study_df["VISIT_R"] = study_df["VISIT"].apply(get_visit_num)
    return study_df


def format_rnd(sponsor_data, study_df):
    if sponsor_data[0] == 'Roche Remley':
        # Req eval apply Reason not done
        rnd_columns = [x for x in study_df.columns[study_df.columns.str.contains('FREAS')]]

        # apply ND filter to study_df and merge to study_df study_df
        ev_lm = study_df["EV_LM"] == 0
        ev_if = study_df["EV_IF"] == 0
        ev_em = study_df["EV_EM"] == 0
        ev_nd = study_df['EV_ND'] == 1

        # Populate RND for all coulumns if nothing can be scored from Req CRF
        study_df.loc[ev_lm & ev_if & ev_em, rnd_columns] = study_df["EV_RND"]
        study_df.loc[ev_lm & ev_if & ev_em, "COMPLM_RND"] = study_df["EV_RND"]
        study_df.loc[ev_lm & ev_if & ev_em, "COMPIF_RND"] = study_df["EV_RND"]
        study_df.loc[ev_lm & ev_if & ev_em, "COMPLM_RND"] = study_df["EV_RND"]

        # Add LMFREAS - RND columns to lm_study_df dataframe
        cols_to_fill = [x for x in study_df.columns if x.startswith("LMFREAS")]

        # apply ND filter to study_df and merge to study_df study_df
        ND = study_df["EV_LM"] == 0
        LM_ND = study_df["COMPLM"] == "Not done"
        study_df = study_df.copy()
        study_df.loc[ND, cols_to_fill] = study_df["EV_RND"]
        study_df.loc[ND, 'COMPLM_RND'] = study_df["EV_RND"]
        study_df.loc[LM_ND, cols_to_fill] = study_df["COMPLM_RND"]

        # Add IFFREAS - RND columns to IF_study_df dataframe
        cols_to_fill = [x for x in study_df.columns if x.startswith("IFFREAS")]

        # apply ND filter to study_df and merge to ln study_df
        ND = study_df["EV_IF"] == 0
        IF_ND = study_df["COMPIF"] == "Not done"
        study_df = study_df.copy()
        study_df.loc[ND, cols_to_fill] = study_df["EV_RND"]
        study_df.loc[ND, 'COMPIF_RND'] = study_df["EV_RND"]
        study_df.loc[IF_ND, cols_to_fill] = study_df["COMPIF_RND"]

        # Add EMFREAS - RND columns to EM_study_df dataframe
        cols_to_fill = [x for x in study_df.columns if x.startswith("EMFREAS")]

        # apply ND filter to study_df and merge to ln study_df
        ND = study_df["EV_EM"] == 0
        EM_ND = study_df["COMPEM"] == "Not Done"
        study_df = study_df.copy()
        study_df.loc[ND, cols_to_fill] = study_df["EV_RND"]
        study_df.loc[ND, 'COMPEM_RND'] = study_df["EV_RND"]
        study_df.loc[EM_ND, cols_to_fill] = study_df["COMPEM_RND"]
        return study_df

    elif sponsor_data[0] == 'Roche Majesty':
        # Evaluation section
        rnd_columns = [x for x in study_df.columns[study_df.columns.str.contains('FREAS')]]
        ev_columns = [x for x in study_df.columns[study_df.columns.str.contains('EVALRND')]]

        # #apply ND filter to study_df and merge to study_df study_df
        ev_lm = study_df["EV_LM"] == 0
        ev_if = study_df["EV_IF"] == 0
        ev_em = study_df["EV_EM"] == 0
        ev_nd = study_df['EV_ND'] == 1

        # Populate RND for all coulumns if nothing can be scored from Req CRF
        study_df.loc[ev_lm & ev_if & ev_em, rnd_columns] = study_df["EV_RND"]
        study_df.loc[ev_lm & ev_if & ev_em, ev_columns] = study_df["EV_RND"]
        study_df.loc[ev_lm & ev_if & ev_em, "LBLOC_RND"] = study_df["EV_RND"]
        study_df.loc[ev_lm & ev_if & ev_em, "COMPLM_RND"] = study_df["EV_RND"]
        study_df.loc[ev_lm & ev_if & ev_em, "COMPIF_RND"] = study_df["EV_RND"]
        study_df.loc[ev_lm & ev_if & ev_em, "COMPLM_RND"] = study_df["EV_RND"]

        # Add LMFREAS - RND columns to ev_study_df dataframe
        cols_to_fill = [x for x in study_df.columns if x.startswith("EVALRND")]

        # apply ND filter to study_df and merge to study_df study_df
        LM_ND = study_df["EV_LM"] == 0
        IF_ND = study_df["EV_IF"] == 0
        EM_ND = study_df["EV_EM"] == 0
        study_df = study_df.copy()
        study_df.loc[LM_ND & IF_ND & EM_ND, cols_to_fill] = study_df["EV_RND"]

        # LM section
        # Add LMFREAS - RND columns to lm_study_df dataframe
        cols_to_fill = [x for x in study_df.columns if x.startswith("LMFREAS")]

        # apply ND filter to study_df and merge to study_df study_df
        ND = study_df["EV_LM"] == 0
        LM_ND = study_df["COMPLM"] == "Not done"
        study_df = study_df.copy()
        study_df.loc[ND, cols_to_fill] = study_df["EV_RND"]
        study_df.loc[ND, 'COMPLM_RND'] = study_df["EV_RND"]
        study_df.loc[LM_ND, cols_to_fill] = study_df["COMPLM_RND"]

        # IF section
        # Add IFFREAS - RND columns to IF_study_df dataframe
        cols_to_fill = [x for x in study_df.columns if x.startswith("IFFREAS")]

        # apply ND filter to study_df and merge to ln study_df
        ND = study_df["EV_IF"] == 0
        IF_ND = study_df["COMPIF"] == "Not done"
        study_df = study_df.copy()
        study_df.loc[ND, cols_to_fill] = study_df["EV_RND"]
        study_df.loc[ND, 'COMPIF_RND'] = study_df["EV_RND"]
        study_df.loc[IF_ND, cols_to_fill] = study_df["COMPIF_RND"]

        # EM Section
        # Add EMFREAS - RND columns to EM_study_df dataframe
        cols_to_fill = [x for x in study_df.columns if x.startswith("EMFREAS")]

        # apply ND filter to study_df and merge to ln study_df
        ND = study_df["EV_EM"] == 0
        EM_ND = study_df["COMPEM"] == "Not Done"
        study_df = study_df.copy()
        study_df.loc[ND, cols_to_fill] = study_df["EV_RND"]
        study_df.loc[ND, 'COMPEM_RND'] = study_df["EV_RND"]
        study_df.loc[EM_ND, cols_to_fill] = study_df["COMPEM_RND"]
        return study_df


def create_sdtm(sponsor_data, study_df):
    if sponsor_data[0] == 'Roche Remley':
        # Create sdtm dataframe
        columns = ["STUDYID", 'Subject', "MINAM", "PATNUM", "EV_LM", "EV_IF", "EV_EM", 'EV_ND', 'EV_RND', 'COMPLM',
                   'COMPLM_RND', 'COMPIF', 'COMPIF_RND', 'COMPEM', 'COMPEM_RND', 'LBLOC', 'LBLOC_RND', 'VISIT_R',
                   'MCFD', 'MCFTD', "ACCSNM", "MIREFID",
                   'MIEVAL']

        sdtm = study_df[columns].copy()

        # rename VISIT_R to VISIT to match DTA
        sdtm.rename(columns={'VISIT_R': 'VISIT'}, inplace=True)

        # Add MIEVALID to sdtm study_df
        sdtm["MIEVALID"] = 'PATHOLOGIST 1'
        return sdtm

    elif sponsor_data[0] == 'Roche Majesty':
        # Create sdtm dataframe
        columns = ["STUDYID", 'Subject', "MINAM", "PATNUM", "EV_LM", "EV_IF", "EV_EM", 'EV_ND', 'EV_RND', 'COMPLM',
                   'COMPLM_RND', 'COMPIF', 'COMPIF_RND', 'COMPEM', 'COMPEM_RND', 'LBLOC', 'LBLOC_RND', 'VISIT_R',
                   'MCFD',
                   'MCFTD', "ACCSNM", "MIREFID", 'MIEVAL']

        sdtm = study_df[columns].copy()

        # rename VISIT_R to VISIT to match DTA
        sdtm.rename(columns={'VISIT_R': 'VISIT'}, inplace=True)

        # Add MIEVAL to SDTM df
        sdtm["MIEVALID"] = 'PATHOLOGIST 1'
        return sdtm


def create_dbspec(sponsor_data):
    import warnings
    if sponsor_data[0] == 'Roche Remley':
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            dbspec = pd.read_csv("files/DB_SPEC_REMELY.csv")
        dbspec = dbspec.fillna("")
        return dbspec
    elif sponsor_data[0] == 'Roche Majesty':
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            dbspec = pd.read_csv("files/DB_SPEC_MAJESTY.csv")
        dbspec = dbspec.fillna("")
        return dbspec


def melt_columns(sponsor_data, study_df, dbspec_df, sdtm_df):
    if sponsor_data[0] == 'Roche Remley':

        # Create df to map out results
        result_columns = ['Subject',
                          'ISNRPS',
                          'IND_TOSC',
                          'GLONEKAR',
                          'CHROINTS',
                          'GLOSCLR',
                          'LUP_VAS',
                          'GL_PREIS',
                          'TONUMSCP',
                          'TONUMSEG',
                          'ENDOHYP',
                          'MES_HY',
                          'HYA_DEP',
                          'FIBNECX2',
                          'CELFIBX2',
                          'GLO_CRE',
                          'INTIFL',
                          'INTFIBR',
                          'TUB_ATR',
                          'VAS_FI_A',
                          'ART_HY',
                          'THRO_MIC',
                          'GIGA_I',
                          'GIGA_P',
                          'GIGG_I',
                          'GIGG_P',
                          'GIGM_I',
                          'GIGM_P',
                          'GC3_I',
                          'GC3_P',
                          'GC1Q_I',
                          'GC1Q_P',
                          'GKAP_I',
                          'GKAP_P',
                          'GLAM_I',
                          'GLAM_P',
                          'TIGA_I',
                          'TIGG_I',
                          'TIGM_I',
                          'TC3_I',
                          'TC1Q_I',
                          'TKAP_I',
                          'TLAM_I',
                          'VIGA_I',
                          'VIGG_I',
                          'VIGM_I',
                          'VC3_I',
                          'VC1Q_I',
                          'VKAP_I',
                          'VLAM_I',
                          'MSNG_SC',
                          'SUEND_SC',
                          'SUBEPEM',
                          'PFPE']

        results_melt = study_df[result_columns].copy()

        # Melt columns to make MCFREAS column
        results_melt = pd.melt(results_melt, id_vars=['Subject'], var_name='LBTESTCD',
                               value_name='LBORRES').sort_values("Subject").reset_index()

        # drop added index column and merge to study_df study_df
        results_melt
        results_melt.drop(columns='index', axis=1, inplace=True)

        # Melt Comment columns

        other_columns = [x for x in study_df.columns[study_df.columns.str.contains('FRESC')]]
        other_columns.append('Subject')

        other_melt = study_df[other_columns].copy()

        # Melt columns to make MIAINTP column
        other_melt = pd.melt(other_melt, id_vars=['Subject'], var_name='OTHER_COLUMNS',
                             value_name='LBCOMM').sort_values("Subject").reset_index()
        other_melt.drop(columns='index', axis=1, inplace=True)

        # Melt columns to make MIREASND column
        rnd_cols = [x for x in study_df.columns[study_df.columns.str.contains('FREAS')]]
        rnd_cols.append('Subject')

        # Create rnd_melt study_df
        rnd_melt = study_df[rnd_cols].copy()

        rnd_melt = pd.melt(rnd_melt, id_vars=['Subject'], var_name='RND_COLUMNS', value_name='MIREASND').sort_values(
            "Subject").reset_index()
        rnd_melt.drop(columns='index', axis=1, inplace=True)

        # Merge melted results to ln study_df
        study_df = study_df.merge(results_melt, on='Subject', suffixes=(None, None))

        # Convert all versions of not done to ND
        sdtm_df = pd.merge(sdtm_df, study_df[['Subject', "LBTESTCD", "LBORRES"]], on='Subject', how='left',
                           suffixes=(None, None))
        filter_list = ['TONUMSEG', 'GL_PREIS', 'TONUMSCP', ]
        not_done = sdtm_df["LBORRES"].str.len() == 0
        Not_done = sdtm_df["LBORRES"] == "Not done"
        Not_Done = sdtm_df["LBORRES"] == "Not Done"

        sdtm_df.loc[not_done | Not_done | Not_Done, "LBORRES"] = "ND"

        # Merge study_df to sdtm_df
        sdtm_df = pd.merge(sdtm_df, dbspec_df, left_on="LBTESTCD", right_on="Results", how="left",
                           suffixes=(None, '_R')).sort_values(['Subject', "Row Number"]).reset_index()
        sdtm_df.drop(columns='index', axis=1, inplace=True)

        # Merge Comment column to sdtm_df
        sdtm_df = pd.merge(sdtm_df, other_melt, left_on=["Subject", "Other"], right_on=["Subject", "OTHER_COLUMNS"],
                           how="left", suffixes=(None, "_R")).sort_values(["Subject", "Row Number"]).reset_index()

        sdtm_df.drop(columns='index', axis=1, inplace=True)

        # Merge Reason Not done column to sdtm_df
        sdtm_df = pd.merge(sdtm_df, rnd_melt, left_on=["Subject", "Reason Not Done"],
                           right_on=["Subject", "RND_COLUMNS"],
                           how="left", suffixes=(None, '_R')).sort_values(["Subject", "Row Number"]).reset_index()
        sdtm_df.drop(columns='index', axis=1, inplace=True)
        sdtm_df = sdtm_df.fillna("")
        return sdtm_df

    elif sponsor_data[0] == 'Roche Majesty':
        # Create df to map out results
        result_columns = ['Subject',
                          'MNFIND',
                          'LNFIND',
                          'MNSECFIND',
                          'DNFIND',
                          'OTHER',
                          'ENDOHYP',
                          'MES_HYP',
                          'HYA_DEP',
                          'FIBNECX2',
                          'CELFIBX2',
                          'FIBCRE',
                          'INTIFL',
                          'INTFIBR',
                          'TUB_ATR',
                          'GL_PREIS',
                          'TONUMSCP',
                          'TONUMSEG',
                          'VAS_FI_A',
                          'ART_HY',
                          'THRO_MIC',
                          'PLA2R',
                          'THSD7A',
                          'ANTOTHER',
                          'GIGA_I',
                          'GIGA_P',
                          'GIGG_I',
                          'GIGG_P',
                          'GIGM_I',
                          'GIGM_P',
                          'GC3_I',
                          'GC3_P',
                          'GC1Q_I',
                          'GC1Q_P',
                          'GKAP_I',
                          'GKAP_P',
                          'GLAM_I',
                          'GLAM_P',
                          'TIGA_I',
                          'TIGG_I',
                          'TIGM_I',
                          'TC3_I',
                          'TC1Q_I',
                          'TKAP_I',
                          'TLAM_I',
                          'VIGA_I',
                          'VIGG_I',
                          'VIGM_I',
                          'VC3_I',
                          'VC1Q_I',
                          'VKAP_I',
                          'VLAM_I',
                          'MSNG_SC',
                          'SUEND_SC',
                          'SUBEPEM',
                          'TUBBASMEM',
                          'PFPE',
                          'LBLOC',
                          'COMPLM',
                          'COMPIF',
                          'COMPEM'
                          ]

        results_melt = study_df[result_columns].copy()

        # Melt columns to make MCFREAS column
        results_melt = pd.melt(results_melt, id_vars=['Subject'], var_name='LBTESTCD',
                               value_name='LBORRES').sort_values("Subject").reset_index()

        # drop added index column and merge to study_df study_df
        results_melt
        results_melt.drop(columns='index', axis=1, inplace=True)

        # Other Melt
        other_columns = [x for x in study_df.columns[study_df.columns.str.contains('FRESC')]]
        ev = [x for x in study_df.columns[study_df.columns.str.contains('EVALOTH')]]
        # other_columns =[x for x in study_df.columns[study_df.columns.str.contains('FRESC')]]

        other_columns.append('Subject')
        other_columns.append('LBLOC_OTHER')
        for column in ev:
            other_columns.append(column)

        other_melt = study_df[other_columns].copy()

        # Melt columns to make MIAINTP column
        other_melt = pd.melt(other_melt, id_vars=['Subject'], var_name='OTHER_COLUMNS',
                             value_name='LBCOMM').sort_values("Subject").reset_index()
        other_melt.drop(columns='index', axis=1, inplace=True)

        # RND - Reason Not done - Melt

        rnd_cols = [x for x in study_df.columns[study_df.columns.str.contains('FREAS')]]
        ev = [x for x in study_df.columns[study_df.columns.str.contains('EVALRND')]]

        rnd_cols.append('Subject')
        rnd_cols.append('LBLOC_RND')
        rnd_cols.append('COMPLM_RND')
        rnd_cols.append('COMPIF_RND')
        rnd_cols.append('COMPEM_RND')

        for column in ev:
            rnd_cols.append(column)

        # Create rnd_melt study_df
        rnd_melt = study_df[rnd_cols].copy()

        rnd_melt = pd.melt(rnd_melt, id_vars=['Subject'], var_name='RND_COLUMNS', value_name='MIREASND').sort_values(
            "Subject").reset_index()
        rnd_melt.drop(columns='index', axis=1, inplace=True)

        # Merge melted results to ln study_df
        study_df = study_df.merge(results_melt, on='Subject', suffixes=(None, None))

        # Merge results to sdtm_df
        sdtm_df = pd.merge(sdtm_df, study_df[['Subject', "LBTESTCD", "LBORRES"]], on='Subject', how='left',
                           suffixes=(None, None))
        filter_list = ['TONUMSEG', 'GL_PREIS', 'TONUMSCP', ]
        not_done = sdtm_df["LBORRES"].str.len() == 0
        ND = sdtm_df["LBORRES"] == "Not done"
        sdtm_df.loc[not_done, "LBORRES"] = "Not done"
        sdtm_df.loc[ND, "LBORRES"] = "Not done"

        # Merge sdtm_df and dbspec_df
        sdtm_df = pd.merge(sdtm_df, dbspec_df, left_on="LBTESTCD", right_on="Results", how="left",
                           suffixes=(None, '_R')).sort_values(['Subject', "Row Number"]).reset_index()
        sdtm_df.drop(columns='index', axis=1, inplace=True)

        # Merge Other columns to sdtm_df
        sdtm_df = pd.merge(sdtm_df, other_melt, left_on=["Subject", "Other"], right_on=["Subject", "OTHER_COLUMNS"],
                           how="left", suffixes=(None, "_R")).sort_values(["Subject", "Row Number"]).reset_index()

        sdtm_df.drop(columns='index', axis=1, inplace=True)
        sdtm_df = sdtm_df.fillna("")

        # Merge RND - Reason Not done - to sdtm_df
        sdtm_df = pd.merge(sdtm_df, rnd_melt, left_on=["Subject", "Reason Not Done"],
                           right_on=["Subject", "RND_COLUMNS"],
                           how="left", suffixes=(None, '_R')).sort_values(["Subject", "Row Number"]).reset_index()
        sdtm_df.drop(columns='index', axis=1, inplace=True)
        sdtm_df = sdtm_df.fillna("")
        return sdtm_df


def add_columns(sponsor_data, sdtm_df):
    if sponsor_data[0] == 'Roche Remley':
        sdtm_df['MISTAT'] = ''
        sdtm_df['MCFRESN'] = ''
        return sdtm_df
    elif sponsor_data[0] == 'Roche Majesty':
        sdtm_df['MISTAT'] = ''
        sdtm_df['MCFRESN'] = ''
        return sdtm_df


def apply_filters(sponsor_data, sdtm_df):
    if sponsor_data[0] == 'Roche Remley':
        filter_list = ['TONUMSEG', 'GL_PREIS', 'TONUMSCP', 'CHROINTS', 'IND_TOSC']
        cols_to_fill = ["MCFRESN"]

        zero = sdtm_df['LBORRES'] == 0
        ZERO = sdtm_df['LBORRES'] == '0'
        nd = sdtm_df['LBORRES'] == 'ND'

        # Populate MISTAT = ND
        sdtm_df.loc[nd, 'MISTAT'] = 'NOT DONE'

        # Blank LBORRES where  = ND
        sdtm_df.loc[nd, 'LBORRES'] = ''

        # populate MCFRESN where there is a number
        sdtm_df.loc[sdtm_df["LBTESTCD"].isin(filter_list) | zero | ZERO, 'MCFRESN'] = sdtm_df["LBORRES"]

        # apply values to LBORRES and MIREASND for COMP_LM, COMP_IF, and COMP_EM
        cols_to_fill = ["LBORRES"]
        col_not_done = ["MIREASND"]

        # Evaluation completed
        ev_lm = sdtm_df["EV_LM"] != 0
        ev_if = sdtm_df["EV_IF"] != 0
        ev_em = sdtm_df["EV_EM"] != 0

        # Evaluation not completed
        ev_lm_nd = sdtm_df["EV_LM"] == 0
        ev_if_nd = sdtm_df["EV_IF"] == 0
        ev_em_nd = sdtm_df["EV_EM"] == 0

        # Completed on the basis of:  LM, IF, and EM
        lm_nd = sdtm_df["COMPLM"] == 'Not done'
        if_nd = sdtm_df["COMPIF"] == 'Not done'
        em_nd = sdtm_df["COMPEM"] == 'Not Done'
        renal_nd = sdtm_df["LBLOC"] == "No renal tissue"

        # Convert Row Number to integer so it can be used for filtering
        sdtm_df['Row Number'] = sdtm_df['Row Number'].astype('Int64')

        # Filter on LM, IF, and EM sections
        seq_lm = sdtm_df["Row Number"].between(1, 21)
        seq_if = sdtm_df["Row Number"].between(22, 49)
        seq_em = sdtm_df["Row Number"].between(50, 53)
        seq_all = sdtm_df["Row Number"].between(1, 53)

        # Populate MISTAT if an evaluation section is selected Not done
        sdtm_df.loc[seq_lm & ev_lm_nd, 'MISTAT'] = 'NOT DONE'
        sdtm_df.loc[seq_if & ev_if_nd, 'MISTAT'] = 'NOT DONE'
        sdtm_df.loc[seq_em & ev_em_nd, 'MISTAT'] = 'NOT DONE'

        # Populate MIREASND for completed on the basis of RND
        sdtm_df.loc[lm_nd & seq_lm, col_not_done] = sdtm_df["COMPLM_RND"]
        sdtm_df.loc[lm_nd & seq_lm, 'MISTAT'] = 'NOT DONE'
        sdtm_df.loc[lm_nd & seq_lm, 'LBORRES'] = ''
        sdtm_df.loc[lm_nd & seq_lm, 'MCFRESN'] = ''

        sdtm_df.loc[if_nd & seq_if, col_not_done] = sdtm_df["COMPIF_RND"]
        sdtm_df.loc[if_nd & seq_if, 'MISTAT'] = 'NOT DONE'
        sdtm_df.loc[if_nd & seq_if, 'LBORRES'] = ''
        sdtm_df.loc[if_nd & seq_if, 'MCFRESN'] = ''

        sdtm_df.loc[em_nd & seq_em, col_not_done] = sdtm_df["COMPEM_RND"]
        sdtm_df.loc[em_nd & seq_em, 'MISTAT'] = 'NOT DONE'
        sdtm_df.loc[em_nd & seq_em, 'LBORRES'] = ''
        sdtm_df.loc[em_nd & seq_em, 'MCFRESN'] = ''

        # Populate MIREASND for evaluation RND
        sdtm_df.loc[ev_lm_nd & ev_if_nd & ev_em_nd, col_not_done] = sdtm_df["EV_RND"]
        sdtm_df.loc[ev_lm_nd & ev_if_nd & ev_em_nd, 'MISTAT'] = 'NOT DONE'
        sdtm_df.loc[ev_lm_nd & ev_if_nd & ev_em_nd, 'LBORRES'] = ''
        sdtm_df.loc[ev_lm_nd & ev_if_nd & ev_em_nd, 'MCFRESN'] = ''

        # Populate MIREASND for No renal tissue
        sdtm_df.loc[renal_nd, col_not_done] = sdtm_df["LBLOC_RND"]
        sdtm_df.loc[renal_nd, 'MISTAT'] = 'NOT DONE'
        sdtm_df.loc[renal_nd, 'LBORRES'] = ''
        sdtm_df.loc[renal_nd, 'MCFRESN'] = ''

        # Populate ISNRPS - Not done with default value due to form not having a Reason not done field
        isnrps_test = sdtm_df["LBTESTCD"] == "ISNRPS"
        nd = sdtm_df['LBORRES'] == 'Not done'
        ev_lm = sdtm_df['EV_LM'] == 1

        sdtm_df.loc[isnrps_test & nd & ev_lm, 'MIREASND'] = 'Not completed'
        sdtm_df.loc[isnrps_test & nd & ev_lm, 'MISTAT'] = 'NOT DONE'
        sdtm_df.loc[isnrps_test & nd & ev_lm, 'MCFRESN'] = ''
        sdtm_df.loc[isnrps_test & nd & ev_lm, 'LBORRES'] = ''

        # Populate MISTAT with ND and Blank LBORRES and MCFRESN where values = Not done or ND
        # Columns to blank
        nd = sdtm_df['LBORRES'] == 'ND'
        not_done = sdtm_df['LBORRES'] == 'Not done'
        NOT_DONE = sdtm_df['LBORRES'] == 'NOT DONE'
        Not_Done = sdtm_df['LBORRES'] == 'Not Done'
        blank_num = sdtm_df["MCFRESN"].str.len() > 0
        cols_to_fill = ["LBORRES", "MCFRESN"]

        sdtm_df.loc[nd | not_done | NOT_DONE | Not_Done, "MISTAT"] = 'NOT DONE'
        sdtm_df.loc[nd | not_done | NOT_DONE | Not_Done, cols_to_fill] = ''

        # Blank LBORRES where there is a number in MCFRESN
        sdtm_df.loc[blank_num, 'LBORRES'] = ''

        # Concatenate LBCOMM Other and LBLOC
        sdtm_df['LBCOMM'] = sdtm_df['LBCOMM'] + '|' + sdtm_df['LBLOC']
        sdtm_df.fillna("", inplace=True)

        # NA Values populate MISTAT and BLANK LBORRES
        na = sdtm_df['LBORRES'] == 'NA'

        sdtm_df.loc[na, 'MISTAT'] = 'NOT DONE'
        sdtm_df.loc[na, 'LBORRES'] = ''
        return sdtm_df

    elif sponsor_data[0] == 'Roche Majesty':
        nd = sdtm_df['LBORRES'] == 'Not done'
        ND = sdtm_df['LBORRES'] == 'ND'
        na = sdtm_df['MIREASND'] == "Not applicable"
        em_tbm_test = sdtm_df["LBTESTCD"] == "TUBBASMEM"
        mistat_nd = sdtm_df['MISTAT'] == 'ND'
        # test filters and results filters
        antother = sdtm_df["LBTESTCD"] == "ANTOTHER"
        other_test = sdtm_df["LBTESTCD"] == "OTHER"
        lborres_nd = sdtm_df["LBORRES"] == "ND"
        lborres_empty = sdtm_df['LBORRES'] == 'Not done'

        blank_num = sdtm_df["MCFRESN"] != ''

        # apply values to LBORRES and MIREASND for COMP_LM, COMP_IF, and COMP_EM
        cols_to_fill = ["LBORRES"]
        col_not_done = ["MIREASND"]
        filter_list = ['TONUMSEG', 'GL_PREIS', 'TONUMSCP', ]
        cols_to_fill_num = ["MCFRESN"]

        ev_lm = sdtm_df["EV_LM"] != 0
        ev_if = sdtm_df["EV_IF"] != 0
        ev_em = sdtm_df["EV_EM"] != 0

        ev_lm_nd = sdtm_df["EV_LM"] == 0
        ev_if_nd = sdtm_df["EV_IF"] == 0
        ev_em_nd = sdtm_df["EV_EM"] == 0
        ev_em_comp = sdtm_df['EV_EM'] == 1
        compem_not_nd = sdtm_df['COMPEM_RND'].str.len() == 0
        lm_nd = sdtm_df["COMPLM"] == 'Not done'
        if_nd = sdtm_df["COMPIF"] == 'Not done'
        em_nd = sdtm_df["COMPEM"] == 'Not Done'
        renal_nd = sdtm_df["LBORRES"] == "No renal tissue"

        # convert Row number to int for filtering
        sdtm_df['Row Number'] = sdtm_df['Row Number'].astype('Int64')

        seq_ev = sdtm_df["Row Number"].between(1, 23)
        seq_lm = sdtm_df["Row Number"].between(5, 23)
        seq_if = sdtm_df["Row Number"].between(24, 51)
        seq_em = sdtm_df["Row Number"].between(52, 56)
        seq_exam = sdtm_df["Row Number"].between(57, 60)
        seq_all = sdtm_df["Row Number"].between(1, 60)

        # Populate MIREASND
        sdtm_df.loc[lm_nd & seq_ev, col_not_done] = sdtm_df["COMPLM_RND"]
        sdtm_df.loc[if_nd & seq_if, col_not_done] = sdtm_df["COMPIF_RND"]
        sdtm_df.loc[em_nd & seq_em, col_not_done] = sdtm_df["COMPEM_RND"]
        sdtm_df.loc[renal_nd, col_not_done] = sdtm_df["LBLOC_RND"]
        sdtm_df.loc[ev_lm_nd & ev_if_nd & ev_em_nd & seq_all, "MIREASND"] = sdtm_df["EV_RND"]
        sdtm_df.loc[ev_lm_nd & ev_if_nd & ev_em_nd & seq_all, "MISTAT"] = 'ND'
        sdtm_df.loc[ev_lm_nd & ev_if_nd & ev_em_nd & seq_all, "LBORRES"] = ''
        sdtm_df.loc[ev_lm_nd & ev_if_nd & ev_em_nd & seq_all, "MCFRESN"] = ''
        sdtm_df.loc[lm_nd & seq_lm, "MIREASND"] = sdtm_df["COMPLM_RND"]
        sdtm_df.loc[if_nd & seq_if, "MIREASND"] = sdtm_df["COMPIF_RND"]
        sdtm_df.loc[em_nd & seq_em, "MIREASND"] = sdtm_df["COMPEM_RND"]
        sdtm_df.loc[antother & lborres_empty, "MIREASND"] = "Not applicable"
        sdtm_df.loc[other_test & lborres_empty, "MIREASND"] = "Not applicable"
        sdtm_df.loc[em_tbm_test & nd, 'MIREASND'] = 'Not completed'
        sdtm_df.loc[em_tbm_test & nd & ev_em_comp & compem_not_nd, 'MISTAT'] = 'ND'
        sdtm_df.loc[em_tbm_test & nd, 'LBORRES'] = ''

        # Set MISTAT
        sdtm_df.loc[na, "MISTAT"] = "ND"
        sdtm_df.loc[nd, 'MISTAT'] = 'ND'
        sdtm_df.loc[nd, 'MISTAT'] = 'ND'

        # populate MCFRESN where LBORRES = 0
        zero = sdtm_df['LBORRES'] == 0
        ZERO = sdtm_df['LBORRES'] == '0'

        # populate MCFRESN where there is a number
        sdtm_df.loc[sdtm_df["LBTESTCD"].isin(filter_list), 'MCFRESN'] = sdtm_df["LBORRES"]

        # Populate MCFRESN
        sdtm_df.loc[zero, 'MCFRESN'] = sdtm_df["LBORRES"]
        sdtm_df.loc[ZERO, 'MCFRESN'] = sdtm_df["LBORRES"]

        sdtm_df.loc[zero, 'LBORRES'] = ''
        sdtm_df.loc[ZERO, 'LBORRES'] = ''

        sdtm_df.fillna("", inplace=True)

        # Populate MISTAT with ND and Blank LBORRES and MCFRESN where values = Not done or ND
        # Columns to blank
        nd = sdtm_df['LBORRES'] == 'ND'
        not_done = sdtm_df['LBORRES'] == 'Not done'
        NOT_DONE = sdtm_df['LBORRES'] == 'NOT DONE'
        Not_Done = sdtm_df['LBORRES'] == 'Not Done'
        blank_num = sdtm_df["MCFRESN"].str.len() > 0
        emptpy_num = sdtm_df["LBORRES"].str.len() > 0

        # Apply ND to MISTAT and blank results columns
        cols_to_fill = ["LBORRES", "MCFRESN", 'LBCOMM']

        sdtm_df.loc[nd | not_done | NOT_DONE | Not_Done, "MISTAT"] = 'ND'
        sdtm_df.loc[nd | not_done | NOT_DONE | Not_Done, cols_to_fill] = ''

        # Set default value for Tubular basement membrane becuase form branching is not working properly.
        em_tbm_test = sdtm_df["LBTESTCD"] == "TUBBASMEM"
        nd = sdtm_df['LBORRES'] == 'Not done'
        sdtm_df.loc[em_tbm_test & nd, 'MIREASND'] = 'Not completed'
        ev_em = sdtm_df['EV_EM'] == 1
        compem_not_nd = sdtm_df['COMPEM_RND'].str.len() == 0
        sdtm_df.loc[em_tbm_test & nd & ev_em & compem_not_nd, 'MISTAT'] = 'ND'
        sdtm_df.loc[em_tbm_test & nd, 'LBORRES'] = ''

        # Blank LBORRES and MCFRESN where there is a number in MCFRESN
        cols_to_fill = ['LBORRES']
        sdtm_df.loc[blank_num, cols_to_fill] = ''
        # sdtm_df.loc[emptpy_num, "MCFRESN"]=''
        sdtm_df.fillna("", inplace=True)

        return sdtm_df


def prepare_for_export(sponsor_data, sdtm_df):
    if sponsor_data[0] == 'Roche Remley':
        sdtm_df = sdtm_df.copy()
        # drop columns not needed

        sdtm_df['MCFRESC'] = sdtm_df['LBORRES']

        # #add  missing sdtm_df columns as blank columns
        columns_to_add = ['MISPCCND', 'MCFTPT', 'MCFTM', 'MIMTDTL', 'MIOBJSCI', 'MIMRKSTR', 'MIOBJSCR', 'IPACCSNM']

        for column in columns_to_add:
            sdtm_df[column] = ""

        # Rename and add columns to match FFS
        sdtm_df['MIAINTP'] = sdtm_df['LBCOMM']
        sdtm_df['MISPEC'] = 'TISSUE'

        sdtm_df_columns_in_order = ["STUDYID", "MINAM", "PATNUM", 'VISIT', 'MCFTPT', 'MCFD', 'MCFTM', "ACCSNM",
                                    "IPACCSNM", "MIREFID", "MISPEC", 'MISPCCND', "MIMETHOD", 'MIMTDTL', 'MIOBJI',
                                    'MIMRKSTI', 'MIOBJLCI', 'MIOBJSCI', 'MIOBJR',
                                    'MIMRKSTR', 'MIOBJLCR', 'MIOBJSCR', 'MITESTCD', 'MITSTDTL', 'MCFRESN', 'MCFORESU',
                                    'MCFRESC', 'MISTAT', 'MIREASND', 'MIAINTP', 'MIEVAL', "MIEVALID"]

        sdtm_df = sdtm_df[sdtm_df_columns_in_order]

        # sdtm_df_df to UPPERCASE
        sdtm_df_columns_uppercase = ["STUDYID", "MINAM", "PATNUM", 'VISIT', 'MCFTPT', 'MCFD', 'MCFTM', "ACCSNM",
                                     "IPACCSNM", "MIREFID", "MISPEC", 'MISPCCND', "MIMETHOD", 'MIMTDTL', 'MIOBJI',
                                     'MIMRKSTI', 'MIOBJLCI', 'MIOBJSCI', 'MIOBJR',
                                     'MIMRKSTR', 'MIOBJLCR', 'MIOBJSCR', 'MITESTCD', 'MITSTDTL', 'MCFRESN', 'MCFORESU',
                                     'MISTAT', 'MIREASND', 'MIAINTP', 'MIEVAL', "MIEVALID"]

        sdtm_df[sdtm_df_columns_uppercase] = sdtm_df[sdtm_df_columns_uppercase].apply(
            lambda x: x.astype(str).str.upper())

        # format date for study date format
        sdtm_df["MCFD"] = pd.to_datetime(sdtm_df.MCFD, format='%Y-%m-%d')
        sdtm_df['MCFD'] = pd.to_datetime(sdtm_df.MCFD, format='%Y%m%d')
        sdtm_df['MCFD'] = sdtm_df['MCFD'].dt.strftime('%Y%m%d')

        # Fill in nan values to empty space
        sdtm_df.fillna("", inplace=True)
        return sdtm_df

    elif sponsor_data[0] == 'Roche Majesty':
        # drop columns not needed
        cols_to_drop = ['MCFD']
        sdtm_df.drop(columns=cols_to_drop, axis=1, inplace=True)
        sdtm_df['MCFRESC'] = sdtm_df['LBORRES']

        # #add  missing sdtm_df columns as blank columns
        columns_to_add = ['MISPCCND', 'MCFTPT', 'MCFTM', 'MIMTDTL', 'MITSTDTL', 'MIOBJSCI', 'MIMRKSTR', 'MIOBJSCR',
                          'MCFD', "MISPEC"]

        for column in columns_to_add:
            sdtm_df[column] = ""

        # Rename columns to match DTA

        sdtm_df = (sdtm_df
        .rename(
            columns={'LBCOMM': 'MIAINTP',
                     })
        )

        sdtm_df_columns_in_order = ["STUDYID", "MINAM", "PATNUM", 'VISIT', 'MCFTPT', 'MCFD', 'MCFTM', "ACCSNM",
                                    "MIREFID", "MISPEC", 'MISPCCND', "MIMETHOD", 'MIMTDTL', 'MIOBJI', 'MIMRKSTI',
                                    'MIOBJLCI', 'MIOBJSCI', 'MIOBJR', 'MIMRKSTR', 'MIOBJLCR', 'MIOBJSCR', 'MITESTCD',
                                    'MITSTDTL', 'MCFRESN', 'MCFORESU', 'MCFRESC', 'MISTAT', 'MIREASND', 'MIAINTP',
                                    'MIEVAL', "MIEVALID", "MCFTD"]

        sdtm_df = sdtm_df[sdtm_df_columns_in_order]

        # Format date column
        sdtm_df["MCFTD"] = pd.to_datetime(sdtm_df.MCFTD, format='%Y-%m-%d')
        sdtm_df['MCFTD'] = pd.to_datetime(sdtm_df.MCFTD, format='%Y%m%d')
        sdtm_df['MCFTD'] = sdtm_df['MCFTD'].dt.strftime('%Y%m%d')

        # Convert sdtm_df to UPPERCASE
        sdtm_df = sdtm_df.apply(lambda x: x.astype(str).str.upper())

        # Fill nan columns with empty space
        sdtm_df.fillna("", inplace=True)
        return sdtm_df


def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def download_sdtm(sponsor_data, sdtm_df):
    import datetime
    timestamp = pd.Timestamp(datetime.datetime(2021, 10, 10))
    current_date = timestamp.now()

    if sponsor_data[0] == 'Roche Remley':
        # Sponsor file naming convention for current FFS
        # YA42816_ARKA_MCF1_PROD_V3.0_YYYYMMDDHHMMSS.csv - {Production file}
        # YA42816_ARKA_MCF1_TEST_V3.0_YYYYMMDDHHMMSS.csv - {Test file}

        current_date = current_date.strftime('%Y%m%d%H%M%S').upper()
        file_name = "YA42816_ARKA_MCF1_PROD_V3.0_" + current_date + '.csv'
        csv = sdtm_df.to_csv(index=False).encode("utf-8")

    elif sponsor_data[0] == 'Roche Majesty':
        # Sponsor file naming convention for current FFS
        # WA41937_ARKA_MCF1_PROD_V4.0_YYYYMMDDHHMMSS.csv
        # WA41937_ARKA_MCF1_TEST_V4.0_YYYYMMDDHHMMSS.csv

        current_date = current_date.strftime('%Y%m%d%H%M%S').upper()
        file_name = "WA41937_ARKA_MCF1_PROD_V5.0_" + current_date + '.csv'
        csv = sdtm_df.to_csv(index=False, encoding='utf-8')

    if len(csv) != 0:
        if st.download_button(
                label='Download SDTM file',
                data=csv,
                file_name=file_name,
                mime='text/csv',
                key="sdtm-csv", ):
            st.write(f"Check your downloads folder for {file_name}")
        return
    else:
        st.write("File is empty.  Email:  helpdesk@arkanalabs.com")
        return
