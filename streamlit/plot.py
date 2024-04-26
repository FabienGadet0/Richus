from src.db.db import fetch_all_data
import pandas as pd
import streamlit as st
from datetime import datetime
import os
import dotenv

dotenv.load_dotenv()

st.set_page_config(layout="wide")


def get_data(file_name, dl=True):
    # Define file path
    # Check if file exists
    if os.path.exists(f"streamlit/data/{file_name}.csv") and not dl:
        return pd.read_csv(f"streamlit/data/{file_name}.csv")
    else:
        # Fetch all data if file does not exist and save to CSV
        df = fetch_all_data(file_name)
        df.to_csv(f"streamlit/data/{file_name}.csv", index=False)
        return df


# first_load = True
# first_load = 'first_load' not in st.session_state
# if 'first_load' not in st.session_state:
#     st.session_state['first_load'] = True
#     first_load = False

df = get_data("gold_price_brisage", dl=False)
df_history = get_data("bronze_brisage_coeff_history", dl=False)
df_runes = get_data("gold_item_rune_price", dl=False)


df1 = df.copy()
df = df[
    [
        "item_id",
        "objet_type",
        "objet_level",
        "nom_objet",
        "meilleur_renta",
        "meilleur_renta_percent",
        "meilleur_renta_valeur",
        "coefficient",
        "rune_last_update",
        "hdv_last_update",
    ]
]
df1 = df1[
    [
        "item_id",
        "nom_objet",
        "prix",
        "craft",
        "focus_rentabilite",
        "total_profit_non_focus",
        "craft_vs_focus_diff",
        "craft_vs_prix_diff",
        "craft_vs_total_profit_non_focus_diff",
    ]
]

df["meilleur_renta_valeur"] = df["meilleur_renta_valeur"].fillna(0)
df["meilleur_renta_valeur"] = df["meilleur_renta_valeur"].astype(int)


df["rune_last_update"] = pd.to_datetime(df["rune_last_update"])
df["hdv_last_update"] = pd.to_datetime(df["hdv_last_update"])

df["coeff_derniere_update"] = (
    ((datetime.now() - df["rune_last_update"]).dt.total_seconds() / 3600)
    .fillna(0)
    .astype(int)
)
df.drop(columns=["rune_last_update"], inplace=True)

df["hdv_derniere_update"] = (
    ((datetime.now() - df["hdv_last_update"]).dt.total_seconds() / 3600)
    .fillna(0)
    .astype(int)
)
df.drop(columns=["hdv_last_update"], inplace=True)

st.markdown(
    "<h1 style='text-align: center; color: #FFD700; font-size: 80px;'>Richus</h1>",
    unsafe_allow_html=True,
)
st.markdown("&nbsp;")
st.markdown("&nbsp;")
st.markdown("&nbsp;")

st.markdown(
    "<h2 style='text-align: center; color: white;'>Résumé (Hell Mina)</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("## Filtres")
item_id_filter = st.sidebar.multiselect(
    "ID de l'objet",
    options=sorted(list(df["item_id"].unique())),
    default=[],
    key="item_id_select",
)
if item_id_filter:
    df = df[df["item_id"].isin(item_id_filter)]
    df1 = df1[df1["item_id"].isin(item_id_filter)]

name_filter = st.sidebar.text_input(
    "Nom de l'objet",
    key="nom_objet_filter",
)

if name_filter:
    df = df[df["nom_objet"].str.contains(name_filter)]
    df1 = df1[df1["nom_objet"].str.contains(name_filter)]

type_filter = st.sidebar.multiselect(
    "Type de l'objet",
    options=sorted(list(df["objet_type"].unique())),
    default=[],
    key="type_objet_filter",
)
if type_filter:
    df = df[df["objet_type"].isin(type_filter)]

meilleur_renta_filter = st.sidebar.multiselect(
    "Meilleur methode",
    options=sorted(list(df["meilleur_renta"].unique())),
    default=[],
    key="meilleur_renta_filter",
)
if meilleur_renta_filter:
    df = df[df["meilleur_renta"].isin(meilleur_renta_filter)]

update_filter_options = {
    "Tout": None,
    "Moins d'un jour": 24,
    "Moins d'une semaine": 168,
    "Moins d'un mois": 720,
}
update_filter_choice = st.sidebar.selectbox(
    "Derniere MAJ des coeffs de rune",
    options=list(update_filter_options.keys()),
    key="update_filter",
)

if update_filter_options[update_filter_choice]:
    df = df[df["coeff_derniere_update"] <= update_filter_options[update_filter_choice]]

rentable_filter = st.sidebar.checkbox("Seulement rentable", key="rentable_filter")
if rentable_filter:
    df = df[df["meilleur_renta"] != "non_rentable"]

coefficient_filter = st.sidebar.checkbox(
    "Coefficient sous 1000", key="coefficient_filter"
)
if coefficient_filter:
    df = df[df["coefficient"].astype(float) < 1000]


def highlight_renta_percent_high(s):
    return [
        "background-color: gold; color:black" if float(val) > 200 else "" for val in s
    ]


def highlight_renta_valeur(s):
    return ["background-color: #ffcccc; color:black" if val <= 0 else "" for val in s]


def highlight_update(s):
    return [
        "background-color: lightgreen; color:black" if val <= 96 else "" for val in s
    ]


def highlight_coefficient_above_average(s, avg):
    return ["background-color: gold; color:black" if val > avg else "" for val in s]


avg_coefficient = df["coefficient"].astype(float).mean()


# if not item_id_filter and not name_filter and not type_filter and update_filter_choice == 'Tout' and not rentable_filter and not coefficient_filter:

if item_id_filter or name_filter:
    if item_id_filter:
        df_runes = df_runes[df_runes["item_id"].isin(item_id_filter)]
        df1 = df1[df1["item_id"].isin(item_id_filter)]
        df = df[df["item_id"].isin(item_id_filter)]
    if name_filter:
        df = df[df["nom_objet"].str.contains(name_filter.lower(), case=False)]
        df1 = df1[df1["nom_objet"].str.contains(name_filter.lower(), case=False)]
        df_runes = df_runes[df_runes["item_id"].isin(df["item_id"].unique())]
else:
    df = df.head(400)
    # If no filter is applied, show an empty dataframe
    # df_runes = df_runes[df_runes["item_id"].isin(df["item_id"].unique())]
    df1 = df1[df1["item_id"].isin(df["item_id"].unique())]
    df_runes = df_runes.head(0)

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
    "focus_rentabilite": "Prix de vente Focus",
    "total_profit_non_focus": "Prix de vente non Focus",
    "craft_vs_focus_diff": "Rentabilité Craft -> Focus",
    "craft_vs_total_profit_non_focus_diff": "Rentabilité Craft -> Brisage Non Focus",
    "craft_vs_prix_diff": "Rentabilité Craft -> Revente",
}

