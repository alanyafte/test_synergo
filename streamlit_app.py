import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide"
)

st.title("Dashboard de Analisis de Ventas")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_csv('BD_EVALUACION.csv', encoding='latin1', low_memory=False)
    
    df['Venta'] = pd.to_numeric(df['Venta'], errors='coerce')
    
    df['Fecha Vta'] = pd.to_datetime(df['Fecha Vta'], format='%d/%m/%Y', errors='coerce')
    
    df['Hora'] = pd.to_datetime(df['Hora Vta'], format='%H:%M:%S', errors='coerce').dt.hour
    
    df = df.dropna(subset=['Venta'])
    
    return df

st.sidebar.header("Filtros")

try:
    df = load_data()
    
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
    
    tiendas = ['Todas'] + sorted(df['Tienda'].unique().tolist())
    tienda_seleccionada = st.sidebar.selectbox("Seleccionar Tienda", tiendas)
    
    productos = ['Todos'] + sorted(df['Producto'].unique().tolist())
    producto_seleccionado = st.sidebar.selectbox("Seleccionar Producto", productos)
    
    st.sidebar.subheader("Rango de Horas")
    hora_min = st.sidebar.slider("Hora minima", 0, 23, 0)
    hora_max = st.sidebar.slider("Hora maxima", 0, 23, 23)
    
    df_filtrado = df.copy()
    
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha Vta'].dt.date >= fecha_inicio) & 
        (df_filtrado['Fecha Vta'].dt.date <= fecha_fin)
    ]
    
    if tienda_seleccionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Tienda'] == tienda_seleccionada]
    
    if producto_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Producto'] == producto_seleccionado]
    
    df_filtrado = df_filtrado[
        (df_filtrado['Hora'] >= hora_min) & 
        (df_filtrado['Hora'] <= hora_max)
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        venta_total = df_filtrado['Venta'].sum()
        st.metric("Venta Total", f"${venta_total:,.2f}")
    
    with col2:
        num_tickets = df_filtrado['Ticket'].nunique()
        st.metric("Tickets Totales", f"{num_tickets:,}")
    
    with col3:
        ticket_promedio = venta_total / num_tickets if num_tickets > 0 else 0
        st.metric("Ticket Promedio", f"${ticket_promedio:.2f}")
    
    with col4:
        num_productos = df_filtrado['Producto'].nunique()
        st.metric("Productos Unicos", f"{num_productos:,}")
    
    st.markdown("---")
    
    # 1. Venta Total (Global y por Tienda)
    st.header("1. Venta Total (Global y por Tienda)")
    
    venta_total_global = df_filtrado['Venta'].sum()
    st.write(f"Venta Total Global: {venta_total_global:,.2f}")
    
    venta_total_por_tienda = df_filtrado.groupby('Tienda')['Venta'].sum()
    st.write("Venta Total por Tienda:")
    st.dataframe(venta_total_por_tienda.reset_index().style.format({'Venta': '${:,.2f}'}), hide_index=True)
    
    fig = px.bar(
        venta_total_por_tienda.reset_index(),
        x='Tienda',
        y='Venta',
        title='Venta Total por Tienda',
        labels={'Tienda': 'Tienda', 'Venta': 'Venta Total'}
    )
    fig.update_xaxes(title_text='Tienda')
    fig.update_yaxes(title_text='Venta Total')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 2. Numero de Tickets (Global y por Tienda)
    st.header("2. Numero de Tickets (Global y por Tienda)")
    
    num_tickets_global = df_filtrado['Ticket'].nunique()
    st.write(f"Numero Total de Tickets: {num_tickets_global}")
    
    num_tickets_por_tienda = df_filtrado.groupby('Tienda')['Ticket'].nunique()
    st.write("Numero de Tickets por Tienda:")
    st.dataframe(num_tickets_por_tienda.reset_index(), hide_index=True)
    
    fig = px.bar(
        num_tickets_por_tienda.reset_index(),
        x='Tienda',
        y='Ticket',
        title='Numero de Tickets por Tienda',
        labels={'Tienda': 'Tienda', 'Ticket': 'Numero de Tickets'}
    )
    fig.update_xaxes(title_text='Tienda')
    fig.update_yaxes(title_text='Numero de Tickets')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 3. Venta por Dia (Global y por Tienda)
    st.header("3. Venta por Dia (Global y por Tienda)")
    
    venta_por_dia_global = df_filtrado.groupby('Fecha Vta')['Venta'].sum().sort_index()
    st.write("Venta por Dia (Global):")
    st.dataframe(venta_por_dia_global.reset_index().style.format({'Venta': '${:,.2f}'}), hide_index=True)
    
    fig_global = px.line(
        venta_por_dia_global.reset_index(),
        x='Fecha Vta',
        y='Venta',
        title='Venta por Dia (Global)'
    )
    fig_global.update_xaxes(title_text='Fecha')
    fig_global.update_yaxes(title_text='Venta Total')
    st.plotly_chart(fig_global, use_container_width=True)
    
    venta_por_dia_por_tienda = df_filtrado.groupby(['Tienda', 'Fecha Vta'])['Venta'].sum().reset_index()
    st.write("Venta por Dia (por Tienda):")
    
    fig_tienda = px.line(
        venta_por_dia_por_tienda,
        x='Fecha Vta',
        y='Venta',
        color='Tienda',
        title='Venta por Dia (por Tienda)'
    )
    fig_tienda.update_xaxes(title_text='Fecha')
    fig_tienda.update_yaxes(title_text='Venta Total')
    st.plotly_chart(fig_tienda, use_container_width=True)
    
    st.markdown("---")
    
   # 4. Venta por Hora (Global y por Tienda)
    st.header("4. Venta por Hora (Global y por Tienda)")
    
    def format_hour(hour):
        if hour == 0:
            return '12 AM'
        elif hour < 12:
            return f'{hour} AM'
        elif hour == 12:
            return '12 PM'
        else:
            return f'{hour - 12} PM'
    
    venta_por_hora_global = df_filtrado.groupby('Hora')['Venta'].sum().sort_index()
    st.write("Venta por Hora (Global):")
    st.dataframe(venta_por_hora_global.reset_index().style.format({'Venta': '${:,.2f}'}), hide_index=True)
    
    formatted_hours_global = venta_por_hora_global.index.map(format_hour)
    fig_hora_global = px.bar(
        x=formatted_hours_global,
        y=venta_por_hora_global.values,
        title='Venta por Hora (Global)',
        labels={'x': 'Hora del Dia', 'y': 'Venta Total'}
    )
    fig_hora_global.update_xaxes(title_text='Hora del Dia')
    fig_hora_global.update_yaxes(title_text='Venta Total')
    st.plotly_chart(fig_hora_global, use_container_width=True)
    
    venta_por_hora_por_tienda = df_filtrado.groupby(['Tienda', 'Hora'])['Venta'].sum().reset_index()
    venta_por_hora_por_tienda['Hora Formato'] = venta_por_hora_por_tienda['Hora'].map(format_hour)
    st.write("Venta por Hora (por Tienda) - Grafico de Lineas:")
    
    fig_hora_tienda = px.line(
        venta_por_hora_por_tienda,
        x='Hora Formato',
        y='Venta',
        color='Tienda',
        title='Venta por Hora (por Tienda)'
    )
    fig_hora_tienda.update_xaxes(title_text='Hora del Dia')
    fig_hora_tienda.update_yaxes(title_text='Venta Total')
    st.plotly_chart(fig_hora_tienda, use_container_width=True)
    
    # Diagrama de calor (Heatmap) para Venta por Hora por Tienda
    st.write("Venta por Hora (por Tienda) - Diagrama de Calor:")
    
    # Preparar datos para el heatmap
    venta_por_hora_heatmap = df_filtrado.groupby(['Tienda', 'Hora'])['Venta'].sum().unstack(level=0)
    
    # Obtener las horas formateadas para el eje X
    horas_heatmap = venta_por_hora_heatmap.index.map(format_hour)
    
    # Crear el heatmap
    fig_heatmap = px.imshow(
        venta_por_hora_heatmap.T,  # Transponer para que las tiendas estén en el eje Y y las horas en el eje X
        x=horas_heatmap,
        y=venta_por_hora_heatmap.columns,
        title='Venta por Hora (por Tienda) - Diagrama de Calor',
        labels=dict(x='Hora del Dia', y='Tienda', color='Venta Total'),
        color_continuous_scale='Viridis',
        aspect='auto'
    )
    
    fig_heatmap.update_xaxes(title_text='Hora del Dia')
    fig_heatmap.update_yaxes(title_text='Tienda')
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Mostrar la tabla de datos del heatmap
    st.write("Tabla de Venta por Hora (por Tienda):")
    venta_por_hora_tabla = venta_por_hora_heatmap.copy()
    venta_por_hora_tabla.index = horas_heatmap
    st.dataframe(venta_por_hora_tabla.style.format('${:,.2f}'), use_container_width=True)
    
    # 5. Venta por Producto (Global y por Tienda)
    st.header("5. Venta por Producto (Global y por Tienda)")
    
    venta_por_producto_global = df_filtrado.groupby('Producto')['Venta'].sum().sort_values(ascending=False)
    st.write("Venta por Producto (Global):")
    st.dataframe(venta_por_producto_global.reset_index().head(20).style.format({'Venta': '${:,.2f}'}), hide_index=True)
    
    top_10_global_products = venta_por_producto_global.nlargest(10)
    
    fig_global_top10_products = px.bar(
        top_10_global_products.reset_index(),
        x='Producto',
        y='Venta',
        title='Top 10 Productos Mas Vendidos (Global)',
        labels={'Producto': 'Producto', 'Venta': 'Venta Total'}
    )
    fig_global_top10_products.update_xaxes(title_text='Producto')
    fig_global_top10_products.update_yaxes(title_text='Venta Total')
    st.plotly_chart(fig_global_top10_products, use_container_width=True)
    
    if not top_10_global_products.empty:
        df_top10_global_filtered = df_filtrado[df_filtrado['Producto'].isin(top_10_global_products.index)]
        
        venta_top10_por_producto_y_tienda = df_top10_global_filtered.groupby(['Producto', 'Tienda'])['Venta'].sum().reset_index()
        
        total_sales_per_product = df_top10_global_filtered.groupby('Producto')['Venta'].sum().rename('Total Venta Producto').reset_index()
        
        venta_top10_por_producto_y_tienda = pd.merge(venta_top10_por_producto_y_tienda, total_sales_per_product, on='Producto')
        
        venta_top10_por_producto_y_tienda['Porcentaje Venta Tienda'] = (venta_top10_por_producto_y_tienda['Venta'] / venta_top10_por_producto_y_tienda['Total Venta Producto']) * 100
        
        fig_stacked_bar = px.bar(
            venta_top10_por_producto_y_tienda,
            x='Producto',
            y='Venta',
            color='Tienda',
            title='Venta de los Top 10 Productos Globales por Tienda',
            labels={'Producto': 'Producto', 'Venta': 'Venta Total', 'Tienda': 'Tienda'}
        )
        
        fig_stacked_bar.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_stacked_bar, use_container_width=True)
    
    st.markdown("---")
    
    # 6. Top 10 Productos Mas Vendidos (Global y por Tienda)
    st.header("6. Top 10 Productos Mas Vendidos (Global y por Tienda)")
    
    top_10_global = df_filtrado.groupby('Producto')['Venta'].sum().nlargest(10)
    st.write("Top 10 Productos Mas Vendidos (Global):")
    st.dataframe(top_10_global.reset_index().style.format({'Venta': '${:,.2f}'}), hide_index=True)
    
    fig_global_top10 = px.bar(
        top_10_global.reset_index(),
        x='Producto',
        y='Venta',
        title='Top 10 Productos Mas Vendidos (Global)',
        labels={'Producto': 'Producto', 'Venta': 'Venta Total'}
    )
    fig_global_top10.update_xaxes(title_text='Producto')
    fig_global_top10.update_yaxes(title_text='Venta Total')
    st.plotly_chart(fig_global_top10, use_container_width=True)
    
    top_10_por_tienda = df_filtrado.groupby(['Tienda', 'Producto'])['Venta'].sum().groupby(level=0, group_keys=False).nlargest(10)
    st.write("Top 10 Productos Mas Vendidos (por Tienda):")
    st.dataframe(top_10_por_tienda.reset_index().style.format({'Venta': '${:,.2f}'}), hide_index=True)
    
    for tienda in top_10_por_tienda.index.get_level_values('Tienda').unique():
        productos_tienda = top_10_por_tienda.loc[tienda]
        
        if not productos_tienda.empty:
            productos_tienda_df = productos_tienda.reset_index()
            fig_tienda_top10 = px.bar(
                productos_tienda_df,
                x='Producto',
                y='Venta',
                title=f'Top 10 Productos Mas Vendidos en {tienda}',
                labels={'Producto': 'Producto', 'Venta': 'Venta Total'}
            )
            fig_tienda_top10.update_xaxes(title_text='Producto')
            fig_tienda_top10.update_yaxes(title_text='Venta Total')
            st.plotly_chart(fig_tienda_top10, use_container_width=True)
    
    st.markdown("---")
    
    # 7. Datos Detallados
    st.header("7. Datos Detallados")
    
    st.subheader("Vista de Datos Aplicando Filtros")
    
    columnas_mostrar = st.multiselect(
        "Seleccionar columnas a mostrar",
        df_filtrado.columns.tolist(),
        default=['Tienda', 'Ticket', 'Producto', 'Venta', 'Fecha Vta', 'Hora', 'Cantidad']
    )
    
    if columnas_mostrar:
        st.dataframe(df_filtrado[columnas_mostrar].head(1000), use_container_width=True, height=400)
        
        @st.cache_data
        def convert_df_to_csv(df_to_convert, columns):
            return df_to_convert[columns].to_csv(index=False).encode('utf-8')
        
        csv = convert_df_to_csv(df_filtrado, columnas_mostrar)
        st.download_button(
            label="Descargar datos filtrados (CSV)",
            data=csv,
            file_name=f"ventas_filtradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        f"""
        Informacion del Dashboard
        
        Total de registros: {len(df_filtrado):,}
        Rango de fechas: {fecha_inicio} a {fecha_fin}
        Tiendas incluidas: {tienda_seleccionada if tienda_seleccionada != 'Todas' else 'Todas'}
        Productos incluidos: {producto_seleccionado if producto_seleccionado != 'Todos' else 'Todos'}
        """
    )
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>Dashboard creado con Streamlit | Analisis de Ventas</div>",
        unsafe_allow_html=True
    )

except FileNotFoundError:
    st.error("Error: No se encontro el archivo 'BD_EVALUACION.csv'")
    st.info("Por favor, asegurate de que el archivo CSV este en el mismo directorio que este script")
except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
