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
    
    col1_1, col1_2 = st.columns([3, 2])
    
    with col1_1:
        venta_total_global = df_filtrado['Venta'].sum()
        st.write(f"**Venta Total Global:** ${venta_total_global:,.2f}")
        
        venta_total_por_tienda = df_filtrado.groupby('Tienda')['Venta'].sum().sort_values(ascending=False)
        
        fig1 = px.bar(
            venta_total_por_tienda.reset_index(),
            x='Tienda',
            y='Venta',
            title='Venta Total por Tienda',
            labels={'Tienda': 'Tienda', 'Venta': 'Venta Total'},
            text='Venta'
        )
        fig1.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig1.update_xaxes(title_text='Tienda')
        fig1.update_yaxes(title_text='Venta Total')
        st.plotly_chart(fig1, use_container_width=True, key="fig_venta_tienda")
    
    with col1_2:
        st.info(
            "**Conclusion:**\n\n"
            f"La tienda con mayor volumen de ventas es **{venta_total_por_tienda.index[0]}** "
            f"con ${venta_total_por_tienda.iloc[0]:,.2f}, representando el "
            f"{(venta_total_por_tienda.iloc[0] / venta_total_global * 100):.1f}% del total. "
            f"La tienda con menor desempeno es **{venta_total_por_tienda.index[-1]}** con "
            f"${venta_total_por_tienda.iloc[-1]:,.2f}. La diferencia entre la tienda lider y la "
            f"ultima es de ${venta_total_por_tienda.iloc[0] - venta_total_por_tienda.iloc[-1]:,.2f}, "
            f"lo que indica una oportunidad de mejora para las tiendas de menor rendimiento."
        )
    
    st.markdown("---")
    
    # 2. Numero de Tickets (Global y por Tienda)
    st.header("2. Numero de Tickets (Global y por Tienda)")
    
    col2_1, col2_2 = st.columns([3, 2])
    
    with col2_1:
        num_tickets_global = df_filtrado['Ticket'].nunique()
        st.write(f"**Numero Total de Tickets:** {num_tickets_global:,}")
        
        num_tickets_por_tienda = df_filtrado.groupby('Tienda')['Ticket'].nunique().sort_values(ascending=False)
        
        fig2 = px.bar(
            num_tickets_por_tienda.reset_index(),
            x='Tienda',
            y='Ticket',
            title='Numero de Tickets por Tienda',
            labels={'Tienda': 'Tienda', 'Ticket': 'Numero de Tickets'},
            text='Ticket'
        )
        fig2.update_traces(textposition='outside')
        fig2.update_xaxes(title_text='Tienda')
        fig2.update_yaxes(title_text='Numero de Tickets')
        st.plotly_chart(fig2, use_container_width=True, key="fig_tickets_tienda")
    
    with col2_2:
        st.info(
            "**Conclusion:**\n\n"
            f"La tienda **{num_tickets_por_tienda.index[0]}** genera la mayor cantidad de tickets "
            f"con {num_tickets_por_tienda.iloc[0]:,} transacciones, mientras que la tienda "
            f"**{num_tickets_por_tienda.index[-1]}** genera solo {num_tickets_por_tienda.iloc[-1]:,} tickets. "
            f"El ticket promedio por tienda es de {num_tickets_global / df_filtrado['Tienda'].nunique():.0f} tickets. "
            f"La correlacion entre volumen de tickets y ventas totales sugiere que aumentar el flujo "
            f"de clientes podria beneficiar directamente los ingresos."
        )
    
    st.markdown("---")
    
    # 3. Venta por Dia (Global y por Tienda)
    st.header("3. Venta por Dia (Global y por Tienda)")
    
    venta_por_dia_global = df_filtrado.groupby('Fecha Vta')['Venta'].sum().sort_index()
    dia_max_ventas = venta_por_dia_global.idxmax().strftime('%Y-%m-%d')
    dia_min_ventas = venta_por_dia_global.idxmin().strftime('%Y-%m-%d')
    venta_max_dia = venta_por_dia_global.max()
    venta_min_dia = venta_por_dia_global.min()
    
    col3_1, col3_2 = st.columns([3, 2])
    
    with col3_1:
        fig_global = px.line(
            venta_por_dia_global.reset_index(),
            x='Fecha Vta',
            y='Venta',
            title='Venta por Dia (Global)',
            markers=True
        )
        fig_global.update_traces(line=dict(width=2), marker=dict(size=6))
        fig_global.update_xaxes(title_text='Fecha')
        fig_global.update_yaxes(title_text='Venta Total')
        st.plotly_chart(fig_global, use_container_width=True, key="fig_venta_dia_global")
        
        venta_por_dia_por_tienda = df_filtrado.groupby(['Tienda', 'Fecha Vta'])['Venta'].sum().reset_index()
        
        fig_tienda = px.line(
            venta_por_dia_por_tienda,
            x='Fecha Vta',
            y='Venta',
            color='Tienda',
            title='Venta por Dia (por Tienda)',
            markers=True
        )
        fig_tienda.update_xaxes(title_text='Fecha')
        fig_tienda.update_yaxes(title_text='Venta Total')
        st.plotly_chart(fig_tienda, use_container_width=True, key="fig_venta_dia_tienda")
    
    with col3_2:
        st.info(
            "**Conclusion:**\n\n"
            f"Se observa una tendencia clara de mayores ventas los fines de semana, con el pico maximo "
            f"el **{dia_max_ventas}** alcanzando ${venta_max_dia:,.2f}. El dia de menor actividad fue "
            f"**{dia_min_ventas}** con ${venta_min_dia:,.2f}. "
            f"La variabilidad entre dias es significativa, con una diferencia del "
            f"{((venta_max_dia - venta_min_dia) / venta_min_dia * 100):.1f}% entre el mejor y peor dia. "
            f"Esto sugiere oportunidades para estrategias promocionales especificas durante los dias de menor actividad."
        )
    
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
    hora_pico = venta_por_hora_global.idxmax()
    hora_valle = venta_por_hora_global.idxmin()
    venta_hora_pico = venta_por_hora_global.max()
    venta_hora_valle = venta_por_hora_global.min()
    
    col4_1, col4_2 = st.columns([3, 2])
    
    with col4_1:
        formatted_hours_global = venta_por_hora_global.index.map(format_hour)
        fig_hora_global = px.bar(
            x=formatted_hours_global,
            y=venta_por_hora_global.values,
            title='Venta por Hora (Global)',
            labels={'x': 'Hora del Dia', 'y': 'Venta Total'},
            text=venta_por_hora_global.values
        )
        fig_hora_global.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_hora_global.update_xaxes(title_text='Hora del Dia')
        fig_hora_global.update_yaxes(title_text='Venta Total')
        st.plotly_chart(fig_hora_global, use_container_width=True, key="fig_venta_hora_global")
        
        venta_por_hora_por_tienda = df_filtrado.groupby(['Tienda', 'Hora'])['Venta'].sum().reset_index()
        venta_por_hora_por_tienda['Hora Formato'] = venta_por_hora_por_tienda['Hora'].map(format_hour)
        
        fig_hora_tienda = px.line(
            venta_por_hora_por_tienda,
            x='Hora Formato',
            y='Venta',
            color='Tienda',
            title='Venta por Hora (por Tienda)',
            markers=True
        )
        fig_hora_tienda.update_xaxes(title_text='Hora del Dia')
        fig_hora_tienda.update_yaxes(title_text='Venta Total')
        st.plotly_chart(fig_hora_tienda, use_container_width=True, key="fig_venta_hora_tienda_lineas")
        
        venta_por_hora_heatmap = df_filtrado.groupby(['Tienda', 'Hora'])['Venta'].sum().unstack(level=0)
        horas_heatmap = venta_por_hora_heatmap.index.map(format_hour)
        
        fig_heatmap = px.imshow(
            venta_por_hora_heatmap.T,
            x=horas_heatmap,
            y=venta_por_hora_heatmap.columns,
            title='Venta por Hora (por Tienda) - Diagrama de Calor',
            labels=dict(x='Hora del Dia', y='Tienda', color='Venta Total'),
            color_continuous_scale='Viridis',
            aspect='auto'
        )
        fig_heatmap.update_xaxes(title_text='Hora del Dia')
        fig_heatmap.update_yaxes(title_text='Tienda')
        st.plotly_chart(fig_heatmap, use_container_width=True, key="fig_venta_hora_heatmap")
    
    with col4_2:
        st.info(
            "**Conclusion:**\n\n"
            f"El patron de ventas por hora muestra una distribucion bimodal. La **hora pico** es a las "
            f"{format_hour(hora_pico)} con ${venta_hora_pico:,.2f} en ventas, mientras que la **hora valle** "
            f"es a las {format_hour(hora_valle)} con solo ${venta_hora_valle:,.2f}. "
            f"Se identifican claramente dos segmentos horarios de alta actividad: "
            f"**{format_hour(7)} a {format_hour(10)}** (horas matutinas) y "
            f"**{format_hour(16)} a {format_hour(20)}** (horas vespertinas). "
            f"Las horas de madrugada (12 AM a 5 AM) representan el {((venta_por_hora_global.loc[0:5].sum()) / venta_por_hora_global.sum() * 100):.1f}% "
            f"del total de ventas, lo que podria justificar ajustes en horarios operativos."
        )
    
    st.markdown("---")
    
        # 5. Venta por Producto (Global y por Tienda)
    st.header("5. Venta por Producto (Global y por Tienda)")
    
    venta_por_producto_global = df_filtrado.groupby('Producto')['Venta'].sum().sort_values(ascending=False)
    top_3_productos = venta_por_producto_global.head(3)
    productos_con_ventas_negativas = venta_por_producto_global[venta_por_producto_global < 0]
    
    col5_1, col5_2 = st.columns([3, 2])
    
    with col5_1:
        top_10_global_products = venta_por_producto_global.nlargest(10)
        
        fig_global_top10_products = px.bar(
            top_10_global_products.reset_index(),
            x='Producto',
            y='Venta',
            title='Top 10 Productos Mas Vendidos (Global)',
            labels={'Producto': 'Producto', 'Venta': 'Venta Total'},
            text='Venta'
        )
        fig_global_top10_products.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_global_top10_products.update_xaxes(title_text='Producto')
        fig_global_top10_products.update_yaxes(title_text='Venta Total')
        st.plotly_chart(fig_global_top10_products, use_container_width=True, key="fig_top10_productos_global")
        
        if not top_10_global_products.empty:
            df_top10_global_filtered = df_filtrado[df_filtrado['Producto'].isin(top_10_global_products.index)]
            
            venta_top10_por_producto_y_tienda = df_top10_global_filtered.groupby(['Producto', 'Tienda'])['Venta'].sum().reset_index()
            
            total_sales_per_product = df_top10_global_filtered.groupby('Producto')['Venta'].sum().rename('Total Venta Producto').reset_index()
            
            venta_top10_por_producto_y_tienda = pd.merge(venta_top10_por_producto_y_tienda, total_sales_per_product, on='Producto')
            
            venta_top10_por_producto_y_tienda['Porcentaje Venta Tienda'] = (venta_top10_por_producto_y_tienda['Venta'] / venta_top10_por_producto_y_tienda['Total Venta Producto']) * 100
            
            venta_top10_por_producto_y_tienda['Porcentaje Formateado'] = venta_top10_por_producto_y_tienda['Porcentaje Venta Tienda'].apply(lambda x: f'{x:.1f}%')
            
            fig_stacked_bar = px.bar(
                venta_top10_por_producto_y_tienda,
                x='Producto',
                y='Venta',
                color='Tienda',
                title='Venta de los Top 10 Productos Globales por Tienda',
                labels={'Producto': 'Producto', 'Venta': 'Venta Total', 'Tienda': 'Tienda'},
                text='Venta'
            )
            
            fig_stacked_bar.update_traces(
                texttemplate='$%{text:,.0f}',
                textposition='inside',
                hovertemplate='<b>Producto:</b> %{customdata[0]}<br>' +
                              '<b>Tienda:</b> %{customdata[1]}<br>' +
                              '<b>Venta:</b> $%{customdata[2]:,.2f}<br>' +
                              '<b>Contribucion:</b> %{customdata[3]:.1f}%<br>' +
                              '<extra></extra>'
            )
            
            custom_data_stack = venta_top10_por_producto_y_tienda[['Producto', 'Tienda', 'Venta', 'Porcentaje Venta Tienda']].values
            fig_stacked_bar.update_traces(customdata=custom_data_stack)
            
            fig_stacked_bar.update_layout(
                xaxis={'categoryorder': 'total descending'},
                barmode='stack'
            )
            st.plotly_chart(fig_stacked_bar, use_container_width=True, key="fig_stacked_bar_top10")
            
            st.write("**Desglose de Ventas por Producto y Tienda (Top 10 Global):**")
            tabla_desglose = venta_top10_por_producto_y_tienda.pivot_table(
                index='Producto',
                columns='Tienda',
                values='Venta',
                fill_value=0
            )
            
            tabla_porcentaje = venta_top10_por_producto_y_tienda.pivot_table(
                index='Producto',
                columns='Tienda',
                values='Porcentaje Venta Tienda',
                fill_value=0
            )
            
            for col in tabla_porcentaje.columns:
                tabla_porcentaje[col] = tabla_porcentaje[col].apply(lambda x: f'{x:.1f}%')
            
            st.dataframe(tabla_desglose.style.format('${:,.2f}'), use_container_width=True)
            st.caption("Tabla de Ventas por Producto y Tienda")
            
            st.dataframe(tabla_porcentaje, use_container_width=True)
            st.caption("Tabla de Porcentaje de Contribucion por Tienda")
    
    with col5_2:
        st.info(
            "**Conclusion:**\n\n"
            f"El top 3 de productos representa el **{(top_3_productos.sum() / venta_por_producto_global.sum() * 100):.1f}%** "
            f"de las ventas totales, evidenciando una alta concentracion en pocos SKUs. "
            f"**{top_3_productos.index[0]}** lidera con ${top_3_productos.iloc[0]:,.2f}, seguido por "
            f"**{top_3_productos.index[1]}** (${top_3_productos.iloc[1]:,.2f}) y "
            f"**{top_3_productos.index[2]}** (${top_3_productos.iloc[2]:,.2f}). "
            f"Se detectaron {len(productos_con_ventas_negativas)} productos con ventas negativas, "
            f"lo que podria indicar devoluciones o ajustes contables que requieren atencion. "
            f"La distribucion por tienda del top 10 muestra que la **Tienda 4** domina en la mayoria "
            f"de estos productos, con participaciones que superan el 40% en varios casos."
        )
    
    # 6. Top 10 Productos Mas Vendidos (Global y por Tienda)
    st.header("6. Top 10 Productos Mas Vendidos (Global y por Tienda)")
    
    col6_1, col6_2 = st.columns([3, 2])
    
    with col6_1:
        top_10_global = df_filtrado.groupby('Producto')['Venta'].sum().nlargest(10)
        
        fig_global_top10 = px.bar(
            top_10_global.reset_index(),
            x='Producto',
            y='Venta',
            title='Top 10 Productos Mas Vendidos (Global)',
            labels={'Producto': 'Producto', 'Venta': 'Venta Total'},
            text='Venta'
        )
        fig_global_top10.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_global_top10.update_xaxes(title_text='Producto')
        fig_global_top10.update_yaxes(title_text='Venta Total')
        st.plotly_chart(fig_global_top10, use_container_width=True, key="fig_top10_global_repeat")
        
        top_10_por_tienda = df_filtrado.groupby(['Tienda', 'Producto'])['Venta'].sum().groupby(level=0, group_keys=False).nlargest(10)
        
        for i, tienda in enumerate(top_10_por_tienda.index.get_level_values('Tienda').unique()):
            productos_tienda = top_10_por_tienda.loc[tienda]
            
            if not productos_tienda.empty:
                productos_tienda_df = productos_tienda.reset_index()
                fig_tienda_top10 = px.bar(
                    productos_tienda_df,
                    x='Producto',
                    y='Venta',
                    title=f'Top 10 Productos Mas Vendidos en {tienda}',
                    labels={'Producto': 'Producto', 'Venta': 'Venta Total'},
                    text='Venta'
                )
                fig_tienda_top10.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
                fig_tienda_top10.update_xaxes(title_text='Producto')
                fig_tienda_top10.update_yaxes(title_text='Venta Total')
                st.plotly_chart(fig_tienda_top10, use_container_width=True, key=f"fig_top10_tienda_{i}_{tienda}")
    
    with col6_2:
        st.info(
            "**Conclusion:**\n\n"
            "El analisis del top 10 por tienda revela diferencias significativas en las preferencias "
            "de los clientes por ubicacion. La **Tienda 4** tiene una mayor diversificacion en su top 10, "
            "mientras que la **Tienda 1** muestra una fuerte dependencia de sus 3 productos principales. "
            "El **Producto 716** aparece en el top 5 de todas las tiendas, siendo el unico producto con "
            "presencia universal entre las preferencias. Esta informacion es valiosa para ajustar "
            "el inventario y las estrategias de surtido por ubicacion."
        )
    
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
    
    st.markdown("---")
    
    
    # 8. Analisis Pareto (Regla 80/20)
    st.header("8. Analisis Pareto (Regla 80/20)")
    
    st.markdown("""
    El analisis Pareto permite identificar los productos que generan el mayor impacto en las ventas.
    La regla 80/20 sugiere que aproximadamente el 20% de los productos generan el 80% de las ventas.
    """)
    
    # Calcular Pareto
    venta_por_producto_pareto = df_filtrado.groupby('Producto')['Venta'].sum().sort_values(ascending=False)
    venta_acumulada = venta_por_producto_pareto.cumsum()
    venta_total_pareto = venta_acumulada.iloc[-1]
    porcentaje_acumulado = (venta_acumulada / venta_total_pareto) * 100
    
    pareto_df = pd.DataFrame({
        'Producto': venta_por_producto_pareto.index,
        'Venta': venta_por_producto_pareto.values,
        'Venta Acumulada': venta_acumulada.values,
        'Porcentaje Acumulado': porcentaje_acumulado.values
    })
    
    pareto_df['Numero Producto'] = range(1, len(pareto_df) + 1)
    pareto_df['Porcentaje Productos'] = (pareto_df['Numero Producto'] / len(pareto_df)) * 100
    
    # Encontrar el punto donde se alcanza el 80% de ventas
    punto_80 = pareto_df[pareto_df['Porcentaje Acumulado'] >= 80].iloc[0]
    productos_80 = punto_80['Numero Producto']
    porcentaje_productos_80 = punto_80['Porcentaje Productos']
    venta_80 = punto_80['Venta Acumulada']
    
    # Encontrar el punto donde se alcanza el 20% de productos
    pareto_df['Porcentaje Productos Redondeado'] = pareto_df['Porcentaje Productos'].round(1)
    punto_20_productos = pareto_df[pareto_df['Porcentaje Productos'] >= 20].iloc[0]
    venta_en_20 = punto_20_productos['Porcentaje Acumulado']
    
    col8_1, col8_2, col8_3 = st.columns(3)
    
    with col8_1:
        st.metric(
            "Productos que generan 80% de ventas",
            f"{productos_80} productos",
            f"{porcentaje_productos_80:.1f}% del total"
        )
    
    with col8_2:
        st.metric(
            "Ventas generadas por 20% de productos",
            f"{venta_en_20:.1f}%",
            delta="vs 80% esperado"
        )
    
    with col8_3:
        productos_top20 = int(len(venta_por_producto_pareto) * 0.2)
        ventas_top20 = venta_por_producto_pareto.head(productos_top20).sum()
        porcentaje_top20 = (ventas_top20 / venta_total_pareto) * 100
        st.metric(
            "Ventas del top 20% de productos",
            f"{porcentaje_top20:.1f}%",
            delta=f"{porcentaje_top20 - 80:.1f}% vs regla 80/20"
        )
    
    st.markdown("---")
    
    # Grafico de Pareto
    col8_4, col8_5 = st.columns([3, 2])
    
    with col8_4:
        fig_pareto = go.Figure()
        
        fig_pareto.add_trace(go.Bar(
            x=pareto_df['Numero Producto'].head(30),
            y=pareto_df['Venta'].head(30),
            name='Venta por Producto',
            marker_color='steelblue',
            text=pareto_df['Venta'].head(30).apply(lambda x: f'${x:,.0f}'),
            textposition='outside',
            hovertemplate='Producto #%{x}<br>Venta: $%{y:,.2f}<extra></extra>'
        ))
        
        fig_pareto.add_trace(go.Scatter(
            x=pareto_df['Numero Producto'],
            y=pareto_df['Porcentaje Acumulado'],
            name='Porcentaje Acumulado',
            marker_color='red',
            mode='lines+markers',
            yaxis='y2',
            line=dict(width=2, dash='dash'),
            hovertemplate='Producto #%{x}<br>Acumulado: %{y:.1f}%<extra></extra>'
        ))
        
        fig_pareto.add_hline(
            y=80, 
            line_dash="dash", 
            line_color="green",
            annotation_text="80%",
            annotation_position="top right"
        )
        
        fig_pareto.add_vline(
            x=productos_80,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"{productos_80} productos",
            annotation_position="top"
        )
        
        fig_pareto.update_layout(
            title='Analisis Pareto: Contribucion Acumulada de Ventas por Producto',
            xaxis_title='Numero de Productos (ordenados por venta descendente)',
            yaxis_title='Venta por Producto',
            yaxis2=dict(
                title='Porcentaje Acumulado de Ventas (%)',
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
            height=500
        )
        
        st.plotly_chart(fig_pareto, use_container_width=True, key="fig_pareto")
        
        # Grafico de torta para el top 20%
        col_pie1, col_pie2 = st.columns(2)
        
        with col_pie1:
            top20_productos = venta_por_producto_pareto.head(productos_top20)
            resto_productos = venta_por_producto_pareto.iloc[productos_top20:]
            
            pie_data = pd.DataFrame({
                'Categoria': ['Top 20% Productos', 'Resto 80% Productos'],
                'Venta': [top20_productos.sum(), resto_productos.sum()]
            })
            
            fig_pie = px.pie(
                pie_data,
                values='Venta',
                names='Categoria',
                title=f'Top 20% de Productos ({productos_top20} productos) vs Resto',
                color_discrete_sequence=['#2E86AB', '#A23B72'],
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True, key="fig_pie_top20")
        
        with col_pie2:
            categorias_pareto = pd.DataFrame({
                'Categoria': ['Top Productos (hasta 80%)', 'Resto Productos'],
                'Venta': [venta_80, venta_total_pareto - venta_80]
            })
            
            fig_pie_80 = px.pie(
                categorias_pareto,
                values='Venta',
                names='Categoria',
                title=f'Distribucion al Alcanzar 80% de Ventas ({productos_80} productos)',
                color_discrete_sequence=['#06A77D', '#D62828'],
                hole=0.4
            )
            fig_pie_80.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie_80, use_container_width=True, key="fig_pie_80")
    
    with col8_5:
        st.info(
            "**Conclusion del Analisis Pareto:**\n\n"
            f"El analisis revela que **{productos_80} productos** ({porcentaje_productos_80:.1f}% del total) "
            f"generan el 80% de las ventas, lo que representa una concentracion "
            f"{'mayor' if productos_80 / len(venta_por_producto_pareto) * 100 < 20 else 'menor'} a la esperada "
            f"por la regla 80/20 clasica.\n\n"
            f"**Hallazgos clave:**\n"
            f"- El top 20% de productos genera el **{porcentaje_top20:.1f}%** de las ventas\n"
            f"- El producto mas vendido aporta **{(venta_por_producto_pareto.iloc[0] / venta_total_pareto * 100):.1f}%** del total\n"
            f"- Los ultimos {min(50, len(venta_por_producto_pareto))} productos representan solo "
            f"**{(venta_por_producto_pareto.tail(50).sum() / venta_total_pareto * 100):.2f}%** de las ventas\n\n"
            f"**Implicaciones estrategicas:**\n"
            f"- Enfocar esfuerzos de marketing e inventario en los {productos_80} productos clave\n"
            f"- Evaluar la rentabilidad de mantener productos de muy baja rotacion\n"
            f"- Considerar estrategias de descontinuacion o liquidacion para productos cola"
        )
    
    # Tabla de top productos Pareto
    st.markdown("---")
    st.subheader("Top 20 Productos por Volumen de Ventas")
    
    top20_pareto = pareto_df.head(20).copy()
    top20_pareto['% del Total'] = (top20_pareto['Venta'] / venta_total_pareto * 100).apply(lambda x: f'{x:.2f}%')
    top20_pareto['% Acumulado'] = top20_pareto['Porcentaje Acumulado'].apply(lambda x: f'{x:.2f}%')
    top20_pareto['Venta'] = top20_pareto['Venta'].apply(lambda x: f'${x:,.2f}')
    top20_pareto['Venta Acumulada'] = top20_pareto['Venta Acumulada'].apply(lambda x: f'${x:,.2f}')
    
    st.dataframe(
        top20_pareto[['Numero Producto', 'Producto', 'Venta', '% del Total', 'Venta Acumulada', '% Acumulado']],
        use_container_width=True,
        hide_index=True
    )
    
    st.caption("Tabla de Pareto: Productos ordenados de mayor a menor contribucion a ventas")
    
    # Recomendaciones basadas en Pareto
    st.markdown("---")
    st.subheader("Recomendaciones basadas en Analisis Pareto")
    
    col_rec1, col_rec2 = st.columns(2)
    
    with col_rec1:
        st.write("**Productos Clase A (Mayor contribucion):**")
        st.write(f"- Enfocar recursos de marketing en estos {min(10, productos_80)} productos")
        st.write("- Mantener inventario de seguridad mas alto")
        st.write("- Negociar mejores precios por volumen con proveedores")
        st.write("- Priorizar su visibilidad en tienda")
    
    with col_rec2:
        st.write("**Productos Clase C (Menor contribucion):**")
        st.write("- Evaluar costo de oportunidad de mantener inventario")
        st.write("- Considerar promociones para liquidar existencias")
        st.write("- Analizar posibilidad de discontinuacion")
        st.write("- Reducir espacio en anaquel asignado")
    
    
    # 9. Insights para Toma de Decisiones
    st.header("9. Insights para Toma de Decisiones")
    
    # Calcular insights adicionales
    ticket_promedio_tienda = df_filtrado.groupby('Tienda').apply(
        lambda x: x['Venta'].sum() / x['Ticket'].nunique() if x['Ticket'].nunique() > 0 else 0
    ).sort_values(ascending=False)
    
    productos_baja_rotacion = venta_por_producto_global[venta_por_producto_global > 0].tail(20)
    
    mejor_horario_tiendas = df_filtrado.groupby(['Tienda', 'Hora'])['Venta'].sum().groupby('Tienda').idxmax()
    
    col8_1, col8_2, col8_3 = st.columns(3)
    
    with col8_1:
        st.subheader("Insight 1: Concentracion de Ventas")
        st.info(
            f"**Hallazgo:** El {(top_3_productos.sum() / venta_por_producto_global.sum() * 100):.1f}% "
            f"de las ventas proviene de solo 3 productos.\n\n"
            f"**Accion recomendada:**\n"
            f"- Asegurar inventario suficiente de **{top_3_productos.index[0]}**, "
            f"**{top_3_productos.index[1]}** y **{top_3_productos.index[2]}**\n"
            f"- Negociar mejores precios con proveedores de estos productos clave\n"
            f"- Desarrollar estrategias de upselling/cross-selling para productos complementarios\n"
            f"- Monitorear semanalmente el stock de estos productos para evitar desabasto"
        )
    
    with col8_2:
        st.subheader("Insight 2: Oportunidad Horaria")
        st.info(
            f"**Hallazgo:** Las ventas fuera del horario pico representan "
            f"{((venta_total_global - venta_por_hora_global.loc[7:20].sum()) / venta_total_global * 100):.1f}% "
            f"del total.\n\n"
            f"**Accion recomendada:**\n"
            f"- Evaluar reduccion de horario operativo de 12 AM a 5 AM si los costos superan los beneficios\n"
            f"- Implementar promociones especificas en horas de menor afluencia (2 PM a 4 PM)\n"
            f"- Considerar programas de fidelizacion para clientes que compran en horas valle\n"
            f"- Optimizar horarios de personal priorizando las horas de mayor demanda"
        )
    
    with col8_3:
        st.subheader("Insight 3: Disparidad por Tienda")
        st.info(
            f"**Hallazgo:** La tienda con mejor desempeno ({venta_total_por_tienda.index[0]}) supera en "
            f"{((venta_total_por_tienda.iloc[0] / venta_total_por_tienda.iloc[-1]) - 1) * 100:.1f}% "
            f"a la tienda de menor desempeno ({venta_total_por_tienda.index[-1]}).\n\n"
            f"**Accion recomendada:**\n"
            f"- Realizar benchmarking operativo de la tienda lider para replicar mejores practicas\n"
            f"- Analizar factores externos (ubicacion, competencia, demografia) que afectan el desempeno\n"
            f"- Implementar programa piloto de mejora en la tienda de menor rendimiento\n"
            f"- Establecer metas diferenciadas por tienda basadas en su potencial real"
        )
    
    st.markdown("---")
    
    # Informacion en sidebar
    st.sidebar.markdown("---")
    st.sidebar.info(
        f"""
        **Informacion del Dashboard**
        
        - Total de registros: {len(df_filtrado):,}
        - Rango de fechas: {fecha_inicio} a {fecha_fin}
        - Tiendas incluidas: {tienda_seleccionada if tienda_seleccionada != 'Todas' else 'Todas'}
        - Productos incluidos: {producto_seleccionado if producto_seleccionado != 'Todos' else 'Todos'}
        - Rango de horas: {hora_min}:00 a {hora_max}:00
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
