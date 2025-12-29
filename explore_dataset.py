import pandas as pd

# 1. CHARGER LE FICHIER
print("📂 Chargement du fichier...")
df = pd.read_excel('online_retail_II.xlsx')
print("✅ Fichier chargé !\n")

# 2. INFOS DE BASE
print("=" * 50)
print("📊 INFORMATIONS GÉNÉRALES")
print("=" * 50)
print(f"Nombre de lignes : {len(df)}")
print(f"Nombre de colonnes : {len(df.columns)}")
print(f"Colonnes : {list(df.columns)}\n")

# 3. APERÇU DES DONNÉES
print("=" * 50)
print("👀 APERÇU (5 premières lignes)")
print("=" * 50)
print(df.head())
print()

# 4. VALEURS MANQUANTES
print("=" * 50)
print("⚠️ VALEURS MANQUANTES")
print("=" * 50)
print(df.isnull().sum())
print()

# 5. STATISTIQUES
print("=" * 50)
print("📈 STATISTIQUES")
print("=" * 50)
print(df.describe())
print()

# 6. PROBLÈMES DÉTECTÉS
print("=" * 50)
print("🚨 PROBLÈMES")
print("=" * 50)
print(f"Retours (Quantity < 0) : {(df['Quantity'] < 0).sum()}")
print(f"Prix à 0 : {(df['Price'] == 0).sum()}")
print(f"CustomerID manquants : {df['Customer ID'].isnull().sum()}")

print("\n✅ EXPLORATION TERMINÉE !")