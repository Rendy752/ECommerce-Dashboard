import pandas as pd
import streamlit as st
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

def create_products_revenue_df():
    products_df = pd.read_csv("products.csv")
    order_items_df = pd.read_csv("order_items.csv")
    orders_df = pd.read_csv("orders.csv")
    order_payments_df = pd.read_csv("order_payments.csv")
    products_revenue_df = products_df.merge(order_items_df, on="product_id", how="left")
    products_revenue_df = products_revenue_df.merge(orders_df, on="order_id", how="left")
    products_revenue_df = products_revenue_df.merge(order_payments_df, on="order_id", how="left")

    return products_revenue_df

def create_show_orders_late_df():
    orders_df = pd.read_csv("orders.csv")
    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
    orders_2017_df = orders_df[orders_df["order_purchase_timestamp"].dt.year == 2017]
    orders_late_df = orders_2017_df[orders_2017_df["order_estimated_delivery_date"] < orders_2017_df["order_delivered_customer_date"]]
    orders_late_df["month"] = orders_late_df["order_purchase_timestamp"].dt.strftime('%B')
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December']
    orders_late_df['month'] = pd.Categorical(orders_late_df['month'], categories=month_order, ordered=True)
    orders_late_df.groupby("month").agg({"order_id": "count"}).rename(columns={'order_id': 'count'})
    show_orders_late_df = orders_late_df.groupby("month").agg({"order_id": "count"}).rename(columns={'order_id': 'count'})

    return show_orders_late_df

def create_chart_products_revenue(products_revenue_df):
    top_products = products_revenue_df.groupby("product_category_name").agg({"price": "sum"}).sort_values(by="price", ascending=False).head(5)
    worst_products = products_revenue_df.groupby("product_category_name").agg({"price": "sum"}).sort_values(by="price", ascending=True).head(5)

    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.15, subplot_titles=("Top 5 Product Revenue", "Worst 5 Product Revenue"))

    fig.add_trace(go.Bar(x=top_products['price'], y=top_products.index, orientation='h', marker_color="#72BCD4",
                     hovertemplate='%{y}: %{x}<extra></extra>'),
              row=1, col=1)
    
    fig.add_trace(go.Bar(x=worst_products['price'], y=worst_products.index, orientation='h', marker_color="#D3D3D3",
                     hovertemplate='%{y}: %{x}<extra></extra>'),
              row=2, col=1)

    fig.update_layout(height=800, showlegend=False, title_text="Best and Worst Performing Products by Revenue")
    fig.update_yaxes(title_text="", autorange="reversed") 
    fig.update_xaxes(title_text="Revenue")

    return fig

def create_chart_orders_late(show_orders_late_df):
    fig = px.line(show_orders_late_df, 
              x=show_orders_late_df.index, 
              y="count", 
              markers=True, 
              line_shape='linear', 
              title="Total Late Order Case per Month (2017)")

    fig.update_traces(line=dict(width=2, color="#72BCD4"), marker=dict(size=8))
    fig.update_layout(
        xaxis=dict(title="Month", tickangle=45, tickfont=dict(size=10)),
        yaxis=dict(title="Total Late Orders", tickfont=dict(size=10)),
        title=dict(x=0.5, xanchor='center', font=dict(size=20))
    )

    return fig

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

st.title("📊 Dashboard Visualisasi Data E-Commerce")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📈 Data Revenue Berdasarkan Produk")
    products_revenue_df = create_products_revenue_df()
    st.plotly_chart(create_chart_products_revenue(products_revenue_df))

with col2:
    st.subheader("🚚 Data Keterlambatan Pengiriman Pada Tahun 2017")
    show_orders_late_df = create_show_orders_late_df()
    st.plotly_chart(create_chart_orders_late(show_orders_late_df))

with st.expander("🔍 Lihat Detail"):
    st.write("Kategori produk **beleza_saude** memiliki peran vital dalam menyumbang pendapatan paling banyak bagi perusahaan yang memiliki total pendapatan sebesar **1,297,490.77** diikuti oleh **relogios_presentes**, **cama_mesa_banho**, dst. Sedangkan yang paling sedikit yaitu kategori produk **seguros_e_servicos** yang hanya memiliki total pendapatan sebesar **283.29**.")
    st.write("Tren kasus keterlambatan pengiriman barang diatas waktu estimasi pada tahun 2017 cenderung mengalami kenaikan dan penurunan pada awal bulan, akan mengalami **kenaikan drastis** pada bulan **November**, dan **penurunan drastis** pada bulan **Desember**.")

st.caption("👤 Created by: Rendy Pratama")