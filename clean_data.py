import pandas as pd

print("🧹 Nettoyage des données...\n")

# Charger
df = pd.read_excel('online_retail_II.xlsx')
print(f"Avant : {len(df):,} lignes")

# Nettoyer
df = df[df['Customer ID'].notna()]  # Supprimer CustomerID vides
df = df[df['Quantity'] > 0]         # Supprimer retours
df = df[df['Price'] > 0]            # Supprimer prix = 0

# Ajouter TotalAmount
df['TotalAmount'] = df['Quantity'] * df['Price']

print(f"Après : {len(df):,} lignes")
print(f"Revenue : £{df['TotalAmount'].sum():,.2f}\n")

# Sauvegarder
df.to_csv('online_retail_clean.csv', index=False)
print("✅ Fichier créé : online_retail_clean.csv")