import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard de Análisis de Ventas")
st.markdown("---")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv('BD_EVALUACION.csv', encoding='latin1', low_memory=False)
    
    # Convertir 'Venta' a numérico
    df['Venta'] = pd.to_numeric(df['Venta'], errors='coerce')
    
    # Convertir 'Fecha Vta' a datetime
    df['Fecha Vta'] = pd.to_datetime(df['Fecha Vta'], format='%d/%m/%Y', errors='coerce')
    
    # Extraer la hora
    df['Hora'] = pd.to_datetime(df['Hora Vta'], format='%H:%M:%S', errors='coerce').dt.hour
    
    # Eliminar filas con valores nulos en Venta
    df = df.dropna(subset=['Venta'])
    
    return df

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Cargar datos
try:
    df = load_data()
    
    # Filtros en sidebar
    st.sidebar.subheader("Filtros de Fecha")
    
    # Filtro de rango de fechas
    min_date = df['Fecha Vta'].min().date()
    max_date = df['Fecha Vta'].max().date()
    
    fecha_inicio = st.sidebar.date_input(
        "Fecha inicial",
        min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    fecha_fin = st.sidebar.date_input(
        "Fecha final",
        max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro de tienda
    tiendas = ['Todas'] + sorted(df['Tienda'].unique().tolist())
    tienda_seleccionada = st.sidebar.selectbox("Seleccionar Tienda", tiendas)
    
    # Filtro de producto (búsqueda)
    productos = ['Todos'] + sorted(df['Producto'].unique().tolist())
    producto_seleccionado = st.sidebar.selectbox("Seleccionar Producto", productos)
    
    # Filtro de hora (rango)
    st.sidebar.subheader("Rango de Horas")
    hora_min = st.sidebar.slider("Hora mínima", 0, 23, 0)
    hora_max = st.sidebar.slider("Hora máxima", 0, 23, 23)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    # Filtro de fechas
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha Vta'].dt.date >= fecha_inicio) & 
        (df_filtrado['Fecha Vta'].dt.date <= fecha_fin)
    ]
    
    # Filtro de tienda
    if tienda_seleccionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Tienda'] == tienda_seleccionada]
    
    # Filtro de producto
    if producto_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Producto'] == producto_seleccionado]
    
    # Filtro de hora
    df_filtrado = df_filtrado[
        (df_filtrado['Hora'] >= hora_min) & 
        (df_filtrado['Hora'] <= hora_max)
    ]
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        venta_total = df_filtrado['Venta'].sum()
        st.metric("💰 Venta Total", f"${venta_total:,.2f}")
    
    with col2:
        num_tickets = df_filtrado['Ticket'].nunique()
        st.metric("🎫 Tickets Totales", f"{num_tickets:,}")
    
    with col3:
        ticket_promedio = venta_total / num_tickets if num_tickets > 0 else 0
        st.metric("📈 Ticket Promedio", f"${ticket_promedio:.2f}")
    
    with col4:
        num_productos = df_filtrado['Producto'].nunique()
        st.metric("📦 Productos Únicos", f"{num_productos:,}")
    
    st.markdown("---")
    
    # 1. Venta Total por Tienda
    st.header("🏪 1. Venta Total por Tienda")
    
    col1_1, col1_2 = st.columns([2, 1])
    
    with col1_1:
        venta_por_tienda = df_filtrado.groupby('Tienda')['Venta'].sum().sort_values(ascending=False)
        fig_tienda = px.bar(
            venta_por_tienda.reset_index(),
            x='Tienda',
            y='Venta',
            title='Venta Total por Tienda',
            color='Venta',
            color_continuous_scale='Viridis',
            text='Venta'
        )
        fig_tienda.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_tienda.update_layout(showlegend=False)
        st.plotly_chart(fig_tienda, use_container_width=True)
    
    with col1_2:
        st.dataframe(
            venta_por_tienda.reset_index().style.format({'Venta': '${:,.2f}'}),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # 2. Número de Tickets por Tienda
    st.header("🎫 2. Número de Tickets por Tienda")
    
    col2_1, col2_2 = st.columns([2, 1])
    
    with col2_1:
        tickets_por_tienda = df_filtrado.groupby('Tienda')['Ticket'].nunique().sort_values(ascending=False)
        fig_tickets = px.bar(
            tickets_por_tienda.reset_index(),
            x='Tienda',
            y='Ticket',
            title='Número de Tickets por Tienda',
            color='Ticket',
            color_continuous_scale='Plasma',
            text='Ticket'
        )
        fig_tickets.update_traces(textposition='outside')
        st.plotly_chart(fig_tickets, use_container_width=True)
    
    with col2_2:
        st.dataframe(
            tickets_por_tienda.reset_index().style.format({'Ticket': '{:,.0f}'}),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # 3. Venta por Día
    st.header("📅 3. Venta por Día")
    
    tab1, tab2 = st.tabs(["Global", "Por Tienda"])
    
    with tab1:
        venta_por_dia = df_filtrado.groupby('Fecha Vta')['Venta'].sum().sort_index()
        fig_dia_global = px.line(
            venta_por_dia.reset_index(),
            x='Fecha Vta',
            y='Venta',
            title='Venta por Día (Global)',
            markers=True
        )
        fig_dia_global.update_traces(line=dict(width=2), marker=dict(size=6))
        st.plotly_chart(fig_dia_global, use_container_width=True)
        
        # Mostrar tabla
        st.dataframe(
            venta_por_dia.reset_index().style.format({'Venta': '${:,.2f}'}),
            use_container_width=True,
            hide_index=True
        )
    
    with tab2:
        venta_por_dia_tienda = df_filtrado.groupby(['Tienda', 'Fecha Vta'])['Venta'].sum().reset_index()
        fig_dia_tienda = px.line(
            venta_por_dia_tienda,
            x='Fecha Vta',
            y='Venta',
            color='Tienda',
            title='Venta por Día (por Tienda)',
            markers=True
        )
        st.plotly_chart(fig_dia_tienda, use_container_width=True)
    
    st.markdown("---")
    
    # 4. Venta por Hora
    st.header("⏰ 4. Venta por Hora")
    
    def format_hour(hour):
        if hour == 0:
            return '12 AM'
        elif hour < 12:
            return f'{hour} AM'
        elif hour == 12:
            return '12 PM'
        else:
            return f'{hour - 12} PM'
    
    tab3, tab4 = st.tabs(["Global", "Por Tienda"])
    
    with tab3:
        venta_por_hora = df_filtrado.groupby('Hora')['Venta'].sum().sort_index()
        horas_formateadas = [format_hour(h) for h in venta_por_hora.index]
        
        fig_hora = px.bar(
            x=horas_formateadas,
            y=venta_por_hora.values,
            title='Venta por Hora (Global)',
            labels={'x': 'Hora del Día', 'y': 'Venta Total'},
            color=venta_por_hora.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_hora, use_container_width=True)
        
        # Tabla
        hora_df = pd.DataFrame({
            'Hora': horas_formateadas,
            'Venta': venta_por_hora.values
        })
        st.dataframe(
            hora_df.style.format({'Venta': '${:,.2f}'}),
            use_container_width=True,
            hide_index=True
        )
    
    with tab4:
        venta_por_hora_tienda = df_filtrado.groupby(['Tienda', 'Hora'])['Venta'].sum().reset_index()
        venta_por_hora_tienda['Hora_Formato'] = venta_por_hora_tienda['Hora'].map(format_hour)
        
        fig_hora_tienda = px.line(
            venta_por_hora_tienda,
            x='Hora_Formato',
            y='Venta',
            color='Tienda',
            title='Venta por Hora (por Tienda)',
            markers=True
        )
        st.plotly_chart(fig_hora_tienda, use_container_width=True)
    
    st.markdown("---")
    
    # 5. Top 10 Productos Más Vendidos
    st.header("🏆 5. Top 10 Productos Más Vendidos")
    
    tab5, tab6 = st.tabs(["Global", "Por Tienda"])
    
    with tab5:
        top_10_global = df_filtrado.groupby('Producto')['Venta'].sum().nlargest(10)
        
        fig_top10 = px.bar(
            top_10_global.reset_index(),
            x='Venta',
            y='Producto',
            title='Top 10 Productos Más Vendidos (Global)',
            orientation='h',
            color='Venta',
            color_continuous_scale='Viridis',
            text='Venta'
        )
        fig_top10.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
        fig_top10.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_top10, use_container_width=True)
        
        st.dataframe(
            top_10_global.reset_index().style.format({'Venta': '${:,.2f}'}),
            use_container_width=True,
            hide_index=True
        )
    
    with tab6:
        # Selector de tienda para top 10
        tienda_top10 = st.selectbox(
            "Seleccionar Tienda para Top 10",
            ['Todas'] + sorted(df_filtrado['Tienda'].unique().tolist()),
            key='top10_tienda'
        )
        
        if tienda_top10 == 'Todas':
            top_10_tienda = df_filtrado.groupby(['Tienda', 'Producto'])['Venta'].sum().groupby(level=0, group_keys=False).nlargest(10)
            
            for tienda in top_10_tienda.index.get_level_values('Tienda').unique():
                st.subheader(f"Top 10 - {tienda}")
                productos_tienda = top_10_tienda.loc[tienda]
                
                if not productos_tienda.empty:
                    fig = px.bar(
                        productos_tienda.reset_index(),
                        x='Venta',
                        y='Producto',
                        title=f'Top 10 Productos - {tienda}',
                        orientation='h',
                        color='Venta',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            top_10_tienda = df_filtrado[df_filtrado['Tienda'] == tienda_top10].groupby('Producto')['Venta'].sum().nlargest(10)
            
            fig = px.bar(
                top_10_tienda.reset_index(),
                x='Venta',
                y='Producto',
                title=f'Top 10 Productos - {tienda_top10}',
                orientation='h',
                color='Venta',
                color_continuous_scale='Viridis',
                text='Venta'
            )
            fig.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 6. Tabla de Datos Filtrada
    st.header("📋 6. Datos Detallados")
    
    # Mostrar datos filtrados
    st.subheader("Vista de Datos Aplicando Filtros")
    
    # Selector de columnas a mostrar
    columnas_disponibles = df_filtrado.columns.tolist()
    columnas_mostrar = st.multiselect(
        "Seleccionar columnas a mostrar",
        columnas_disponibles,
        default=['Tienda', 'Ticket', 'Producto', 'Venta', 'Fecha Vta', 'Hora', 'Cantidad']
    )
    
    if columnas_mostrar:
        st.dataframe(
            df_filtrado[columnas_mostrar].head(1000),
            use_container_width=True,
            height=400
        )
        
        # Descargar datos filtrados
        @st.cache_data
        def convert_df_to_csv(df_to_convert, columns):
            return df_to_convert[columns].to_csv(index=False).encode('utf-8')
        
        csv = convert_df_to_csv(df_filtrado, columnas_mostrar)
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=csv,
            file_name=f"ventas_filtradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Información del dashboard
    st.sidebar.markdown("---")
    st.sidebar.info(
        f"""
        ### 📊 Información del Dashboard
        
        - **Total de registros:** {len(df_filtrado):,}
        - **Rango de fechas:** {fecha_inicio} a {fecha_fin}
        - **Tiendas incluidas:** {tienda_seleccionada if tienda_seleccionada != 'Todas' else 'Todas'}
        - **Productos incluidos:** {producto_seleccionado if producto_seleccionado != 'Todos' else 'Todos'}
        """
    )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>Dashboard creado con Streamlit | Análisis de Ventas</div>",
        unsafe_allow_html=True
    )

except FileNotFoundError:
    st.error("❌ Error: No se encontró el archivo 'BD_EVALUACION.csv'")
    st.info("Por favor, asegúrate de que el archivo CSV esté en el mismo directorio que este script")
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {str(e)}")
