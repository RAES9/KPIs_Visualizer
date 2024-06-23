import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import base64

# Función para cargar y mostrar el archivo CSV
def load_csv():
    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df
    return None

# Función para mostrar gráficos lineales por persona en Streamlit
def plot_kpis_by_person_st(dataframe, name, kpi_columns):
    person_data = dataframe[dataframe['Nombre'] == name]
    person_data = person_data.set_index('Mes')[kpi_columns]
    st.line_chart(person_data)
    return person_data

# Función para mostrar gráficos de barras por mes en Streamlit
def plot_kpis_by_month_st(dataframe, month, kpi_columns):
    month_data = dataframe[dataframe['Mes'] == month]
    month_data = month_data.set_index('Nombre')[kpi_columns]
    st.bar_chart(month_data)
    return month_data

# Función para calcular y mostrar los promedios
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

# Función para convertir dataframe a imagen para PDF
def df_to_image(df):
    buf = BytesIO()
    fig = df.plot().get_figure()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf

# Función para generar el reporte PDF
def generate_pdf(dataframe, name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Reporte de KPIs para {name}", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="KPIs por Mes", ln=True)

    buf = df_to_image(dataframe)
    pdf.image(buf, x=10, y=40, w=180)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Main
st.title('Visualización de KPIs')

# Ingresar cantidad de KPIs
st.sidebar.subheader('Ingresar Cantidad de KPIs')
num_kpis_responsibilities = st.sidebar.number_input('Cantidad de KPIs de Responsabilidades', min_value=1, step=1, value=4)
num_kpis_values = st.sidebar.number_input('Cantidad de KPIs de Valores de la Empresa', min_value=1, step=1, value=5)

# Ingresar nombres de los KPIs
st.sidebar.subheader('Ingresar Nombres de KPIs')

kpi_names = {}
for i in range(1, num_kpis_responsibilities + 1):
    kpi_names[f'KPI_{i}'] = st.sidebar.text_input(f'Nombre para KPI_{i} (Responsabilidades)', value=f'KPI_{i}')

for i in range(1, num_kpis_values + 1):
    kpi_names[f'KPI_SS_{i}'] = st.sidebar.text_input(f'Nombre para KPI_SS_{i} (Valores de la Empresa)', value=f'KPI_SS_{i}')

# Asegurarse que todos los nombres han sido ingresados
if all(kpi_names.values()):
    st.sidebar.success('Todos los nombres de los KPIs han sido ingresados.')
    # Cargar el archivo CSV
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

            # Botón para generar y descargar el reporte PDF
            if st.button(f'Descargar Reporte PDF para {selected_name}'):
                pdf = generate_pdf(df, selected_name)
                st.download_button(
                    label="Descargar Reporte PDF",
                    data=pdf,
                    file_name=f'reporte_{selected_name}.pdf',
                    mime='application/octet-stream'
                )

        st.sidebar.subheader('Filtrar por Mes')
        selected_month = st.sidebar.selectbox('Selecciona un mes', df['Mes'].unique())
        if selected_month:
            st.subheader(f'KPIs del Mes de {selected_month}')
            plot_kpis_by_month_st(df, selected_month, kpi_columns_responsibilities)
            plot_kpis_by_month_st(df, selected_month, kpi_columns_values)
else:
    st.sidebar.error('Por favor, ingrese todos los nombres de los KPIs antes de cargar el archivo CSV.')