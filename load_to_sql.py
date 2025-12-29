import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os
from datetime import datetime

# Charger les variables d'environnement depuis .env
load_dotenv()

print("📤 CHARGEMENT DES DONNÉES VERS AZURE SQL\n")
print("=" * 60)

# ================================================
# 1. CONFIGURATION CONNEXION SQL (SÉCURISÉE)
# ================================================
server = os.getenv('SERVER')
database = os.getenv('DATABASE')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

#connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes; TrustServerCertificate=no'

connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

print("🔌 Connexion à Azure SQL...")
try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    print("✅ Connecté avec succès !\n")
except Exception as e:
    print(f"❌ Erreur connexion : {e}")
    exit()

# ================================================
# 2. CHARGER LES DONNÉES NETTOYÉES
# ================================================
print("📂 Chargement du fichier CSV nettoyé...")
df = pd.read_csv('online_retail_clean.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
print(f"✅ {len(df):,} lignes chargées\n")

# ================================================
# 3. REMPLIR dim_country
# ================================================
print("=" * 60)
print("🌍 REMPLISSAGE dim_country")
print("=" * 60)

countries = df.groupby('Country').agg({
    'Invoice': 'count',
    'TotalAmount': 'sum'
}).reset_index()

for _, row in countries.iterrows():
    cursor.execute("""
        INSERT INTO dim_country (country_name, total_orders, total_revenue)
        VALUES (?, ?, ?)
    """, row['Country'], int(row['Invoice']), float(row['TotalAmount']))

conn.commit()
print(f"✅ {len(countries)} pays insérés\n")

# ================================================
# 4. REMPLIR dim_customer
# ================================================
print("=" * 60)
print("👤 REMPLISSAGE dim_customer")
print("=" * 60)

customers = df.groupby('Customer ID').agg({
    'Country': 'first',
    'InvoiceDate': ['min', 'max'],
    'Invoice': 'count',
    'TotalAmount': 'sum'
}).reset_index()

customers.columns = ['customer_id', 'country', 'first_purchase', 'last_purchase', 'total_orders', 'total_revenue']

for _, row in customers.iterrows():
    cursor.execute("""
        INSERT INTO dim_customer (customer_id, country_name, first_purchase_date, last_purchase_date, total_orders, total_revenue)
        VALUES (?, ?, ?, ?, ?, ?)
    """, 
    int(row['customer_id']), 
    row['country'], 
    row['first_purchase'].date(), 
    row['last_purchase'].date(), 
    int(row['total_orders']), 
    float(row['total_revenue']))

conn.commit()
print(f"✅ {len(customers):,} clients insérés\n")

# ================================================
# 5. REMPLIR dim_product
# ================================================
print("=" * 60)
print("📦 REMPLISSAGE dim_product")
print("=" * 60)

products = df.groupby(['StockCode', 'Description']).agg({
    'Price': 'mean',
    'Quantity': 'sum'
}).reset_index()

product_mapping = {}  # Pour mapper StockCode -> product_id

for _, row in products.iterrows():
    cursor.execute("""
        INSERT INTO dim_product (stock_code, description, avg_price, total_quantity_sold)
        VALUES (?, ?, ?, ?)
    """, row['StockCode'], row['Description'], float(row['Price']), int(row['Quantity']))
    
    cursor.execute("SELECT @@IDENTITY")
    product_id = cursor.fetchone()[0]
    product_mapping[row['StockCode']] = product_id

conn.commit()
print(f"✅ {len(products):,} produits insérés\n")

# ================================================
# 6. REMPLIR dim_date
# ================================================
print("=" * 60)
print("📅 REMPLISSAGE dim_date")
print("=" * 60)

dates = pd.DataFrame({
    'date': pd.date_range(start='2009-12-01', end='2011-12-31', freq='D')
})

dates['date_id'] = dates['date'].dt.strftime('%Y%m%d').astype(int)
dates['year'] = dates['date'].dt.year
dates['quarter'] = dates['date'].dt.quarter
dates['month'] = dates['date'].dt.month
dates['month_name'] = dates['date'].dt.month_name()
dates['day'] = dates['date'].dt.day
dates['day_of_week'] = dates['date'].dt.dayofweek
dates['day_name'] = dates['date'].dt.day_name()
dates['is_weekend'] = dates['day_of_week'].isin([5, 6]).astype(int)

for _, row in dates.iterrows():
    cursor.execute("""
        INSERT INTO dim_date (date_id, full_date, year, quarter, month, month_name, day, day_of_week, day_name, is_weekend)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, 
    int(row['date_id']), 
    row['date'].date(), 
    int(row['year']), 
    int(row['quarter']), 
    int(row['month']), 
    row['month_name'], 
    int(row['day']), 
    int(row['day_of_week']), 
    row['day_name'], 
    int(row['is_weekend']))

conn.commit()
print(f"✅ {len(dates):,} dates insérées\n")

# ================================================
# 7. REMPLIR fact_orders
# ================================================
print("=" * 60)
print("📊 REMPLISSAGE fact_orders (peut prendre 5-10 min)")
print("=" * 60)

# Récupérer country_id mapping
cursor.execute("SELECT country_id, country_name FROM dim_country")
country_mapping = {row[1]: row[0] for row in cursor.fetchall()}

# Préparer les données
df['date_id'] = df['InvoiceDate'].dt.strftime('%Y%m%d').astype(int)
df['product_id'] = df['StockCode'].map(product_mapping)
df['country_id'] = df['Country'].map(country_mapping)

batch_size = 1000
total = len(df)

for i in range(0, total, batch_size):
    batch = df.iloc[i:i+batch_size]
    
    for _, row in batch.iterrows():
        cursor.execute("""
            INSERT INTO fact_orders (invoice_no, date_id, customer_id, product_id, country_id, quantity, unit_price, total_amount, invoice_datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, 
        row['Invoice'], 
        int(row['date_id']), 
        int(row['Customer ID']), 
        int(row['product_id']), 
        int(row['country_id']), 
        int(row['Quantity']), 
        float(row['Price']), 
        float(row['TotalAmount']), 
        row['InvoiceDate'])
    
    conn.commit()
    print(f"  Progression : {min(i+batch_size, total):,} / {total:,} lignes ({min(i+batch_size, total)/total*100:.1f}%)")

print(f"\n✅ {total:,} transactions insérées\n")

# ================================================
# 8. VÉRIFICATION FINALE
# ================================================
print("=" * 60)
print("✅ VÉRIFICATION DES DONNÉES")
print("=" * 60)

tables = ['dim_country', 'dim_customer', 'dim_product', 'dim_date', 'fact_orders']

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table:20s} : {count:,} lignes")

# Fermer connexion
cursor.close()
conn.close()

print("\n" + "=" * 60)
print("🎉 CHARGEMENT TERMINÉ AVEC SUCCÈS !")
print("=" * 60)