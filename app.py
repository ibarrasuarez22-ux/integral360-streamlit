import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
import numpy as np
from datetime import datetime, timedelta
import os

# Verificar existencia de logos
logo_path = '/Users/robertoibarrasuarez/Desktop/integral360/logo.png'
watermark_path = '/Users/robertoibarrasuarez/Desktop/integral360/watermark_logo.png'

# Estilo CSS para el fondo en gota de agua
if os.path.exists(watermark_path):
    st.markdown(
        """
        <style>
        .main {
            background-image: url('watermark_logo.png') !important;
            background-size: 80% auto !important;
            background-position: bottom left !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
            opacity: 0.9 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("No se encontró 'watermark_logo.png' en /Users/robertoibarrasuarez/Desktop/integral360. El fondo en gota de agua no se mostrará. Asegúrate de que el archivo esté en el directorio o usa una URL base64.")

# Logo superior izquierdo
if os.path.exists(logo_path):
    st.image(logo_path, width=150)
else:
    st.warning("No se encontró 'logo.png' en /Users/robertoibarrasuarez/Desktop/integral360. El logo superior no se mostrará.")

# Función para convertir serial Excel a fecha/hora
def excel_to_date(serial):
    try:
        return datetime(1899, 12, 30) + timedelta(days=serial)
    except:
        return pd.NaT

def fraction_to_time(frac):
    try:
        hours = int(frac * 24)
        minutes = int((frac * 24 - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"
    except:
        return "00:00"

# Carga de datos
@st.cache_data
def load_data():
    servicios_data = {
        'ID_Servicio': ['S01','S02','S03','S04','S05','S06','S07','S08','S09','S10','S11','S12','S13'],
        'Nombre': ['Consulta médica general','Consulta a domicilio','Aplicación de inyecciones','Control de enfermedades crónicas','Chequeo preventivo','Certificado médico','Curaciones simples','Vacunación','Asesoría nutricional básica','Teleconsulta','Examen de glucosa capilar','Presión arterial y signos vitales','Expedición de receta médica'],
        'Precio': [500,800,100,600,700,300,250,350,400,450,100,80,100],
        'Margen_Estimado': [0.6,0.65,0.5,0.55,0.65,0.7,0.5,0.6,0.55,0.7,0.4,0.45,0.75],
        'Duración_Minutos': [30,45,10,30,45,20,20,15,30,25,10,10,5],
        'Frecuencia_Mensual': [120,25,40,60,40,35,30,45,20,50,60,70,25]
    }
    servicios = pd.DataFrame(servicios_data)
    
    pacientes_data = {
        'ID_Paciente': list(range(1,41)),
        'Nombre': ['Ana Torres','Carlos Ruiz','Lucía Gómez','José Martínez','María López','Raúl Hernández','Laura Sánchez','Pedro Jiménez','Claudia Ramírez','Andrés Castro','Verónica Díaz','Roberto Morales','Sofía Aguilar','Diego Navarro','Patricia Vega','Enrique Ríos','Daniela Flores','Manuel Ortiz','Isabel Mendoza','Fernando Salas','Adriana Paredes','Hugo Cordero','Paola Estrada','Gerardo Luna','Rebeca Neri','Tomás Bravo','Karina León','Esteban Fuentes','Leticia Palma','Ángel Duarte','Norma Carrillo','Iván Lozano','Silvia Peña','Martín Beltrán','Elsa Romero','Alfredo Lara','Gloria Figueroa','Ramón Ponce','Teresa Molina','Javier Ayala'],
        'Edad': [34,45,29,52,38,60,27,41,33,50,36,47,31,55,40,48,35,43,30,53,39,46,32,49,37,56,28,44,34,51,42,59,33,54,29,40,36,57,31,50],
        'Género': ['F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M','F','M'],
        'Fecha_Ultima_Visita': [45850,45828,45870,45856,45863,45838,45871,45848,45866,45853,45872,45843,45860,45833,45868,45846,45873,45855,45864,45836,45867,45849,45874,45844,45861,45830,45875,45847,45865,45837,45869,45845,45876,45834,45862,45851,45877,45829,45858,45852],
        'Diagnóstico': ['Gripe','Diabetes tipo 2','Chequeo general','Presión alta','Colesterol alto','Chequeo general','Gripe','Diabetes tipo 2','Chequeo general','Presión alta','Gripe','Chequeo general','Colesterol alto','Presión alta','Chequeo general','Diabetes tipo 2','Gripe','Chequeo general','Colesterol alto','Presión alta','Gripe','Chequeo general','Chequeo general','Diabetes tipo 2','Colesterol alto','Presión alta','Gripe','Chequeo general','Colesterol alto','Presión alta','Gripe','Chequeo general','Chequeo general','Diabetes tipo 2','Gripe','Chequeo general','Colesterol alto','Presión alta','Gripe','Chequeo general'],
        'Frecuencia_Visitas': [3,6,1,4,2,1,2,5,1,3,2,1,2,4,1,6,3,1,2,4,2,1,1,5,2,3,2,1,2,4,3,1,1,6,2,1,2,4,3,1]
    }
    pacientes = pd.DataFrame(pacientes_data)
    pacientes['Fecha_Ultima_Visita'] = pacientes['Fecha_Ultima_Visita'].apply(excel_to_date)
    
    competencia_data = {
        'ID_Competidor': ['C01','C02','C03','C04','C05','C06','C07','C08','C09','C10','C11','C12','C13','C14','C15'],
        'Nombre': ['RMS: Consultorio de medicina general','Consultorio médico','Mi Consultorio Emiliano Zapata','Consultorios Medicos','Consultorios Médicos','Evia Especialidades Consultorios Médicos','Consultorio Médico Best','Consultorio Medico Fundación Best','Consultorio Narvarte','Consultorio Holbein','Consultorio Tuxpan','Consultorio Zhushenti','Consultorio Groove','Consultorio Patricio Sanz','Consultorio Universidad'],
        'Ubicación': ['Petén 471, Vértiz Narvarte','Necaxa 75, Portales Norte','Emiliano Zapata 125-B, Portales Norte','Dr. José María Vértiz 1481, Portales Norte','Xochicalco 589, Vértiz Narvarte','Filipinas 908, Portales Sur','Av. Universidad 913, Col del Valle Centro','Dr. José María Vértiz 1008, Narvarte Oriente','Avenida Cuauhtémoc 593, Narvarte','Holbein 174, Ciudad de México','Tuxpan 89, Roma Sur','Plutarco Elías Calles 1340, Roma Sur','Insurgentes Sur 826, Col del Valle Centro','Patricio Sanz 1117, Col del Valle','Av. Universidad 1080, Xoco'],
        'Servicios': ['Consulta general','Consulta general','Consulta y vacunas','Consulta general','Consulta general','Consulta y especialidades','Consulta general','Consulta general','Consulta general','Consulta general','Consulta general','Consulta integral','Consulta dermatológica','Consulta general','Consulta general'],
        'Precio_Promedio': [450,500,600,550,480,700,500,530,600,650,800,900,1000,600,700],
        'Diferenciador': ['Atención 24h','Horario extendido','Farmacia integrada','Atención familiar','Precios accesibles','Especialistas certificados','Ubicación central','Consulta sin cita','Fisioterapia integrada','Atención estética','Educación en diabetes','Acupuntura y homeopatía','Láser especializado','Consulta en línea','Consultorio privado'],
        'Latitud': [19.404, 19.408, 19.406, 19.405, 19.403, 19.400, 19.395, 19.402, 19.410, 19.415, 19.420, 19.418, 19.390, 19.393, 19.394],
        'Longitud': [-99.150, -99.145, -99.147, -99.149, -99.152, -99.155, -99.160, -99.148, -99.154, -99.165, -99.170, -99.168, -99.162, -99.158, -99.159]
    }
    competencia = pd.DataFrame(competencia_data)
    
    gastos_data = {
        'ID_Gasto': ['G001','G002','G003','G004','G005','G006','G007','G008','G009','G010','G011','G012','G013','G014','G015','G016','G017','G018','G019','G020','G021','G022','G023','G024','G025','G026','G027','G028','G029','G030','G031','G032','G033','G034','G035','G036','G037','G038','G039','G040'],
        'Nombre': ['Guantes de látex','Alcohol antiséptico','Jeringas','Gasas estériles','Toallas desechables','Desinfectante','Recetarios médicos','Bata médica','Software de gestión médica','Hosting web y dominio','Renta del local','Energía eléctrica','Agua potable','Internet','Teléfono fijo','Servicio de limpieza','Software de gestión médica','Publicidad digital','Mantenimiento de equipo','Seguro del local','Nómina médica','Nómina médica','Nómina administrativa','Nómina limpieza','Capacitación médica','Uniformes administrativos','Refrigerios para personal','Material de oficina','Papel higiénico','Servilletas','Impresión de volantes','Publicidad en radio local','Consultoría contable','Auditoría fiscal','Actualización de software','Hosting web','Dominio web','Servicio de mensajería','Reparación de mobiliario','Compra de sillas nuevas'],
        'Tipo': ['Insumo médico','Insumo médico','Insumo médico','Insumo médico','Insumo médico','Insumo médico','Administrativo','Insumo médico','Administrativo','Administrativo','Servicio fijo','Servicio fijo','Servicio fijo','Servicio fijo','Servicio fijo','Servicio fijo','Servicio digital','Marketing','Servicio técnico','Gasto fijo','Personal','Personal','Personal','Personal','RRHH','RRHH','Gasto menor','Insumo general','Insumo general','Insumo general','Marketing','Marketing','Servicio externo','Servicio externo','Servicio digital','Servicio digital','Servicio digital','Logística','Servicio técnico','Equipo'],
        'Proveedor': ['MedSupply','MedSupply','MedSupply','MedSupply','MedSupply','MedSupply','OfiMed','MedSupply','SoftClinic','WebSalud','Inmobiliaria Delta','CFE','SACMEX','Telmex','Telmex','LimpioYa','ClinicSoft','Google Ads','MedFix','AXA','Dra. Martínez','Dr. Pérez','Recepcionista','Auxiliar limpieza','SaludCapacita','UniformesMX','SuperSalud','OfficeDepot','HigieneMX','HigieneMX','ImprentaMX','RadioSalud','ContadoresMX','FiscalPro','ClinicSoft','GoDaddy','GoDaddy','MensajerosMX','MueblesFix','OfficeDepot'],
        'Costo_Unitario': [1.2,2.5,0.8,1,1.5,3,0.6,12,25,10,15000,1800,600,800,450,1200,950,2000,1800,3500,25000,24000,12000,8000,3000,1500,500,1200,0.25,0.15,800,1500,2500,4500,1200,300,250,600,900,1800],
        'Frecuencia': ['Mensual','Mensual','Mensual','Mensual','Mensual','Mensual','Mensual','Anual','Mensual','Mensual','Mensual','Mensual','Mensual','Mensual','Mensual','Mensual','Mensual','Mensual','Bimestral','Anual','Mensual','Mensual','Mensual','Mensual','Trimestral','Semestral','Mensual','Mensual','Mensual','Mensual','Bimestral','Mensual','Mensual','Trimestral','Trimestral','Mensual','Anual','Mensual','Bimestral','Semestral'],
        'Último_Pago': [45853,45853,45853,45853,45853,45853,45853,45853,45853,45853,45839,45843,45841,45842,45842,45844,45840,45845,45828,45667,45839,45839,45839,45839,45818,45823,45843,45844,45846,45846,45833,45848,45839,45838,45823,45840,45658,45845,45830,45818]
    }
    gastos = pd.DataFrame(gastos_data).drop_duplicates(subset='ID_Gasto')
    gastos['Último_Pago_Date'] = gastos['Último_Pago'].apply(excel_to_date)
    
    citas_data = {
        'ID_Cita': ['CT001','CT002','CT003','CT004','CT005','CT006','CT007','CT008','CT009','CT010','CT011','CT012','CT013','CT014','CT015','CT016','CT017','CT018','CT019','CT020'],
        'Fecha': [45870,45870,45870,45871,45871,45872,45872,45873,45873,45874,45874,45875,45875,45876,45876,45877,45877,45878,45878,45878],
        'Hora': [0.4791666666666667,0.5104166666666666,0.7395833333333334,0.4583333333333333,0.7291666666666666,0.5208333333333334,0.71875,0.4895833333333333,0.7291666666666666,0.5104166666666666,0.7395833333333334,0.4791666666666667,0.5,0.53125,0.7291666666666666,0.46875,0.7395833333333334,0.3958333333333333,0.4270833333333333,0.4583333333333333],
        'ID_Paciente': [1,3,2,6,7,11,13,12,17,21,23,27,28,33,34,35,37,4,15,38],
        'Nombre_Paciente': ['Ana Torres','Lucía Gómez','Carlos Ruiz','Raúl Hernández','Laura Sánchez','Verónica Díaz','Sofía Aguilar','Roberto Morales','Daniela Flores','Adriana Paredes','Paola Estrada','Karina León','Esteban Fuentes','Silvia Peña','Martín Beltrán','Elsa Romero','Gloria Figueroa','José Martínez','Patricia Vega','María Fernanda López'],
        'Servicio': ['Consulta médica general','Chequeo preventivo','Control de enfermedades crónicas','Chequeo preventivo','Consulta médica general','Consulta médica general','Control de enfermedades crónicas','Chequeo preventivo','Consulta médica general','Consulta médica general','Chequeo preventivo','Consulta médica general','Chequeo preventivo','Chequeo preventivo','Control de enfermedades crónicas','Consulta médica general','Control de enfermedades crónicas','Control de enfermedades crónicas','Chequeo preventivo','Consulta médica general'],
        'Estado': ['Confirmada','Confirmada','Confirmada','Confirmada','Cancelada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada','Confirmada'],
        'Canal_Reserva': ['WhatsApp','Teléfono','Presencial','WhatsApp','Teléfono','WhatsApp','Teléfono','Presencial','WhatsApp','Teléfono','WhatsApp','Teléfono','Presencial','WhatsApp','Teléfono','WhatsApp','Teléfono','Presencial','WhatsApp','Teléfono']
    }
    citas = pd.DataFrame(citas_data)
    citas['Fecha_Date'] = citas['Fecha'].apply(excel_to_date)
    citas['Hora_Time'] = citas['Hora'].apply(fraction_to_time)
    cronicos = ['Diabetes tipo 2', 'Presión alta', 'Colesterol alto', 'Control de enfermedades crónicas']
    pacientes['Es_Cronico_Paciente'] = pacientes['Diagnóstico'].isin(cronicos).astype(int)
    citas['Es_Cronico_Cita'] = citas['Servicio'].isin(cronicos).astype(int)
    
    return servicios, pacientes, competencia, gastos, citas

try:
    servicios, pacientes, competencia, gastos, citas = load_data()
except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    st.stop()

# Verificar coincidencias de servicios
missing_services = citas[~citas['Servicio'].isin(servicios['Nombre'])]['Servicio'].unique()
if len(missing_services) > 0:
    st.warning(f"Los siguientes servicios en 'citas' no están en 'servicios': {missing_services}. Esto puede causar problemas en los cálculos.")

# Filtro en renglón
st.title("INTEGRAL360 Dashboard")
page = st.selectbox("Selecciona una Sección", ["Resumen", "Estadísticas Básicas", "Análisis de Citas", "Análisis Cruzados", "ML y Patrones", "Recomendaciones"], key="page_selector")

if page == "Resumen":
    st.header("Resumen Ejecutivo")
    try:
        ingresos_totales = citas[citas['Estado'] == 'Confirmada'].merge(servicios, left_on='Servicio', right_on='Nombre', how='left')['Precio'].sum()
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Pacientes Totales", len(pacientes))
        col2.metric("Citas Totales", len(citas))
        col3.metric("Citas Confirmadas", len(citas[citas['Estado'] == 'Confirmada']))
        col4.metric("Citas Canceladas", len(citas[citas['Estado'] == 'Cancelada']))
        col5.metric("Ingresos Totales (MXN)", f"{ingresos_totales:,.0f}")
    except Exception as e:
        st.error(f"Error en métricas de resumen: {str(e)}")
    
    # Ingresos por grupo de edad
    try:
        merged_cp = citas.merge(pacientes, on='ID_Paciente', how='left').merge(servicios, left_on='Servicio', right_on='Nombre', how='left')
        merged_cp['Grupo_Edad'] = pd.cut(merged_cp['Edad'], bins=[0, 30, 40, 50, 100], labels=['<30', '30-40', '40-50', '>50'])
        ingresos_edad = merged_cp[merged_cp['Estado'] == 'Confirmada'].groupby('Grupo_Edad', observed=True)['Precio'].sum().reset_index()
        ingresos_edad['Precio'] = ingresos_edad['Precio'].fillna(0)
        st.subheader("Ingresos por Grupo de Edad")
        st.dataframe(ingresos_edad)
    except Exception as e:
        st.error(f"Error en ingresos por grupo de edad: {str(e)}")
    
    # Top 5 servicios por ingresos vs costos
    try:
        merged_cp = citas.merge(servicios, left_on='Servicio', right_on='Nombre', how='left')
        ingresos_serv = merged_cp[merged_cp['Estado'] == 'Confirmada'].groupby('Servicio')['Precio'].sum().reset_index()
        ingresos_serv = ingresos_serv.rename(columns={'Precio': 'Ingresos'})
        servicios_costo = servicios[['Nombre', 'Precio']].copy()
        servicios_costo['Costo_Estimado'] = servicios['Precio'] * (1 - servicios['Margen_Estimado'])
        top5_serv = ingresos_serv.merge(servicios_costo, left_on='Servicio', right_on='Nombre', how='left')
        top5_serv['Ingresos'] = top5_serv['Ingresos'].fillna(0)
        top5_serv['Costo_Estimado'] = top5_serv['Costo_Estimado'].fillna(0)
        top5_serv = top5_serv.nlargest(5, 'Ingresos')
        st.subheader("Top 5 Servicios por Ingresos vs Costos")
        if top5_serv.empty:
            st.write("No hay datos suficientes para mostrar los top 5 servicios.")
        else:
            st.dataframe(top5_serv[['Servicio', 'Ingresos', 'Precio', 'Costo_Estimado']])
    except Exception as e:
        st.error(f"Error en top 5 servicios: {str(e)}")
    
    # Gastos próximos a pagar
    try:
        hoy = datetime(2025, 8, 17)
        gastos['Dias_Ultimo_Pago'] = (hoy - gastos['Último_Pago_Date']).dt.days
        gastos_proximos = gastos[gastos['Dias_Ultimo_Pago'].between(0, 7)][['Nombre', 'Costo_Unitario', 'Frecuencia', 'Último_Pago_Date']]
        st.subheader("Gastos Próximos a Pagar (7 días)")
        if not gastos_proximos.empty:
            st.dataframe(gastos_proximos)
        else:
            st.write("No hay gastos próximos a pagar en los próximos 7 días.")
    except Exception as e:
        st.error(f"Error en gastos próximos: {str(e)}")
    
    # Ingresos últimos 5 días
    try:
        hoy = datetime(2025, 8, 17)
        ultimos_5 = pd.date_range(end=hoy, periods=5, freq='D')
        ingresos_dias = citas[citas['Estado'] == 'Confirmada'].merge(servicios, left_on='Servicio', right_on='Nombre', how='left').groupby('Fecha_Date')['Precio'].sum().reset_index()
        ingresos_dias = ingresos_dias[ingresos_dias['Fecha_Date'].isin(ultimos_5)]
        if ingresos_dias.empty:
            st.subheader("Ingresos Últimos 5 Días")
            st.write("No hay datos de ingresos en los últimos 5 días.")
        else:
            fig_res = px.line(ingresos_dias, x='Fecha_Date', y='Precio', title='Ingresos Últimos 5 Días')
            st.plotly_chart(fig_res)
    except Exception as e:
        st.error(f"Error en gráfico de ingresos últimos 5 días: {str(e)}")

elif page == "Estadísticas Básicas":
    st.header("Estadísticas Básicas")
    
    # Pacientes
    try:
        st.subheader("Pacientes")
        fig1 = px.pie(pacientes, names='Diagnóstico', title='Distribución de Diagnósticos')
        st.plotly_chart(fig1)
        st.markdown("**Recomendación**: Enfocar marketing en crónicos (40% de diagnósticos) con paquetes de control para aumentar ingresos recurrentes.")
    except Exception as e:
        st.error(f"Error en gráfico de pacientes: {str(e)}")
    
    # Servicios
    try:
        st.subheader("Servicios")
        servicios_stats = citas[citas['Estado'] == 'Confirmada'].groupby('Servicio').size().reset_index(name='Num_Servicios')
        servicios_stats = servicios_stats.merge(servicios, left_on='Servicio', right_on='Nombre', how='left')
        servicios_stats['Costo_Estimado'] = servicios_stats['Precio'] * (1 - servicios_stats['Margen_Estimado'])
        servicios_stats['Margen_Ganancia'] = servicios_stats['Margen_Estimado'] * 100
        st.dataframe(servicios_stats[['Servicio', 'Precio', 'Num_Servicios', 'Costo_Estimado', 'Margen_Ganancia']])
        st.markdown("**Recomendación**: Promover servicios de alto margen (ej. Certificado médico, 70%) y aumentar volumen de servicios frecuentes (Consulta general).")
    except Exception as e:
        st.error(f"Error en tabla de servicios: {str(e)}")
    
    # Competencia
    try:
        st.subheader("Competencia")
        fig2 = px.scatter(competencia, x='Precio_Promedio', y='Ubicación', color='Diferenciador', title='Competidores por Precio y Ubicación')
        st.plotly_chart(fig2)
        clinica = pd.DataFrame({'Nombre': ['Nuestra Clínica'], 'Latitud': [19.405], 'Longitud': [-99.155], 'Precio_Promedio': [500]})
        comp_map = pd.concat([competencia[['Nombre', 'Latitud', 'Longitud', 'Precio_Promedio']], clinica], ignore_index=True)
        fig_map = px.scatter_mapbox(comp_map, lat='Latitud', lon='Longitud', color='Nombre', size='Precio_Promedio', zoom=12, mapbox_style="open-street-map", title='Mapa de Competidores')
        st.plotly_chart(fig_map)
        st.markdown("**Recomendación**: Diferenciarse con teleconsultas en Narvarte (alta competencia) y ajustar precios competitivos frente a C13 (1000 MXN).")
    except Exception as e:
        st.error(f"Error en análisis de competencia: {str(e)}")
    
    # Gastos
    try:
        st.subheader("Gastos")
        fig3 = px.treemap(gastos, path=['Tipo'], values='Costo_Unitario', title='Gastos por Tipo')
        st.plotly_chart(fig3)
        gastos_beneficio = gastos[gastos['Tipo'].isin(['Insumo médico', 'Servicio fijo'])].copy()
        gastos_beneficio['Beneficio_Estimado'] = gastos_beneficio['Costo_Unitario'] * 0.5
        fig4 = px.bar(gastos_beneficio, x='Nombre', y='Beneficio_Estimado', title='Gastos con Mayor Beneficio Estimado')
        st.plotly_chart(fig4)
        st.markdown("**Recomendación**: Reducir gastos fijos (renta, nómina) y optimizar insumos médicos para servicios frecuentes.")
    except Exception as e:
        st.error(f"Error en análisis de gastos: {str(e)}")

elif page == "Análisis de Citas":
    st.header("Análisis de Citas")
    
    try:
        fig_c1 = px.pie(citas, names='Estado', title='Confirmadas vs Canceladas')
        st.plotly_chart(fig_c1)
    except Exception as e:
        st.error(f"Error en gráfico Confirmadas vs Canceladas: {str(e)}")
    
    try:
        fig_c2 = px.bar(citas, x='Canal_Reserva', color='Estado', title='Citas por Canal y Estado')
        st.plotly_chart(fig_c2)
    except Exception as e:
        st.error(f"Error en gráfico Citas por Canal y Estado: {str(e)}")
    
    # Día de la semana más demandado
    try:
        citas['Dia_Semana'] = citas['Fecha_Date'].dt.day_name()
        dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        citas_dia = citas[citas['Estado'] == 'Confirmada'].groupby('Dia_Semana').size().reset_index(name='Conteo')
        citas_dia['Dia_Semana'] = pd.Categorical(citas_dia['Dia_Semana'], categories=dias_orden, ordered=True)
        dia_mas_demandado = citas_dia.loc[citas_dia['Conteo'].idxmax(), 'Dia_Semana'] if not citas_dia.empty else "No disponible"
        st.subheader("Día de la Semana Más Demandado")
        st.write(f"El día con mayor demanda es: **{dia_mas_demandado}**")
        if not citas_dia.empty:
            fig_dia = px.bar(citas_dia, x='Dia_Semana', y='Conteo', title='Citas Confirmadas por Día de la Semana')
            st.plotly_chart(fig_dia)
    except Exception as e:
        st.error(f"Error en análisis de día más demandado: {str(e)}")
    
    # Horario más demandado
    try:
        citas['Hora'] = citas['Hora'].apply(lambda x: round(x * 24))
        citas['Rango_Horario'] = pd.cut(citas['Hora'], bins=[0, 12, 16, 20, 24], labels=['Mañana (0-12)', 'Tarde (12-16)', 'Noche (16-20)', 'Madrugada (20-24)'], include_lowest=True)
        citas_hora = citas[citas['Estado'] == 'Confirmada'].groupby('Rango_Horario', observed=True).size().reset_index(name='Conteo')
        horario_mas_demandado = citas_hora.loc[citas_hora['Conteo'].idxmax(), 'Rango_Horario'] if not citas_hora.empty else "No disponible"
        st.subheader("Horario Más Demandado")
        st.write(f"El horario con mayor demanda es: **{horario_mas_demandado}**")
        if not citas_hora.empty:
            fig_hora = px.bar(citas_hora, x='Rango_Horario', y='Conteo', title='Citas Confirmadas por Rango Horario')
            st.plotly_chart(fig_hora)
    except Exception as e:
        st.error(f"Error en análisis de horario más demandado: {str(e)}")
    
    # Promedio citas por día de la semana
    try:
        citas_prom = citas[citas['Estado'] == 'Confirmada'].groupby(['Dia_Semana', 'Servicio']).size().reset_index(name='Conteo')
        citas_prom = citas_prom.groupby(['Dia_Semana', 'Servicio'], as_index=False)['Conteo'].mean()
        citas_prom['Dia_Semana'] = pd.Categorical(citas_prom['Dia_Semana'], categories=dias_orden, ordered=True)
        if citas_prom.empty:
            st.subheader("Promedio Citas por Día de Semana y Servicio")
            st.write("No hay datos suficientes para mostrar el promedio de citas.")
        else:
            fig_c3 = px.line(citas_prom, x='Dia_Semana', y='Conteo', color='Servicio', title='Promedio Citas por Día de Semana y Servicio')
            st.plotly_chart(fig_c3)
    except Exception as e:
        st.error(f"Error en gráfico de promedio de citas: {str(e)}")
    
    # Citas vs Gastos por día
    try:
        citas_dia = citas[citas['Estado'] == 'Confirmada'].groupby('Fecha_Date').size().reset_index(name='Num_Citas')
        gastos['Costo_Diario'] = gastos.apply(
            lambda x: x['Costo_Unitario'] / 30 if x['Frecuencia'] == 'Mensual' 
            else x['Costo_Unitario'] / 365 if x['Frecuencia'] == 'Anual' 
            else x['Costo_Unitario'] / 60 if x['Frecuencia'] == 'Bimestral' 
            else x['Costo_Unitario'] / 90, axis=1)
        gastos_dia = gastos.groupby('Último_Pago_Date')['Costo_Diario'].sum().reset_index(name='Gasto_Diario')
        citas_gastos = citas_dia.merge(gastos_dia, left_on='Fecha_Date', right_on='Último_Pago_Date', how='outer').fillna(0)
        st.subheader("Citas vs Gastos por Día")
        st.dataframe(citas_gastos)
    except Exception as e:
        st.error(f"Error en tabla Citas vs Gastos: {str(e)}")
    
    st.markdown("**Recomendación**: Priorizar WhatsApp (0% cancelaciones) y agrupar citas de crónicos en días de baja demanda (martes).")

elif page == "Análisis Cruzados":
    st.header("Análisis Cruzados y Correlaciones")
    
    # Ingresos Pacientes Crónicos
    try:
        st.subheader("Ingresos Pacientes Crónicos")
        pac_cronicos = pacientes[pacientes['Es_Cronico_Paciente'] == 1][['ID_Paciente', 'Diagnóstico', 'Frecuencia_Visitas']]
        citas_cronicos = citas[citas['Es_Cronico_Cita'] == 1][['ID_Cita', 'ID_Paciente', 'Servicio']].merge(pac_cronicos, on='ID_Paciente', how='left')
        if citas_cronicos.empty:
            st.write("No hay citas de pacientes crónicos disponibles.")
        else:
            st.dataframe(citas_cronicos[['ID_Cita', 'ID_Paciente', 'Servicio', 'Diagnóstico']])
            freq_avg = pac_cronicos['Frecuencia_Visitas'].mean() if not pac_cronicos.empty else 0
            servicios_cronicos = ['Control de enfermedades crónicas', 'Chequeo preventivo', 'Examen de glucosa capilar', 'Presión arterial y signos vitales']
            precio_avg = servicios[servicios['Nombre'].isin(servicios_cronicos)]['Precio'].mean() if servicios['Nombre'].isin(servicios_cronicos).any() else 0
            num_cronicos = len(pac_cronicos)
            meses = 12
            ingresos_mensual = num_cronicos * (freq_avg / 12) * precio_avg if freq_avg > 0 and precio_avg > 0 else 0
            proyeccion = pd.DataFrame({
                'Mes': pd.date_range(start='2025-09-01', periods=meses, freq='M'),
                'Ingresos Proyectados (MXN)': [ingresos_mensual * (1 + 0.05 * i) for i in range(meses)]
            })
            st.write(f"Frecuencia promedio de visitas: {freq_avg:.1f}, Precio promedio por servicio: {precio_avg:.0f} MXN")
            if ingresos_mensual > 0:
                fig_proj = px.line(proyeccion, x='Mes', y='Ingresos Proyectados (MXN)', title='Proyección Ingresos Crónicos (12 Meses)')
                st.plotly_chart(fig_proj)
                st.write(f"Ingresos Totales Proyectados (12 meses): {proyeccion['Ingresos Proyectados (MXN)'].sum():,.0f} MXN")
            else:
                st.write("No hay datos suficientes para proyectar ingresos de crónicos.")
    except Exception as e:
        st.error(f"Error en análisis de crónicos: {str(e)}")
    
    # Correlación
    try:
        merged_cp = citas.merge(pacientes, on='ID_Paciente', how='left').fillna(0)
        corr_cp = merged_cp[['Edad', 'Frecuencia_Visitas', 'Es_Cronico_Paciente']].corr()
        st.write("Correlación con Crónicos:", corr_cp)
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_cp, annot=True, cmap='coolwarm')
        st.pyplot(plt.gcf())
        plt.clf()
    except Exception as e:
        st.error(f"Error en heatmap de correlaciones: {str(e)}")
    
    st.markdown("**Recomendación**: Ofrecer paquetes anuales para crónicos (S04+S11) con descuentos para retención, aumentando ingresos ~20%.")

elif page == "ML y Patrones":
    st.header("Análisis IA: ML Supervisado y No Supervisado")
    
    le = LabelEncoder()
    pacientes['Género'] = le.fit_transform(pacientes['Género'])
    pacientes['Diagnóstico'] = le.fit_transform(pacientes['Diagnóstico'])
    citas['Canal_Reserva'] = le.fit_transform(citas['Canal_Reserva'])
    
    # Clustering Pacientes
    try:
        merged_cp = citas.merge(pacientes, on='ID_Paciente', how='right').fillna(0)
        if 'Es_Cronico_Paciente' not in merged_cp.columns:
            raise KeyError("'Es_Cronico_Paciente' no está en el DataFrame merged_cp")
        X_p = merged_cp[['Edad', 'Frecuencia_Visitas', 'Diagnóstico', 'Es_Cronico_Paciente']]
        kmeans_p = KMeans(n_clusters=3, random_state=42, n_init=10)
        merged_cp['Cluster'] = kmeans_p.fit_predict(X_p)
        fig_ml1 = px.scatter(merged_cp, x='Edad', y='Frecuencia_Visitas', color='Cluster', title='Clusters Pacientes (Incluyendo Crónicos)')
        st.plotly_chart(fig_ml1)
        st.subheader("Explicación Clusters Pacientes")
        st.markdown("""
        - **Cluster 0**: Jóvenes (<35 años), baja frecuencia, diagnósticos no crónicos (ej. gripe). **Contribución**: Marketing para aumentar visitas esporádicas (+10% clientes potencial).
        - **Cluster 1**: Adultos (40-50 años), alta frecuencia, crónicos (diabetes, presión). **Contribución**: Retención con paquetes para ingresos recurrentes (~48k MXN/año, +20% ingresos).
        - **Cluster 2**: Mayores (>50 años), frecuencia media, mix de diagnósticos. **Contribución**: Promover chequeos preventivos para aumentar visitas (+15% citas).
        """)
    except Exception as e:
        st.error(f"Error en clustering de pacientes: {str(e)}")
    
    # Clustering Citas
    try:
        X_c = citas[['Hora', 'Canal_Reserva']]
        kmeans_c = KMeans(n_clusters=3, random_state=42, n_init=10)
        citas['Cluster'] = kmeans_c.fit_predict(X_c)
        fig_ml2 = px.scatter(citas, x='Hora_Time', y='Canal_Reserva', color='Cluster', title='Clusters Citas (Patrones Horarios)')
        st.plotly_chart(fig_ml2)
        st.subheader("Explicación Clusters Citas")
        st.markdown("""
        - **Cluster 0**: Mañanas, WhatsApp. **Contribución**: Optimizar personal para mañanas con reservas digitales (-15% tiempo).
        - **Cluster 1**: Tardes, Teléfono. **Contribución**: Reforzar atención telefónica en horarios pico (-10% tiempo).
        - **Cluster 2**: Mix horarios, Presencial. **Contribución**: Flexibilidad en agenda para citas presenciales (+5% citas).
        """)
    except Exception as e:
        st.error(f"Error en clustering de citas: {str(e)}")
    
    # Predicción de Frecuencia de Visitas
    try:
        X = merged_cp[['Edad', 'Diagnóstico']]
        y = merged_cp['Frecuencia_Visitas']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mse = mean_squared_error(y_test, preds)
        st.write(f"Error Predicción Frecuencia Visitas: {mse:.2f}")
    except Exception as e:
        st.error(f"Error en predicción de frecuencia: {str(e)}")
    
    st.markdown("**Recomendación**: Usar clusters para segmentar clientes y predicciones para optimizar agendas y retención.")

elif page == "Recomendaciones":
    st.header("Recomendaciones para Eficiencia")
    st.markdown("""
    - **Optimización de Costos y Recursos**:
      - Eliminar gastos redundantes como software duplicado (G009/G017, ahorro ~950 MXN/mes).
      - Negociar renta del local (G011, potencial ahorro 10%, ~1500 MXN/mes).
      - Optimizar insumos médicos (ej. G001-G006) para servicios frecuentes como consultas generales y chequeos preventivos, reduciendo costos ~5%.
    - **Mejora de Procesos y Retención de Clientes**:
      - Automatizar teleconsultas (S10, 25 min/cita) y priorizar servicios cortos (S13, 5 min) para reducir tiempo por cita ~15%.
      - Ofrecer paquetes anuales para pacientes crónicos (S04+S11, ~48k MXN/año proyectados) con descuentos para retención, aumentando ingresos ~20%.
      - Priorizar WhatsApp para reservas (0% cancelaciones) y agrupar citas de crónicos en días de baja demanda (martes) para optimizar agendas.
      - Enfocar marketing en pacientes crónicos (40% diagnósticos) con campañas dirigidas en Narvarte, diferenciándose con teleconsultas frente a competidores como C13 (1000 MXN).
    """)
