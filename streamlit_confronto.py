# streamlit confronto

# "Confronto" perché sono presenti due matrici Q, calcolate in due elaborazioni diverse, confrontate per evidenziarne le differenze  

import numpy as np
import pandas as pd
import streamlit as st
#from st_aggrid import AgGrid

st.set_page_config(page_title="RL_npl_utp", layout = "wide")

st.title("Reinforcement Learning on NPL and UTP")


action_dict = {
    
    # from operations
    "SDP": "agent_warning", 
    "REV": "outsourcing_withdrawal", #revoca da parte di AMCO della pratica al servicer in questione
    # from deliberations
    "01": "credits_classification", #passing from utp to npl, usually
    "Pia": "re_entry_plan",
    "Rin": "credit_renunciation",
    "Sal": "full_and_final_settlement", #saldo e stralcio
    "Str": "write_off_with_deferred_payments", #stralcio con dilazione
    "05": "new_recovery_strategy", #proposta di cambio di strategia finora adottata: può essere utile un NLP su "commento proponente" in df_deliberations_date_sorted
    "06": "forbearance_or_covid",
    "08": "bank_credit_withdrawal", #revoca di un fido, spesso antacedente alla chiusura della pratica
    "12": "credit_collection", #richiesta di escussione pegni o garanzie (presenti anche altre proposte, difficlmente classificabili)
    "Ces": "credit_cession", #è una delibera esplicativa della situazione in essere di un credito cedibile
    "Ric": "info_request", #è un servicer che richiede informazioni riguardo a una pratica da essi gestita
    "Avv": "begin_lawsuit", #inizio di una causa legale
    "Azi": "lawsuit_procedure", #una procedura legale non meglio specificata, ma spesso riferita a esecuzione immobiliare, o comunque in una fase avanzata del PCT
    "Con": "lawsuit_procedure", #delibera inserita in automatica ma che corrisponde comunque ad una azione di tipo legale, in stato già avanzato
    "Esc": "confidi_liquidation", #escussione crediti Confidi
    "20": "extrajudicial_appraiser", 
    "23": "claim",
}

action_description_dict = { 
    # dictionary from an action name to an action description
    
    # operations
    "agent_warning" : "send a letter to invite the customer to pay, if he/she is late in doing so",
    "outsourcing_withdrawal" : "revoke the file from a servicer", #revoca da parte di AMCO della pratica al servicer in questione

    #deliberations
    "credits_classification" : "pass the loan to non-performing from another state",
    "re_entry_plan" : "propose a re-entry plan to the customer",
    "credit_renunciation" : "the credit is no more likely to be recovered, so it's better to stop taking actions on it",
    "full_and_final_settlement" : "propose a final convenient solution to the customer in order to recover at least a little part of the debt", #saldo e stralcio
    "write_off_with_deferred_payments" :"propose a final convenient solution to the customer, with deferred payments", #stralcio con dilazione
    "new_recovery_strategy" :"propose a generic new strategy of recovery", #proposta di cambio di strategia finora adottata: può essere utile un NLP su "commento proponente" in df_deliberations_date_sorted
    "forbearance_or_covid" : "concede forbearance measure on the file, mostly for covid moratorium",
    "bank_credit_withdrawal" : "revoke the bank credit to the customer", #revoca di un fido, spesso antacedente alla chiusura della pratica
     "credit_collection" : "enforce pledges or warranties", #richiesta di escussione pegni o garanzie (presenti anche altre proposte, difficlmente classificabili)
    "credit_cession" : "propose to make a cession to a servicer", #è una delibera esplicativa della situazione in essere di un credito cedibile
    "info_request" : "ask for information to AMCO or directly to banks or other entities", #è un servicer che richiede informazioni riguardo a una pratica da essi gestita
    "begin_lawsuit" : "begin a legal procedure", #inizio di una causa legale
    "lawsuit_procedure" : "take a key legal procedure (usually real estate execution)", #una procedura legale non meglio specificata, ma spesso riferita a esecuzione immobiliare, o comunque in una fase avanzata del PCT
     "confidi_liquidation" : "enforce warranties from a consortium (usually Confidi)", #escussione crediti Confidi
    "extrajudicial_appraiser" : "make an appraisal by an expert", 
    "claim" : "ask bank for a refund, usually for files that shouldn't be ceded by bank"
}

gbv_bins = ['0-25k', '25-100k', 
        '100-200k', '200-500k', '500-1000k','>1000k']

#type of non-performing exposure: npl or utp
npe_type =["npl", "utp", "bonis"]
technical_form = ["bank_account", "first_home_loan", "unsecured_loan","mortgage", "other_form", "minor_form"]

#index for the estimated recoverability of a file, by AMCO itself, so a subjective attribute for the file 
max_recovery_value_bins = ['0-25k', '25-100k',
        '100-200k', '200-500k', '500-1000k','>1000k']
#piva_or_not = ["piva", "not_piva"]
macroregions = ["north", "middle", "south_or_islands", "no_macro_region"]
time_from_start_bins = ["0_6_months", "6_12_months", "12_24_months", "24+_months"]

