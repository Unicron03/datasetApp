import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import datetime

# Initialiser session_state si nécessaire
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "new_row" not in st.session_state:
    st.session_state.new_row = {}
if "col_names" not in st.session_state:
    st.session_state.col_names = []
if "show_download_buttons" not in st.session_state:
    st.session_state.show_download_buttons = False
if "show_signature_button" not in st.session_state:
    st.session_state.show_signature_button = False

# Centrer le titre avec CSS
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .input-container {
        border: 2px solid #d3d3d3;
        padding: 20px;
        border-radius: 5px;
        background-color: #f9f9f9;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    <div class="title">Create</div>
""", unsafe_allow_html=True)
st.write("")
st.write("")

# Fonction pour déplacer la colonne "SIGNATURE" à la fin
def move_signature_to_end(df):
    if "SIGNATURE" in df.columns:
        cols = [col for col in df.columns if col != "SIGNATURE"]
        cols.append("SIGNATURE")
        return df[cols]
    return df

st.write('### Création du DataFrame :')

# Ajouter le cadre autour de la zone de création de colonnes
st.markdown("<div class='input-container'>", unsafe_allow_html=True)
new_col_name = st.text_input("Entrez le nom de la nouvelle colonne")
if new_col_name:  # Vérifier si le nom de la colonne n'est pas vide
    if st.button("Ajouter la colonne"):
        st.session_state.col_names.append(new_col_name)
        # Ajouter la nouvelle colonne au DataFrame existant
        if new_col_name not in st.session_state.df.columns:
            st.session_state.df[new_col_name] = pd.Series(dtype='object')
            st.session_state.df = move_signature_to_end(st.session_state.df)
st.markdown("</div>", unsafe_allow_html=True)

# Ajouter le cadre autour de la zone de saisie des données
if st.session_state.df.columns.tolist():
    st.markdown("<div class='input-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Saisie des données</div>", unsafe_allow_html=True)
    
    # Demander les valeurs pour chaque colonne sauf "SIGNATURE"
    for col_name in st.session_state.df.columns:
        if col_name != "SIGNATURE":
            st.session_state.new_row[col_name] = st.text_input(f"Entrez la valeur pour '{col_name}'")

    if st.button("Ajouter la ligne"):
        # Ajouter la nouvelle ligne au DataFrame
        new_data = pd.DataFrame(st.session_state.new_row, index=[0])
        st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
        st.session_state.df = move_signature_to_end(st.session_state.df)
    st.markdown("</div>", unsafe_allow_html=True)

# Afficher le DataFrame
st.write('### Visualisation du DataFrame :')
st.dataframe(st.session_state.df)

# Gestion des actions : Téléchargement, Ajout de signature, Réinitialisation
st.write('### Gestion du DataFrame :')
col1, col2, col3 = st.columns(3)

with col1:
    with st.expander("Télécharger", expanded=False):
        st.download_button("Télécharger en CSV", data=st.session_state.df.to_csv(index=False), file_name="data.csv", mime="text/csv")
        st.download_button("Télécharger en JSON", data=st.session_state.df.to_json(orient="records"), file_name="data.json", mime="application/json")
        table = pa.Table.from_pandas(st.session_state.df)
        pq.write_table(table, 'data.parquet')
        st.download_button("Télécharger en Parquet", data=open('data.parquet', 'rb').read(), file_name="data.parquet", mime="application/octet-stream")

with col2:
    with st.expander("Ajout signature", expanded=False):
        user_name = st.text_input("Entrez votre nom")
        if user_name:
            if st.button("Valider"):
                signature_value = f"Modifié par {user_name} le {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                if "SIGNATURE" not in st.session_state.df.columns:
                    st.session_state.df["SIGNATURE"] = ""
                st.session_state.df["SIGNATURE"] = signature_value
                st.session_state.df = move_signature_to_end(st.session_state.df)
                st.session_state.show_signature_button = False
                st.rerun()

with col3:
    if st.button("Réinitialiser"):
        st.session_state.df = pd.DataFrame()
        st.session_state.new_row = {}
        st.session_state.col_names = []
        st.rerun()

# Fonction pour déplacer la colonne "SIGNATURE" à la fin
def move_signature_to_end(df):
    if "SIGNATURE" in df.columns:
        cols = [col for col in df.columns if col != "SIGNATURE"]
        cols.append("SIGNATURE")
        return df[cols]
    return df
