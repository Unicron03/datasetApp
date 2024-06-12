import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

#---------------------------------------------------Titre--------------------------------------------------------------
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
    }
    </style>
    <div class="title">Update</div>
""", unsafe_allow_html=True)
st.write("")
st.write("")

#--------------------------------------------------------Lire les fichiers-----------------------------------------------------------------------(valider)
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

#-------------------------------------------------Ajouter une nouvelle colonne-------------------------------------------------------------------(valider)
# Fonction pour ajouter une nouvelle colonne
def add_column(df, col_name, col_type):
    if col_type == 'string':
        df[col_name] = ""
    elif col_type == 'int':
        df[col_name] = 0
    elif col_type == 'float':
        df[col_name] = 0.0
    elif col_type == 'bool':
        df[col_name] = False
    return df

#-------------------------------------------------Signature à la fin----------------------------------------------------------------------------
def ensure_signature_at_end(df):
    if 'Signature' in df.columns:
        columns = [col for col in df.columns if col != 'Signature'] + ['Signature']
        df = df[columns]
    return df

#------------------------------------------------Téléchargement du fichier--------------------------------------------------------------------
uploaded_file = st.file_uploader("Choisissez un fichier JSON, CSV ou Parquet", type=["json", "csv", "parquet"])

if uploaded_file is not None:
    df = load_file(uploaded_file)
    if df is not None:
        st.write('### DataFrame original :')
        st.dataframe(df)

        # Initialisation de la liste des modifications
        if 'modifications' not in st.session_state:
            st.session_state.modifications = []

        # Charger le DataFrame modifié stocké dans session_state s'il existe
        if 'modified_df' in st.session_state:
            df = st.session_state.modified_df

        # Sections dépliantes pour ajouter et supprimer des lignes et des colonnes
        st.write('### Ajouter ou supprimer des lignes et des colonnes :')

        with st.expander("Ajouter une ligne", expanded=False):
            if st.button('Ajouter une ligne'):
                new_row_data = {col: None for col in df.columns if col != 'Signature'}
                new_row = pd.DataFrame([new_row_data])
                df = pd.concat([df, new_row], ignore_index=True)
                df = ensure_signature_at_end(df)
                st.session_state.modified_df = df.copy()
                st.experimental_rerun()

        with st.expander("Ajouter une colonne", expanded=False):
            new_col_name = st.text_input('Nom de la nouvelle colonne', key='new_col')
            col_type = st.selectbox('Type de la nouvelle colonne', ['string', 'int', 'float', 'bool'], key='new_col_type')
            if st.button("Ajouter une colonne") and new_col_name:
                df = add_column(df, new_col_name, col_type)
                df = ensure_signature_at_end(df)
                st.session_state.modified_df = df.copy()
                st.experimental_rerun()

        with st.expander("Supprimer une ligne", expanded=False):
            row_to_delete = st.number_input('Index de la ligne à supprimer', min_value=0, max_value=len(df)-1, step=1, key='row_to_delete')
            if st.button("Supprimer une ligne"):
                df = df.drop(index=row_to_delete).reset_index(drop=True)
                df = ensure_signature_at_end(df)
                st.session_state.modified_df = df.copy()
                st.experimental_rerun()

        with st.expander("Supprimer une colonne", expanded=False):
            col_to_delete = st.selectbox('Colonne à supprimer', [col for col in df.columns if col != 'Signature'], key='col_to_delete')
            if st.button("Supprimer une colonne"):
                df = df.drop(columns=[col_to_delete])
                df = ensure_signature_at_end(df)
                st.session_state.modified_df = df.copy()
                st.experimental_rerun()

        #-------------------------------------------------------------------Afficher le DataFrame----------------------------------------------------------
        st.write('### DataFrame après modifications :')
        st.dataframe(df)

        # Saisie de la modification
        st.write('### Modifications des valeurs:')
        
        # Widget pour sélectionner la colonne à modifier
        column_name = st.selectbox('Choisissez le nom de la colonne à modifier', df.columns, key='selected_column')

        # Déterminer le type de la colonne sélectionnée
        col_type = df[column_name].dtype

        # Afficher le widget approprié pour le type de colonne
        if col_type == 'int64':
            new_value = st.number_input('Entrez la nouvelle valeur', step=1, format='%d')
        elif col_type == 'float64':
            new_value = st.number_input('Entrez la nouvelle valeur', format='%f')
        elif col_type == 'bool':
            new_value = st.selectbox('Entrez la nouvelle valeur', [True, False])
        else:
            new_value = st.text_input('Entrez la nouvelle valeur')

        with st.form(key='modification_form'):
            row_index = st.number_input('Entrez l\'index de la ligne à modifier', min_value=0, max_value=len(df)-1, step=1, key='row_index')
            add_modification = st.form_submit_button('Ajouter la modification')

        #-----------------------------------------------------------------Ajouter la modification à la liste------------------------------------------------
        if add_modification:
            st.session_state.modifications.append((row_index, column_name, new_value))
            st.experimental_rerun()

        #---------------------------------------------------------------- Afficher la liste des modifications en attente------------------------------------
        st.write('### Modifications en attente :')
        for i, mod in enumerate(st.session_state.modifications):
            row_index, column_name, new_value = mod
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Ligne {row_index}, Colonne '{column_name}', Nouvelle valeur : {new_value}")
            with col2:
                if st.button('Supprimer', key=f'delete_{i}'):
                    st.session_state.modifications.pop(i)
                    st.experimental_rerun()

        #--------------------------------------------------- Appliquer les modifications et la signature--------------------------------------------------
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button('Appliquer toutes les modifications'):
                for mod in st.session_state.modifications:
                    row_index, column_name, new_value = mod
                    if row_index < len(df):  # Appliquer la modification seulement si l'index est valide
                        df.loc[row_index, column_name] = new_value
                st.write('### DataFrame modifié :')
                st.dataframe(df)

                # Sauvegarder le DataFrame modifié sans signature
                st.session_state.modified_df = df.copy()

                # Réinitialiser la liste des modifications
                st.session_state.modifications = []

        with col2:
            if st.button("Réinitialiser les modifications"):
                if 'modifications' in st.session_state:
                    st.session_state.modifications = []
                st.experimental_rerun()

        with col3:
            with st.expander("Ajouter une signature", expanded=False):
                user_name = st.text_input("Votre nom")
                if st.button("Ajouter Signature"):
                    if user_name:
                        if 'modified_df' in st.session_state:
                            df_with_signature = st.session_state.modified_df.copy()
                            signature = f"Modifié par {user_name} le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            df_with_signature.at[0, 'Signature'] = signature
                            df_with_signature = ensure_signature_at_end(df_with_signature)
                            st.write('### DataFrame avec signature :')
                            st.dataframe(df_with_signature)
                            st.session_state.modified_df = df_with_signature
                        else:
                            st.error("Veuillez appliquer les modifications avant d'ajouter une signature.")
                    else:
                        st.error("Veuillez entrer votre nom pour ajouter une signature.")

        #--------------------------------------------------Options pour télécharger-----------------------------------------------------------
        st.write('### Télécharger les modifications :')
        with st.expander("Options de téléchargement", expanded=False):
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

            if 'modified_df' in st.session_state:
                modified_json = st.session_state.modified_df.to_json(orient='records', indent=2)
                modified_csv = st.session_state.modified_df.to_csv(index=False).encode('utf-8')

                try:
                    buffer = io.BytesIO()
                    # Convertir explicitement les colonnes en types compatibles
                    for col in st.session_state.modified_df.columns:
                        if st.session_state.modified_df[col].dtype == 'object':
                            st.session_state.modified_df[col] = st.session_state.modified_df[col].astype('string')

                    st.session_state.modified_df.to_parquet(buffer, index=False)
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
                except Exception as e:
                    st.error(f"Erreur lors de la conversion en Parquet: {e}")

            st.markdown('</div>', unsafe_allow_html=True)
