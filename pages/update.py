import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

# Fonction pour lire les différents types de fichiers
def load_file(file):
    if file.name.endswith('.json'):
        data = json.load(file)
        return pd.DataFrame(data)
    elif file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.parquet'):
        return pd.read_parquet(file)
    else:
        st.error("Format de fichier non pris en charge!")
        return None

# Téléchargement du fichier JSON, CSV ou Parquet
uploaded_file = st.file_uploader("Choisissez un fichier JSON, CSV ou Parquet", type=["json", "csv", "parquet"])

if uploaded_file is not None:
    df = load_file(uploaded_file)
    if df is not None:
        st.write('DataFrame original :')
        st.write(df)

        # Initialisation de la liste des modifications
        if 'modifications' not in st.session_state:
            st.session_state.modifications = []

        # Saisie de la modification
        with st.form(key='modification_form'):
            row_index = st.number_input('Entrez l\'index de la ligne à modifier', min_value=0, max_value=len(df)-1, step=1)
            column_name = st.selectbox('Choisissez le nom de la colonne à modifier', df.columns)
            new_value = st.text_input('Entrez la nouvelle valeur')
            add_modification = st.form_submit_button('Ajouter la modification')
        
        # Ajouter la modification à la liste
        if add_modification:
            st.session_state.modifications.append((row_index, column_name, new_value))

        # Afficher la liste des modifications en attente avec des boutons pour les supprimer
        st.write('Modifications en attente :')
        for i, mod in enumerate(st.session_state.modifications):
            row_index, column_name, new_value = mod
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Ligne {row_index}, Colonne '{column_name}', Nouvelle valeur : {new_value}")
            with col2:
                if st.button('Supprimer', key=f'delete_{i}'):
                    st.session_state.modifications.pop(i)
                    st.experimental_rerun()

        # Boutons pour les actions de fin
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button('Appliquer toutes les modifications'):
                for mod in st.session_state.modifications:
                    row_index, column_name, new_value = mod
                    df.loc[row_index, column_name] = new_value
                st.write('DataFrame modifié :')
                st.write(df)

                # Réinitialiser la liste des modifications
                st.session_state.modifications = []

        with col2:
            user_name = st.text_input("Votre nom")
            if st.button("Ajouter Signature"):
                if user_name:
                    signature = f"Modifié par {user_name} le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    df.at[0, 'Signature'] = signature
                    st.write('DataFrame avec signature :')
                    st.write(df)
                else:
                    st.error("Veuillez entrer votre nom pour ajouter une signature.")

        with col3:
            if st.button("Réinitialiser"):
                if 'modifications' in st.session_state:
                    st.session_state.modifications = []
                st.experimental_rerun()

        # Expander pour les options de téléchargement
        with st.expander("Télécharger les modifications", expanded=True):
            st.markdown(
                """
                <style>
                .small-button button {
                    font-size: 0.8em !important;
                    padding: 0.25em 0.5em !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.markdown('<div class="small-button">', unsafe_allow_html=True)

            modified_json = df.to_json(orient='records', indent=2)
            modified_csv = df.to_csv(index=False).encode('utf-8')

            buffer = io.BytesIO()
            df.to_parquet(buffer, index=False)
            modified_parquet = buffer.getvalue()

            st.download_button(
                label="Télécharger en JSON",
                data=modified_json,
                file_name="modified_data.json",
                mime="application/json"
            )
            st.download_button(
                label="Télécharger en CSV",
                data=modified_csv,
                file_name="modified_data.csv",
                mime="text/csv"
            )
            st.download_button(
                label="Télécharger en Parquet",
                data=modified_parquet,
                file_name="modified_data.parquet",
                mime="application/octet-stream"
            )

            st.markdown('</div>', unsafe_allow_html=True)