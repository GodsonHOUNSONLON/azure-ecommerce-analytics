import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

print("📊 CHARGEMENT fact_orders AVEC PYTHON\n")
print("=" * 60)

# Configuration
server = os.getenv('SERVER')
database = os.getenv('DATABASE')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

#connection_string = f'mssql+pymssql://{username}:{password}@{server}/{database}'
connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
# Connexion
print("🔌 Connexion à Azure SQL...")
engine = create_engine(connection_string)

# Charger staging
print("📂 Chargement staging_orders...")
staging = pd.read_sql("SELECT * FROM staging_orders", engine)
print(f"✅ {len(staging):,} lignes chargées\n")

# Charger dimensions pour mapping
print("📂 Chargement dimensions...")
dim_product = pd.read_sql("SELECT product_id, stock_code FROM dim_product", engine)
dim_country = pd.read_sql("SELECT country_id, country_name FROM dim_country", engine)
print(f"✅ {len(dim_product):,} produits, {len(dim_country)} pays\n")

# Merger
print("🔗 Mapping avec dimensions...")
staging = staging.merge(dim_product, left_on='StockCode', right_on='stock_code', how='inner')
staging = staging.merge(dim_country, left_on='Country', right_on='country_name', how='inner')

# Préparer fact_orders
staging['date_id'] = pd.to_datetime(staging['InvoiceDate']).dt.strftime('%Y%m%d').astype(int)

fact_orders = staging[[
    'Invoice', 'date_id', 'CustomerID', 'product_id', 'country_id',
    'Quantity', 'Price', 'TotalAmount', 'InvoiceDate'
]].copy()

fact_orders.columns = [
    'invoice_no', 'date_id', 'customer_id', 'product_id', 'country_id',
    'quantity', 'unit_price', 'total_amount', 'invoice_datetime'
]

print(f"✅ {len(fact_orders):,} lignes prêtes\n")

# Insérer dans SQL
print("📤 Insertion dans fact_orders...")
print("Ceci peut prendre 2-3 minutes...")

fact_orders.to_sql('fact_orders', engine, if_exists='append', index=False, chunksize=10000)

print(f"✅ {len(fact_orders):,} transactions insérées !\n")

# Vérification
result = pd.read_sql("SELECT COUNT(*) AS total FROM fact_orders", engine)
print("=" * 60)
print(f"✅ VÉRIFICATION : {result['total'][0]:,} lignes dans fact_orders")
print("=" * 60)

print("\n🎉 TERMINÉ AVEC SUCCÈS !")