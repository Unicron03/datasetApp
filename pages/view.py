import streamlit as st
import pandas as pd
import json
import io

st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
    }
    </style>
    <div class="title">View</div>
""", unsafe_allow_html=True)
st.write("")
st.write("")

# Fonction pour lire les fichiers
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

# Téléchargement du fichier
uploaded_file = st.file_uploader("Choisissez un fichier JSON, CSV ou Parquet", type=["json", "csv", "parquet"])

if uploaded_file is not None:
    df = load_file(uploaded_file)
    if df is not None:
        st.write('### DataFrame original :')
        st.dataframe(df)

        # Initialisation des filtres
        if 'simple_filter' not in st.session_state:
            st.session_state.simple_filter = None
        if 'advanced_filters' not in st.session_state:
            st.session_state.advanced_filters = []
        if 'filtered_df_simple' not in st.session_state:
            st.session_state.filtered_df_simple = None
        if 'filtered_df_advanced' not in st.session_state:
            st.session_state.filtered_df_advanced = None

        # Fonction pour convertir les valeurs des filtres
        def convert_value(value, dtype):
            if dtype == 'int64':
                return int(value)
            elif dtype == 'float64':
                return float(value)
            return value

        # Fonction pour appliquer les filtres avancés
        def apply_advanced_filters(df, filters):
            for column_name, condition, value in filters:
                col_dtype = df[column_name].dtype
                if condition == 'equals':
                    value = convert_value(value, col_dtype)
                    df = df[df[column_name] == value]
                elif condition == 'contains':
                    df = df[df[column_name].astype(str).str.contains(value, na=False)]
                elif condition == 'greater_than':
                    value = convert_value(value, col_dtype)
                    df = df[df[column_name] > value]
                elif condition == 'less_than':
                    value = convert_value(value, col_dtype)
                    df = df[df[column_name] < value]
                elif condition == 'between':
                    min_value, max_value = value
                    min_value = convert_value(min_value, col_dtype)
                    max_value = convert_value(max_value, col_dtype)
                    df = df[df[column_name].between(min_value, max_value)]
            return df

        # Recherche simple
        st.write('### Recherche simple :')
        simple_column = st.selectbox('Colonne', df.columns, key='simple_filter_column')
        simple_value = st.text_input('Valeur', key='simple_filter_value')
        if st.button('Appliquer filtre simple'):
            if not simple_value.strip():
                st.error("La valeur ne peut pas être vide.")
            else:
                st.session_state.simple_filter = (simple_column, simple_value)
                st.experimental_rerun()

        if st.session_state.simple_filter:
            column_name, value = st.session_state.simple_filter
            filtered_df_simple = df[df[column_name].astype(str).str.contains(value, na=False)]
            st.write('### DataFrame après filtrage simple :')
            st.dataframe(filtered_df_simple)

            # Sauvegarder le DataFrame filtré simple dans session_state
            st.session_state.filtered_df_simple = filtered_df_simple

        # Recherche avancée
        st.write('### Recherche avancée :')
        with st.form(key='advanced_filter_form'):
            column_name = st.selectbox('Colonne', df.columns, key='advanced_filter_column')
            condition = st.selectbox('Condition', ['equals', 'contains', 'greater_than', 'less_than', 'between'], key='advanced_filter_condition')
            if condition == 'between':
                value1 = st.text_input('Valeur minimale', key='advanced_filter_value1')
                value2 = st.text_input('Valeur maximale', key='advanced_filter_value2')
                value = (value1, value2)
            else:
                value = st.text_input('Valeur', key='advanced_filter_value')
            add_filter = st.form_submit_button('Ajouter le filtre')

        if add_filter:
            if condition == 'between' and (not value1.strip() or not value2.strip()):
                st.error("Les valeurs minimales et maximales ne peuvent pas être vides.")
            elif condition != 'between' and not value.strip():
                st.error("La valeur ne peut pas être vide.")
            else:
                st.session_state.advanced_filters.append((column_name, condition, value))
                st.experimental_rerun()

        # Afficher les filtres avancés en attente
        st.write('### Filtres avancés en attente :')
        for i, f in enumerate(st.session_state.advanced_filters):
            column_name, condition, value = f
            col1, col2 = st.columns([3, 1])
            with col1:
                if condition == 'between':
                    st.write(f"Colonne '{column_name}', Condition : {condition}, Valeurs : {value[0]} et {value[1]}")
                else:
                    st.write(f"Colonne '{column_name}', Condition : {condition}, Valeur : {value}")
            with col2:
                if st.button('Supprimer', key=f'delete_advanced_filter_{i}'):
                    st.session_state.advanced_filters.pop(i)
                    st.experimental_rerun()

        # Appliquer les filtres avancés et afficher le DataFrame filtré
        if st.button('Appliquer les filtres avancés'):
            if not st.session_state.advanced_filters:
                st.error("Aucun filtre avancé à appliquer.")
            else:
                filtered_df_advanced = apply_advanced_filters(df, st.session_state.advanced_filters)
                st.write('### DataFrame après filtrage avancé :')
                st.dataframe(filtered_df_advanced)

                # Sauvegarder le DataFrame filtré avancé dans session_state
                st.session_state.filtered_df_advanced = filtered_df_advanced

        # Options pour télécharger les filtres appliqués
        st.write('### Télécharger les filtres appliqués :')
        with st.expander("Options de téléchargement des filtres", expanded=False):
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

            if st.session_state.filtered_df_simple is not None:
                filtered_json_simple = st.session_state.filtered_df_simple.to_json(orient='records', indent=2)
                filtered_csv_simple = st.session_state.filtered_df_simple.to_csv(index=False).encode('utf-8')

                try:
                    buffer_simple = io.BytesIO()
                    for col in st.session_state.filtered_df_simple.columns:
                        if st.session_state.filtered_df_simple[col].dtype == 'object':
                            st.session_state.filtered_df_simple[col] = st.session_state.filtered_df_simple[col].astype('string')
                    st.session_state.filtered_df_simple.to_parquet(buffer_simple, index=False)
                    filtered_parquet_simple = buffer_simple.getvalue()

                    st.download_button(
                        label="Télécharger en JSON (Filtre simple)",
                        data=filtered_json_simple,
                        file_name="filtered_data_simple.json",
                        mime="application/json"
                    )
                    st.download_button(
                        label="Télécharger en CSV (Filtre simple)",
                        data=filtered_csv_simple,
                        file_name="filtered_data_simple.csv",
                        mime="text/csv"
                    )
                    st.download_button(
                        label="Télécharger en Parquet (Filtre simple)",
                        data=filtered_parquet_simple,
                        file_name="filtered_data_simple.parquet",
                        mime="application/octet-stream"
                    )
                except Exception as e:
                    st.error(f"Erreur lors de la conversion en Parquet: {e}")

            if st.session_state.filtered_df_advanced is not None:
                filtered_json_advanced = st.session_state.filtered_df_advanced.to_json(orient='records', indent=2)
                filtered_csv_advanced = st.session_state.filtered_df_advanced.to_csv(index=False).encode('utf-8')

                try:
                    buffer_advanced = io.BytesIO()
                    for col in st.session_state.filtered_df_advanced.columns:
                        if st.session_state.filtered_df_advanced[col].dtype == 'object':
                            st.session_state.filtered_df_advanced[col] = st.session_state.filtered_df_advanced[col].astype('string')
                    st.session_state.filtered_df_advanced.to_parquet(buffer_advanced, index=False)
                    filtered_parquet_advanced = buffer_advanced.getvalue()

                    st.download_button(
                        label="Télécharger en JSON (Filtres avancés)",
                        data=filtered_json_advanced,
                        file_name="filtered_data_advanced.json",
                        mime="application/json"
                    )
                    st.download_button(
                        label="Télécharger en CSV (Filtres avancés)",
                        data=filtered_csv_advanced,
                        file_name="filtered_data_advanced.csv",
                        mime="text/csv"
                    )
                    st.download_button(
                        label="Télécharger en Parquet (Filtres avancés)",
                        data=filtered_parquet_advanced,
                        file_name="filtered_data_advanced.parquet",
                        mime="application/octet-stream"
                    )
                except Exception as e:
                    st.error(f"Erreur lors de la conversion en Parquet: {e}")

            st.markdown('</div>', unsafe_allow_html=True)
