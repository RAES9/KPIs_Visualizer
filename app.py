import streamlit as st
import pandas as pd


def load_csv():
    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df
    return None


def plot_kpis_by_person_st(dataframe, name, kpi_columns):
    person_data = dataframe[dataframe['Nombre'] == name]
    person_data['Mes'] = pd.Categorical(person_data['Mes'], categories=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], ordered=True)
    person_data = person_data.sort_values('Mes').set_index('Mes')[kpi_columns]
    st.line_chart(person_data)
    return person_data


def plot_kpis_by_month_st(dataframe, month, kpi_columns):
    month_data = dataframe[dataframe['Mes'] == month]
    month_data = month_data.set_index('Nombre')[kpi_columns]
    st.bar_chart(month_data)
    return month_data


def display_averages(dataframe):
    average_kpis_responsibilities = dataframe.groupby('Nombre')[kpi_columns_responsibilities].mean()
    average_kpis_values = dataframe.groupby('Nombre')[kpi_columns_values].mean()

    overall_average_kpis_responsibilities = average_kpis_responsibilities.mean()
    overall_average_kpis_values = average_kpis_values.mean()

    st.subheader("Resumen de Promedios Generales")
    col1, col2 = st.columns(2)
    with col1:
        for i in range(1, num_kpis_responsibilities + 1):
            st.metric(label=kpi_names[f'KPI_{i}'], value=f"{overall_average_kpis_responsibilities[kpi_names[f'KPI_{i}']]:.2f}")
    with col2:
        for i in range(1, num_kpis_values + 1):
            st.metric(label=kpi_names[f'KPI_SS_{i}'], value=f"{overall_average_kpis_values[kpi_names[f'KPI_SS_{i}']]:.2f}")

    return average_kpis_responsibilities, average_kpis_values, overall_average_kpis_responsibilities, overall_average_kpis_values


st.title('Visualización de KPIs')

st.sidebar.subheader('Ingresar Cantidad de KPIs')
num_kpis_responsibilities = st.sidebar.number_input('Cantidad de KPIs (Habilidates Tecnicas)', min_value=1, step=1, value=4)
num_kpis_values = st.sidebar.number_input('Cantidad de KPIs (Habilidates Blandas)', min_value=1, step=1, value=5)

st.sidebar.subheader('Ingresar Nombres de KPIs')

kpi_names = {}
for i in range(1, num_kpis_responsibilities + 1):
    kpi_names[f'KPI_{i}'] = st.sidebar.text_input(f'Nombre para KPI_{i} (Habilidad Tecnica)', value=f'KPI_{i}')

for i in range(1, num_kpis_values + 1):
    kpi_names[f'KPI_SS_{i}'] = st.sidebar.text_input(f'Nombre para KPI_SS_{i} (Habilidad Blanda)', value=f'KPI_SS_{i}')

if all(kpi_names.values()):
    st.sidebar.success('Todos los nombres de los KPIs han sido ingresados.')

    df = load_csv()

    if df is not None:
        rename_dict = {f'KPI_{i}': kpi_names[f'KPI_{i}'] for i in range(1, num_kpis_responsibilities + 1)}
        rename_dict.update({f'KPI_SS_{i}': kpi_names[f'KPI_SS_{i}'] for i in range(1, num_kpis_values + 1)})
        df = df.rename(columns=rename_dict)

        kpi_columns_responsibilities = [kpi_names[f'KPI_{i}'] for i in range(1, num_kpis_responsibilities + 1)]
        kpi_columns_values = [kpi_names[f'KPI_SS_{i}'] for i in range(1, num_kpis_values + 1)]

        avg_responsibilities, avg_values, overall_avg_responsibilities, overall_avg_values = display_averages(df)

        st.sidebar.subheader('Filtrar por Nombre')
        selected_name = st.sidebar.selectbox('Selecciona un nombre', df['Nombre'].unique())
        if selected_name:
            st.subheader(f'KPIs de {selected_name} por Mes')
            person_data_responsibilities = plot_kpis_by_person_st(df, selected_name, kpi_columns_responsibilities)
            person_data_values = plot_kpis_by_person_st(df, selected_name, kpi_columns_values)

        st.sidebar.subheader('Filtrar por Mes')
        selected_month = st.sidebar.selectbox('Selecciona un mes', df['Mes'].unique())
        if selected_month:
            st.subheader(f'KPIs del Mes de {selected_month}')
            plot_kpis_by_month_st(df, selected_month, kpi_columns_responsibilities)
            plot_kpis_by_month_st(df, selected_month, kpi_columns_values)
else:
    st.sidebar.error('Por favor, ingrese todos los nombres de los KPIs antes de cargar el archivo CSV.')