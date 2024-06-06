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
if "col_types" not in st.session_state:
    st.session_state.col_types = {}  # Stocker le type de chaque colonne

# Centrer le titre avec CSS
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
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

with st.expander("Insérer une colonne", expanded=True):
    # Demander le nom de la nouvelle colonne
    new_col_name = st.text_input("Entrez le nom de la nouvelle colonne")

    # Sélectionner le type de la colonne
    col_type = st.selectbox(
        "Sélectionnez le type de la colonne",
        options=["string", "int", "float", "bool"],
        key="col_type_input"
    )

    if new_col_name and col_type:  # Vérifier si le nom de la colonne et le type ne sont pas vides
        if st.button("Ajouter la colonne"):
            st.session_state.col_names.append(new_col_name)
            st.session_state.col_types[new_col_name] = col_type  # Stocker le type de la colonne
            # Ajouter la nouvelle colonne au DataFrame existant avec le type approprié
            if new_col_name not in st.session_state.df.columns:
                if col_type == "string":
                    st.session_state.df[new_col_name] = pd.Series(dtype='object')
                elif col_type == "int":
                    st.session_state.df[new_col_name] = pd.Series(dtype='int64')
                elif col_type == "float":
                    st.session_state.df[new_col_name] = pd.Series(dtype='float64')
                elif col_type == "bool":
                    st.session_state.df[new_col_name] = pd.Series(dtype='bool')
                st.session_state.df = move_signature_to_end(st.session_state.df)
            # Réinitialiser le champ de texte après ajout
            st.experimental_rerun()

# Si des colonnes ont été ajoutées
if st.session_state.df.columns.tolist():
    with st.expander("Insérer une ligne", expanded=True):
        # Demander les valeurs pour chaque colonne sauf "SIGNATURE"
        for col_name in st.session_state.df.columns:
            if col_name != "SIGNATURE":
                col_type = st.session_state.col_types[col_name]
                if col_type == "string":
                    st.session_state.new_row[col_name] = st.text_input(f"Entrez la valeur pour '{col_name}' (string)", key=f"input_{col_name}")
                elif col_type == "int":
                    st.session_state.new_row[col_name] = st.number_input(f"Entrez une valeur entière pour '{col_name}' (int)", step=1, key=f"input_{col_name}")
                elif col_type == "float":
                    st.session_state.new_row[col_name] = st.number_input(f"Entrez une valeur décimale pour '{col_name}' (float)", key=f"input_{col_name}")
                elif col_type == "bool":
                    st.session_state.new_row[col_name] = st.selectbox(f"Sélectionnez True ou False pour '{col_name}' (bool)", options=[True, False], key=f"input_{col_name}")

        # Si l'utilisateur clique sur le bouton "Ajouter la ligne"
        if st.button("Ajouter la ligne"):
            # Ajouter la nouvelle ligne au DataFrame
            new_data = pd.DataFrame(st.session_state.new_row, index=[0])
            st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
            st.session_state.df = move_signature_to_end(st.session_state.df)
            st.session_state.new_row = {}  # Réinitialiser les valeurs des nouvelles données après l'ajout

# Afficher le DataFrame
st.write('### Visualisation du DataFrame :')
st.dataframe(st.session_state.df)

st.write('### Gestion du DataFrame :')
col1, col2, col3 = st.columns(3)
with col1:
    # Si l'utilisateur clique sur le bouton "Télécharger", basculer l'état des boutons de téléchargement
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
                    st.session_state.df["SIGNATURE"] = pd.Series(dtype='object')  # Créez la colonne avec des valeurs nulles
                    st.session_state.df.at[0, "SIGNATURE"] = signature_value  # Ajoutez la signature uniquement à la première ligne
                st.rerun()
with col3:
    if st.button("Réinitialiser"):
        st.session_state.df = pd.DataFrame()
        st.session_state.new_row = {}
        st.session_state.col_names = []
        st.session_state.col_types = {}
        st.rerun()
