import pandas as pd
import pymysql
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


pio.templates.default = "plotly_dark"

def init_dashboard(flask_app):
    # -------------------- DATABASE CONNECTION --------------------
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password='',
        database="afashion"
    )

    # -------------------- SQL QUERIES --------------------
    products_df = pd.read_sql("""
        SELECT p.product_id, p.price, p.rating,
               c.category_name, b.brand_name
        FROM products p
        JOIN subcategories s ON p.subcategory_id = s.subcategory_id
        JOIN categories c ON s.category_id = c.category_id
        JOIN brands b ON p.brand_id = b.brand_id
    """, connection)

    users_df = pd.read_sql("SELECT * FROM users", connection)
    cart_items_df = pd.read_sql("SELECT * FROM cart_items", connection)

    brands_df = pd.read_sql("""
        SELECT b.brand_name, COUNT(p.product_id) AS product_count,
               ROUND(AVG(p.price), 2) AS avg_price
        FROM products p
        JOIN brands b ON p.brand_id = b.brand_id
        GROUP BY b.brand_name
        ORDER BY product_count DESC
        LIMIT 10
    """, connection)

    connection.close()

    # -------------------- BASIC STATS --------------------
    total_products = products_df['product_id'].nunique()
    total_brands = brands_df['brand_name'].nunique()
    total_categories = products_df['category_name'].nunique()
    avg_price = round(products_df['price'].mean(), 2)
    total_users = users_df.shape[0]
    total_cart_items = cart_items_df.shape[0]

    # -------------------- CHARTS --------------------
   
    category_count = products_df.groupby("category_name").size().reset_index(name="product_count")
    fig_category = go.Figure(data=[go.Bar(
        x=category_count['category_name'],
        y=[0]*len(category_count),  
        marker=dict(
            color=category_count['product_count'],
            colorscale='Viridis',
            line=dict(color='rgb(50,50,50)', width=1.5)
        ),
        text=category_count['product_count'],
        textposition='auto',
        hovertemplate='Category: %{x}<br>Products: %{y}'
    )])

    # Animate the bars from 0 to actual value
    fig_category.update_traces(y=category_count['product_count'])
    fig_category.update_layout(
        title="Products per Category (Animated)",
        paper_bgcolor='#111',
        plot_bgcolor='#111',
        font=dict(color='white', size=14),
        xaxis_title="Category",
        yaxis_title="Number of Products",
        transition={'duration':1000, 'easing':'cubic-in-out'}
    )

    # Brand-wise product distribution (donut with hover)
    fig_brand_pie = px.pie(
        brands_df,
        names="brand_name",
        values="product_count",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_brand_pie.update_traces(
        textinfo='percent+label',
        pull=[0.05]*len(brands_df),
        hoverinfo='label+value+percent',
        marker=dict(line=dict(color='#111', width=2))
    )
    fig_brand_pie.update_layout(
        title="Brand-wise Product Distribution",
        paper_bgcolor='#111',
        plot_bgcolor='#111',
        transition={'duration':1000, 'easing':'cubic-in-out'}
    )

    # Average price per brand (animated gradient bars)
    fig_brand_price = px.bar(
        brands_df,
        x="brand_name",
        y=[0]*len(brands_df),  
        text="avg_price",
        color="avg_price",
        color_continuous_scale=px.colors.sequential.Plasma
    )
    fig_brand_price.update_traces(y=brands_df['avg_price'], hovertemplate='Brand: %{x}<br>Avg Price: $%{y}')
    fig_brand_price.update_layout(
        title="Average Product Price per Brand",
        paper_bgcolor='#111',
        plot_bgcolor='#111',
        font_color='white',
        transition={'duration':1200, 'easing':'cubic-in-out'}
    )

    # Top 10 brands by product count (animated)
    top_brands = brands_df.head(10)
    fig_top_brands = px.bar(
        top_brands,
        x="brand_name",
        y=[0]*len(top_brands),
        text="product_count",
        color="product_count",
        color_continuous_scale=px.colors.sequential.Cividis
    )
    fig_top_brands.update_traces(y=top_brands['product_count'], hovertemplate='Brand: %{x}<br>Products: %{y}')
    fig_top_brands.update_layout(
        title="Top 10 Brands by Number of Products",
        paper_bgcolor='#111',
        plot_bgcolor='#111',
        font_color='white',
        transition={'duration':1200, 'easing':'cubic-in-out'}
    )

    # -------------------- DASH APP --------------------
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname="/dashboard/"
    )

    # -------------------- CARD STYLE --------------------
    card_style = {
        "border": "1px solid #333",
        "padding": "20px",
        "width": "180px",
        "textAlign": "center",
        "borderRadius": "10px",
        "boxShadow": "0 4px 10px rgba(0,0,0,0.5)",
        "backgroundColor": "#1c1c1c",
        "fontWeight": "bold",
        "fontSize": "18px",
        "margin": "10px",
        "transition": "transform 0.3s ease, box-shadow 0.3s ease",
        "cursor": "pointer"
    }

    # -------------------- DASH LAYOUT --------------------
    dash_app.layout = html.Div(
        style={"padding": "20px", "backgroundColor": "#111", "color": "#fff", "minHeight": "100vh"},
        children=[

            html.H1("E-Commerce Dashboard", style={"textAlign": "center", "marginBottom": "40px"}),

            # Stats cards with hover effect
            html.Div(
                style={"display": "flex", "flexWrap": "wrap", "justifyContent": "center", "marginBottom": "40px"},
                children=[
                    html.Div([html.Span("🛍️", style={"fontSize":"30px"}), html.P(f"Total Products: {total_products}")], style=card_style),
                    html.Div([html.Span("🏷️", style={"fontSize":"30px"}), html.P(f"Total Brands: {total_brands}")], style=card_style),
                    html.Div([html.Span("📂", style={"fontSize":"30px"}), html.P(f"Total Categories: {total_categories}")], style=card_style),
                    html.Div([html.Span("💰", style={"fontSize":"30px"}), html.P(f"Avg Price: ${avg_price}")], style=card_style),
                    html.Div([html.Span("👥", style={"fontSize":"30px"}), html.P(f"Total Users: {total_users}")], style=card_style),
                    html.Div([html.Span("🛒", style={"fontSize":"30px"}), html.P(f"Total Cart Items: {total_cart_items}")], style=card_style)
                ]
            ),

            html.Hr(style={"borderColor": "#444"}),

            # Charts with animation
            html.Div([
                dcc.Graph(figure=fig_category, className="graph-container"),
                dcc.Graph(figure=fig_brand_pie, className="graph-container"),
                dcc.Graph(figure=fig_brand_price, className="graph-container"),
                dcc.Graph(figure=fig_top_brands, className="graph-container")
            ])
        ]
    )

    return dash_app