#ARRANGIARE VERSO LO 0% I BIN
revenues_over_gbv_bins = ["no_revenue_over_gbv", "0.01_5%_gbv_recovered", "5%_10%_gbv_recovered", "10_20%_gbv_recovered", "20%+_gbv_recovered"]

#10 = cribis, 6 = fire, 9 = advanced_trade, 7 = sistemia, 00 = AMCO,altro
servicers = ["amco","fire", "cribis", "advanced_trade", "sistemia", "other_servicer"]

action_list_values = list(set(action_dict.values()))
multi_index_tuples = [(gbv_bins[g], npe_type[n], technical_form[tec], max_recovery_value_bins[r],macroregions[m],time_from_start_bins[t], revenues_over_gbv_bins[rev], servicers[s]) for g in np.arange(0, np.size(gbv_bins)) for n in np.arange(0,np.size(npe_type)) for tec in np.arange(0, np.size(technical_form)) for r in np.arange(0, np.size(max_recovery_value_bins)) for m in np.arange(0, np.size(macroregions)) for t in np.arange(0,np.size(time_from_start_bins)) for rev in np.arange(0,np.size(revenues_over_gbv_bins)) for s in np.arange(0, np.size(servicers))]
multi_index_state = pd.MultiIndex.from_tuples(multi_index_tuples)


#if st.checkbox("choose file characteristics"):
#st.write("ok")
option_gbv =st.selectbox('select **GBV bin**', gbv_bins)
option_npe_type = st.selectbox('**non performing loan** or **unlikely to pay**?', npe_type)
option_technical_form = st.selectbox('which **technical form** are you interested in?', technical_form)
option_max_recovery = st.selectbox('how much can you **recover at maximum** from this file?', max_recovery_value_bins)
option_macro_region = st.selectbox('which **macro region** are you interested in?', macroregions)
option_servicer = st.selectbox('which is the **servicer**?', servicers)
option_time_from_start = st.selectbox('how much **time** has passed **since** the **acquisition** of the file?', time_from_start_bins)
option_revenue_over_gbv = st.selectbox('how much has been **already recovered** (in % on the GBV)', revenues_over_gbv_bins)

# if st.button("fine"):
state = {
    "gbv_bin" : option_gbv,
    "npe_type" : option_npe_type,
    "technical_form": option_technical_form,
    "max_recovery_value_bin" : option_max_recovery,
    "macro_region" : option_macro_region,
    "time_from_start_bin" : option_time_from_start,
    "revenues_over_gbv_bin" : option_revenue_over_gbv,
    "servicer" : option_servicer
}

# function for set text color of positive
# values in Dataframes
def color_positive_green(val):
    color = "black"
    try:
        if val > 0:
            color = 'green'
        else:
            color = 'red'
    except:
        pass
    return 'color: %s' % color

state_index = multi_index_tuples.index(tuple(state.values()))

col1, padding, col2 = st.columns((20,2,20))
with col1:
    Q_matrix = pd.read_csv("df_Q_matrix_almost_all_files_06_03_test_beta_0.3_light_for_Github.csv", index_col = [0,1,2,3,4,5,6,7])

    df_Q = pd.DataFrame(Q_matrix.iloc[state_index], index = action_list_values)
    df_Q["description"] = "ciao"
    df_Q = df_Q[df_Q.iloc[:,0] != 0]
    df_Q = df_Q.set_axis(["q-values", "description"],axis = 1) # , inplace = True excluded because causing error
    for i in df_Q.index:
        df_Q.loc[i,"description"] = action_description_dict[i]
    df_Q = df_Q.sort_values("q-values", ascending = False)
    #df_Q.style.highlight_between(left = 0, right = 1000000)
    st.dataframe(df_Q.style.applymap(color_positive_green)\
                .format({"q-values":"{:.0f}€"}), height = 1000, width = 1000)

    # (df_Q.style.highlight_between("q-values", left = 0, right = 1000000, color = "green")\
    #             .highlight_between("q-values", left = -1000000, right = -1, color = "orange")
with col2:
    Q_matrix2 = pd.read_csv("df_Q_matrix_almost_all_files_05_03_test_beta_0.4_originale_colonne_invertite.csv", index_col = [0,1,2,3,4,5,6,7])

    df_Q2 = pd.DataFrame(Q_matrix2.iloc[state_index], index = action_list_values)
    df_Q2["description"] = "ciao"
    df_Q2 = df_Q2[df_Q2.iloc[:,0] != 0]
    df_Q2 = df_Q2.set_axis(["q-values", "description"],axis = 1) # , inplace = True
    for i in df_Q2.index:
        df_Q2.loc[i,"description"] = action_description_dict[i]
    df_Q2 = df_Q2.sort_values("q-values", ascending = False)
    #df_Q2.style.highlight_between(left = 0, right = 1000000)
    st.dataframe(df_Q2.style.applymap(color_positive_green)\
                .format({"q-values":"{:.0f}€"}), height = 1000, width = 1000)
