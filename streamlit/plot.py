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

st.markdown("<h1 style='text-align: center; color: #FFD700; font-size: 80px;'>Richus</h1>",
            unsafe_allow_html=True)
st.markdown("&nbsp;")
st.markdown("&nbsp;")
st.markdown("&nbsp;")
st.markdown("<h2 style='text-align: center; color: white;'>Résumé (Hell Mina)</h2>",
            unsafe_allow_html=True)

st.sidebar.markdown("## Filtres")
item_id_filter = st.sidebar.multiselect("ID de l'objet", options=sorted(list(df['item_id'].unique())), default=[], key='item_id_select')
if item_id_filter:
    df = df[df['item_id'].isin(item_id_filter)]
    df1 = df1[df1['item_id'].isin(item_id_filter)]

name_filter = st.sidebar.multiselect("Nom de l'objet", options=sorted(list(df['nom_objet'].unique())), default=[], key='nom_objet_filter')
if name_filter:
    df = df[df['nom_objet'].isin(name_filter)]
    df1 = df1[df1['nom_objet'].isin(name_filter)]

type_filter = st.sidebar.multiselect("Type de l'objet", options=sorted(list(df['objet_type'].unique())), default=[], key='type_objet_filter')
if type_filter:
    df = df[df['objet_type'].isin(type_filter)]

update_filter_options = {'Tout': None,'Moins d\'un jour': 24, 'Moins d\'une semaine': 168, 'Moins d\'un mois': 720}
update_filter_choice = st.sidebar.selectbox("Derniere update de la rune", options=list(update_filter_options.keys()), key='update_filter')

if update_filter_options[update_filter_choice]:
    df = df[df['coeff_derniere_update'] <=
            update_filter_options[update_filter_choice]]

rentable_filter = st.sidebar.checkbox("Seulement rentable", key='rentable_filter')
if rentable_filter:
    df = df[df['meilleur_renta'] != 'non_rentable']

coefficient_filter = st.sidebar.checkbox("Coefficient sous 1000", key='coefficient_filter')
if coefficient_filter:
    df = df[df['coefficient'].astype(float) < 1000]

def highlight_renta_percent_high(s):
    return ['background-color: gold; color:black' if float(val) > 200 else '' for val in s]


def highlight_renta_valeur(s):
    return ['background-color: #ffcccc; color:black' if val <= 0 else '' for val in s]
def highlight_update(s):
    return ['background-color: lightgreen; color:black' if val <= 96 else '' for val in s]

def highlight_coefficient_above_average(s, avg):
    return ['background-color: gold; color:black' if val > avg else '' for val in s]

avg_coefficient = df['coefficient'].astype(float).mean()


column_translations = {
    "item_id": "ID",
    "objet_type": "Type",
    "objet_level": "Niveau",
    "nom_objet": "Nom",
    "meilleur_renta": "Meilleur methode",
    "meilleur_renta_percent": "% Rentabilité",
    "meilleur_renta_valeur": "Valeur Rentabilité",
    "coefficient": "Coeff",
    "coeff_derniere_update": "MàJ Coeff",
    "hdv_derniere_update": "MàJ HDV",
    "prix": "Prix",
    "craft": "Prix de Craft",
    "focus_rentabilite": "Rentabilité Focus",
    "total_profit_non_focus": "Profit Total"
}

df.rename(columns=column_translations, inplace=True)
df_styled = df.style.apply(
    lambda x: ['background-color: black']*len(x), axis=1
).applymap(
    lambda x: 'text-align: center;'
).apply(
    highlight_update, subset=["MàJ Coeff"]
).apply(
    highlight_renta_valeur, subset=["Valeur Rentabilité"]
).apply(
    highlight_renta_percent_high, subset=["% Rentabilité"]
).apply(
    lambda x: highlight_coefficient_above_average(x, avg_coefficient), subset=["Coeff"]
).format(
    {"% Rentabilité": lambda x: "{:.0f} %".format(x) if x != '' else '', "Coeff": lambda x: "{:.0f} %".format(x) if x != '' else '', "Valeur Rentabilité": lambda x: "{} K".format(x) if x != '' else '', "MàJ Coeff": "Il y a {} heures".format, "MàJ HDV": "Il y a {} heures".format}
).set_properties(
    **{'text-align': 'center', 'border-color': 'lightgray', 'border-width': '1px', 'border-style': 'solid'}
).set_table_styles(
    [{'selector': 'th', 'props': [('background-color', '#4B5D67'), ('color', 'white'), ('text-align', 'center')]}]
)

st.dataframe(df_styled, width=1000, height=600,
             hide_index=True, use_container_width=True)

st.markdown("<h2 style='text-align: center; color: white;'>Prix</h2>",
            unsafe_allow_html=True)

df1['total_profit_non_focus'] = df1['total_profit_non_focus'].fillna(
    0).astype(int)
df1['focus_rentabilite'] = df1['focus_rentabilite'].fillna(
    0).astype(int)

df1.rename(columns=column_translations, inplace=True)

df1_styled = df1.style.apply(
    lambda x: ['background-color: black']*len(x), axis=1
).applymap(
    lambda x: 'text-align: center;'
).format(
    {"Prix": lambda x: "{} K".format(x) if x != '' else '', "Prix de Craft": lambda x: "{} K".format(x) if x != '' else '', "Rentabilité Focus": lambda x: "{} K".format(x) if x != '' else '', "Profit Total": lambda x: "{} K".format(x) if x != '' else ''}
).set_properties(
    **{'text-align': 'center', 'border-color': 'lightgray', 'border-width': '1px', 'border-style': 'solid'}
).set_table_styles(
    [{'selector': 'th', 'props': [('background-color', '#4B5D67'), ('color', 'white'), ('text-align', 'center')]}]
)

st.dataframe(df1_styled, width=1000, height=600, hide_index=True, use_container_width=True)
