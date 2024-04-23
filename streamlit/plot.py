from src.db.db import fetch_all_data
import pandas as pd
import streamlit as st
from datetime import datetime
import os

st.set_page_config(layout="wide")


def get_csv(dl=False):
    # Define file path
    file_path = "streamlit/data/gold_price_brisage.csv"
    # Check if file exists
    if os.path.exists(file_path) and not dl:
        return pd.read_csv(file_path)
    else:
        # Fetch all data if file does not exist and save to CSV
        df = fetch_all_data("gold_price_brisage")
        df.to_csv(file_path, index=False)
        return df


if 'first_load' not in st.session_state:
    st.session_state['first_load'] = True
    df = get_csv(dl=True)
else:
    df = get_csv(dl=False)

df1 = df.copy()
df = df[['item_id', 'objet_type', 'objet_level', 'nom_objet', 'meilleur_renta',
         'meilleur_renta_percent', 'meilleur_renta_valeur', 'coefficient', 'rune_last_update', 'hdv_last_update']]
df1 = df1[['item_id', 'nom_objet', 'prix', 'craft',
           'focus_rentabilite', 'total_profit_non_focus']]

df['meilleur_renta_valeur'] = df['meilleur_renta_valeur'].fillna(0)
df['meilleur_renta_valeur'] = df['meilleur_renta_valeur'].astype(int)


df['rune_last_update'] = pd.to_datetime(df['rune_last_update'])
df['hdv_last_update'] = pd.to_datetime(df['hdv_last_update'])

df['coeff_derniere_update'] = (
    (datetime.now() - df['rune_last_update']).dt.total_seconds() / 3600).fillna(0).astype(int)
df.drop(columns=['rune_last_update'], inplace=True)

df['hdv_derniere_update'] = (
    (datetime.now() - df['hdv_last_update']).dt.total_seconds() / 3600).fillna(0).astype(int)
df.drop(columns=['hdv_last_update'], inplace=True)
# df['hdv_derniere_update'] = df['HDV derniere update'].fillna(0).astype(int)
# Display title in Streamlit app
st.markdown("<h1 style='text-align: center; color: #FFD700; font-size: 80px;'>Richus</h1>",
            unsafe_allow_html=True)
st.markdown("&nbsp;")
st.markdown("&nbsp;")
st.markdown("&nbsp;")
st.markdown("<h2 style='text-align: center; color: white;'>Résumé (Hell Mina)</h2>",
            unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    item_id_filter = st.selectbox("ID de l'objet", options=[
                                  'Tout'] + sorted(list(df['item_id'].unique())), key='item_id_select')
if item_id_filter != 'Tout':
    df = df[df['item_id'] == item_id_filter]
    df1 = df1[df1['item_id'] == item_id_filter]

with col2:
    name_filter = st.text_input("Nom de l'objet", key='nom_objet_filter')
if name_filter:
    df = df[df['nom_objet'].str.contains(name_filter, case=False)]
    df1 = df1[df1['nom_objet'].str.contains(name_filter, case=False)]

with col3:
    update_filter_options = {'Tout': None, 'Moins d\'un jour': 24,
                             'Moins d\'une semaine': 168, 'Moins d\'un mois': 720}
    update_filter_choice = st.selectbox("Derniere update de la rune", options=list(
        update_filter_options.keys()), key='update_filter')

if update_filter_options[update_filter_choice]:
    df = df[df['coeff_derniere_update'] <=
            update_filter_options[update_filter_choice]]

with col4:
    rentable_filter = st.selectbox(
        "Seulement rentable", ['Non', 'Oui'], key='rentable_filter')
if rentable_filter == 'Oui':
    df = df[df['meilleur_renta'] != 'non_rentable']


def highlight_renta_percent_high(s):
    return ['background-color: lightgreen; color:black' if float(val.strip('%')) > 200 else '' for val in s]

# Styling dataframe based on 'Derniere update' value and formatting float columns


def highlight_update(s):
    return ['background-color: lightgreen; color:black' if val <= 168 else '' for val in s]


def highlight_renta_valeur(s):
    return ['background-color: #ffcccc; color:black' if val <= 0 else '' for val in s]


df_styled = df.style.apply(highlight_update, subset=['coeff_derniere_update'])
df_styled = df_styled.apply(highlight_renta_valeur, subset=[
                            'meilleur_renta_valeur'])
df_styled = df_styled.apply(highlight_renta_percent_high, subset=[
                            'meilleur_renta_percent'])

df_styled = df_styled.format(
    {'coeff_derniere_update': lambda x: f"Il y a {x} heures"})
#
# df_styled = df_styled.format(
#     {'hdv_derniere_update': lambda x: f"Il y a {x} heures"})

df['meilleur_renta_percent'] = df['meilleur_renta_percent'].astype(str) + '%'
df['coefficient'] = df['coefficient'].astype(str) + '%'

st.dataframe(df_styled, width=1000, height=600,
             hide_index=True, use_container_width=True)

st.markdown("<h2 style='text-align: center; color: white;'>Prix</h2>",
            unsafe_allow_html=True)


# df1['total_profit_non_focus'].fillna(0).astype(int)
df1['total_profit_non_focus'] = df1['total_profit_non_focus'].fillna(
    0).astype(int)
df1['focus_rentabilite'] = df1['focus_rentabilite'].fillna(
    0).astype(int)


st.dataframe(df1, width=1000, height=600,
             hide_index=True, use_container_width=True)