df.rename(columns=column_translations, inplace=True)
df_styled = (
    df.style.apply(lambda x: ["background-color: black"] * len(x), axis=1)
    .map(lambda x: "text-align: center;")
    .apply(highlight_update, subset=["MàJ Coeff"])
    .apply(highlight_renta_valeur, subset=["Valeur Rentabilité"])
    .apply(highlight_renta_percent_high, subset=["% Rentabilité"])
    .apply(
        lambda x: highlight_coefficient_above_average(x, avg_coefficient),
        subset=["Coeff"],
    )
    .format(
        {
            "% Rentabilité": lambda x: "{:.0f} %".format(x) if x != "" else "",
            "Coeff": lambda x: "{:.0f} %".format(x) if x != "" else "",
            "Valeur Rentabilité": lambda x: "{} K".format(x) if x != "" else "",
            "MàJ Coeff": "Il y a {} heures".format,
            "MàJ HDV": "Il y a {} heures".format,
        }
    )
    .set_properties(
        **{
            "text-align": "center",
            "border-color": "lightgray",
            "border-width": "1px",
            "border-style": "solid",
        }
    )
    .set_table_styles(
        [{"selector": "th", "props": [("color", "white"), ("text-align", "center")]}]
    )
)

df1.rename(columns=column_translations, inplace=True)
df1_styled = (
    df1.style.apply(lambda x: ["background-color: black"] * len(x), axis=1)
    .map(lambda x: "text-align: center;")
    .format(
        {
            "Prix": lambda x: "{} K".format(x) if x != "" else "",
            "Prix de Craft": lambda x: "{} K".format(x) if x != "" else "",
            "Prix de vente Focus": lambda x: (
                "{} K".format(round(x, 1)) if x != "" else ""
            ),
            "Prix de vente non Focus": lambda x: "{} K".format(x) if x != "" else "",
            "Rentabilité Craft -> Focus": lambda x: "{} K".format(x) if x != "" else "",
            "Rentabilité Craft -> Revente": lambda x: (
                "{} K".format(x) if x != "" else ""
            ),
            "Rentabilité Craft -> Brisage Non Focus": lambda x: (
                "{} K".format(x) if x != "" else ""
            ),
        }
    )
    .set_properties(
        **{
            "text-align": "center",
            "border-color": "lightgray",
            "border-width": "1px",
            "border-style": "solid",
        }
    )
    .set_table_styles(
        [{"selector": "th", "props": [("color", "white"), ("text-align", "center")]}]
    )
)


st.dataframe(df_styled, width=1000, height=600, use_container_width=True)

st.markdown(
    "<h2 style='text-align: center; color: white;'>Prix details </h2>",
    unsafe_allow_html=True,
)

st.dataframe(
    df1_styled, width=1000, height=600, hide_index=True, use_container_width=True
)

st.markdown(
    "<h2 style='text-align: center; color: white;'>Runes details</h2>",
    unsafe_allow_html=True,
)
df_runes = df_runes[
    [
        "item_id",
        "name",
        "rune_weight",
        "jet",
        "runes_qty",
        "focus_runes_qty",
        "profitability",
        "focus_profitability",
    ]
]


column_translations_runes = {
    "item_id": "ID",
    "name": "Nom",
    "rune_weight": "Poids Rune",
    "jet": "Jet",
    "runes_qty": "Qté Runes",
    "focus_runes_qty": "Qté Runes Focus",
    "profitability": "Rentabilité",
    "focus_profitability": "Prix de vente Focus",
}

df_runes.rename(columns=column_translations_runes, inplace=True)


df_runes_styled = (
    df_runes.style.apply(lambda x: ["background-color: black"] * len(x), axis=1)
    .map(lambda x: "text-align: center;")
    .format(
        {
            "Qté Runes": "{:,.1f}",
            "Qté Runes Focus": "{:,.1f}",
            "Rentabilité": lambda x: "{} K".format(round(x, 1)) if x != "" else "",
            "Prix de vente Focus": lambda x: (
                "{} K".format(round(x, 1)) if x != "" else ""
            ),
            "Poids Rune": "{:,.1f}",
        }
    )
    .set_properties(
        **{
            "text-align": "center",
            "border-color": "lightgray",
            "border-width": "1px",
            "border-style": "solid",
        }
    )
    .set_table_styles(
        [{"selector": "th", "props": [("color", "white"), ("text-align", "center")]}]
    )
)


st.dataframe(
    df_runes_styled, width=1000, height=600, hide_index=True, use_container_width=True
)
