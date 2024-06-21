import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF
from io import BytesIO


def load_csv():
    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df
    return None


def download_csv(dataframe, filename="reporte.csv"):
    csv = dataframe.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Codificación en base64
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar reporte CSV</a>'
    return href


def plot_kpis_by_person(dataframe, name, kpi_columns):
    person_data = dataframe[dataframe['Nombre'] == name]
    person_data = person_data.set_index('Mes')[kpi_columns]
    st.line_chart(person_data)


def plot_kpis_by_month(dataframe, month, kpi_columns):
    month_data = dataframe[dataframe['Mes'] == month]
    month_data = month_data.set_index('Nombre')[kpi_columns]
    st.bar_chart(month_data)


def display_averages(dataframe):
    average_kpis_responsibilities = dataframe.groupby('Nombre')[kpi_columns_responsibilities].mean()
    average_kpis_values = dataframe.groupby('Nombre')[kpi_columns_values].mean()

    overall_average_kpis_responsibilities = average_kpis_responsibilities.mean()
    overall_average_kpis_values = average_kpis_values.mean()

    st.subheader("Resumen de Promedios Generales")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=kpi_names['KPI_1'], value=f"{overall_average_kpis_responsibilities[kpi_names['KPI_1']]:.2f}")
        st.metric(label=kpi_names['KPI_2'], value=f"{overall_average_kpis_responsibilities[kpi_names['KPI_2']]:.2f}")
        st.metric(label=kpi_names['KPI_3'], value=f"{overall_average_kpis_responsibilities[kpi_names['KPI_3']]:.2f}")
        st.metric(label=kpi_names['KPI_4'], value=f"{overall_average_kpis_responsibilities[kpi_names['KPI_4']]:.2f}")
    with col2:
        st.metric(label=kpi_names['KPI_SS_1'], value=f"{overall_average_kpis_values[kpi_names['KPI_SS_1']]:.2f}")
        st.metric(label=kpi_names['KPI_SS_2'], value=f"{overall_average_kpis_values[kpi_names['KPI_SS_2']]:.2f}")
        st.metric(label=kpi_names['KPI_SS_3'], value=f"{overall_average_kpis_values[kpi_names['KPI_SS_3']]:.2f}")
        st.metric(label=kpi_names['KPI_SS_4'], value=f"{overall_average_kpis_values[kpi_names['KPI_SS_4']]:.2f}")
        st.metric(label=kpi_names['KPI_SS_5'], value=f"{overall_average_kpis_values[kpi_names['KPI_SS_5']]:.2f}")

    return average_kpis_responsibilities, average_kpis_values, overall_average_kpis_responsibilities, overall_average_kpis_values


def generate_pdf(dataframe, name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Reporte de KPIs para {name}", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="KPIs por Mes", ln=True)
    fig = plot_kpis_by_person(dataframe, name, kpi_columns_responsibilities)
    pdf.image(BytesIO(fig_to_image(fig)), x=10, y=40, w=180)

    fig = plot_kpis_by_person(dataframe, name, kpi_columns_values)
    pdf.image(BytesIO(fig_to_image(fig)), x=10, y=140, w=180)

    pdf.output(f"reporte_{name}.pdf")
    return pdf


def fig_to_image(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf


st.title('Visualización de KPIs')
st.sidebar.subheader('Ingresar Nombres de KPIs')

kpi_names = {
    'KPI_1': st.sidebar.text_input('Nombre para KPI_1 (Responsabilidades)', value='Número de tareas completadas por sprint'),
    'KPI_2': st.sidebar.text_input('Nombre para KPI_2 (Responsabilidades)', value='Número de errores de código reportados por el equipo de QA'),
    'KPI_3': st.sidebar.text_input('Nombre para KPI_3 (Responsabilidades)', value='Clockify'),
    'KPI_4': st.sidebar.text_input('Nombre para KPI_4 (Responsabilidades)', value='Educación'),
    'KPI_SS_1': st.sidebar.text_input('Nombre para KPI_SS_1 (Valores de la Empresa)', value='Excelencia'),
    'KPI_SS_2': st.sidebar.text_input('Nombre para KPI_SS_2 (Valores de la Empresa)', value='Actitud de servicio'),
    'KPI_SS_3': st.sidebar.text_input('Nombre para KPI_SS_3 (Valores de la Empresa)', value='Trabajo en equipo'),
    'KPI_SS_4': st.sidebar.text_input('Nombre para KPI_SS_4 (Valores de la Empresa)', value='Continúa búsqueda de excelencia'),
    'KPI_SS_5': st.sidebar.text_input('Nombre para KPI_SS_5 (Valores de la Empresa)', value='Pasión por el alto desempeño')
}


if all(kpi_names.values()):
    st.sidebar.success('Todos los nombres de los KPIs han sido ingresados.')

    df = load_csv()

    if df is not None:
        df = df.rename(columns={
            'KPI_1': kpi_names['KPI_1'],
            'KPI_2': kpi_names['KPI_2'],
            'KPI_3': kpi_names['KPI_3'],
            'KPI_4': kpi_names['KPI_4'],
            'KPI_SS_1': kpi_names['KPI_SS_1'],
            'KPI_SS_2': kpi_names['KPI_SS_2'],
            'KPI_SS_3': kpi_names['KPI_SS_3'],
            'KPI_SS_4': kpi_names['KPI_SS_4'],
            'KPI_SS_5': kpi_names['KPI_SS_5']
        })

        kpi_columns_responsibilities = [
            kpi_names['KPI_1'],
            kpi_names['KPI_2'],
            kpi_names['KPI_3'],
            kpi_names['KPI_4']
        ]

        kpi_columns_values = [
            kpi_names['KPI_SS_1'],
            kpi_names['KPI_SS_2'],
            kpi_names['KPI_SS_3'],
            kpi_names['KPI_SS_4'],
            kpi_names['KPI_SS_5']
        ]

        avg_responsibilities, avg_values, overall_avg_responsibilities, overall_avg_values = display_averages(df)

        st.sidebar.subheader('Filtrar por Nombre')
        selected_name = st.sidebar.selectbox('Selecciona un nombre', df['Nombre'].unique())
        if selected_name:
            st.subheader(f'KPIs de {selected_name} por Mes')
            plot_kpis_by_person(df, selected_name, kpi_columns_responsibilities)
            plot_kpis_by_person(df, selected_name, kpi_columns_values)

            #if st.button(f'Descargar Reporte PDF para {selected_name}'):
                #pdf = generate_pdf(df, selected_name)
                #st.download_button(
                    #label="Descargar Reporte PDF",
                    #data=pdf,
                    #file_name=f'reporte_{selected_name}.pdf',
                    #mime='application/octet-stream'
                #)

        st.sidebar.subheader('Filtrar por Mes')
        selected_month = st.sidebar.selectbox('Selecciona un mes', df['Mes'].unique())
        if selected_month:
            st.subheader(f'KPIs del Mes de {selected_month}')
            plot_kpis_by_month(df, selected_month, kpi_columns_responsibilities)
            plot_kpis_by_month(df, selected_month, kpi_columns_values)

        st.header('Explorar Datos')
        st.subheader("Promedio de KPIs por Persona (Responsabilidades)")
        st.dataframe(avg_responsibilities)

        st.subheader("Promedio de KPIs por Persona (Valores de la Empresa)")
        st.dataframe(avg_values)
else:
    st.sidebar.error('Por favor, ingrese todos los nombres de los KPIs antes de cargar el archivo CSV.')