import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf

# 1. Load and Standardize Dataset
excel_path = "Data Fundamental Sektor Energi dan Komoditas.xlsx"
df = pd.read_excel(excel_path, sheet_name='data skripsi fix')

cols_clean = {
    'Kode': 'ticker',
    'Tahun': 'year',
    'Nama Perusahaan': 'company_name',
    'ROA': 'roa',
    'ROE': 'roe',
    'CR': 'cr',
    'PBV': 'pbv',
    'EPS': 'eps',
    'DER': 'der',
    'PER': 'per',
    'Harga Minyak WTI (Rupiah/Barel)': 'wti_oil_idr',
    'Batu Bara Acuan (Rupiah/Ton)': 'coal_idr',
    'HARGA SAHAM PENUTUP': 'stock_price'
}
df = df.rename(columns=cols_clean)

# Log transform for scaling
df['log_stock_price'] = np.log(df['stock_price'])
df['log_wti'] = np.log(df['wti_oil_idr'])
df['log_coal'] = np.log(df['coal_idr'])

# 2. Econometric Regression Modeling (Fixed Effect Model)
model_fem = smf.ols('log_stock_price ~ roa + roe + cr + pbv + eps + der + per + log_wti + log_coal + C(ticker)', data=df).fit()
print("=== Econometric Panel Regression Summary (Adjusted R-squared) ===")
print(f"Adjusted R-squared: {model_fem.rsquared_adj:.4f}")

# 3. Generate Executive Dashboard Visualization
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Panel 1: Commodity Co-Movement
macro_yearly = df.groupby('year')[['wti_oil_idr', 'coal_idr']].mean().reset_index()
ax1 = axes[0, 0]
ax1_twin = ax1.twinx()
l1 = ax1.plot(macro_yearly['year'], macro_yearly['wti_oil_idr'] / 1e3, color='#c0392b', marker='o', linewidth=2.5, label='WTI Oil (k IDR/Bbl)')
l2 = ax1_twin.plot(macro_yearly['year'], macro_yearly['coal_idr'] / 1e3, color='#2980b9', marker='s', linewidth=2.5, linestyle='--', label='Coal Price (k IDR/Ton)')
ax1.set_title("1. Global Energy Commodity Co-Movement (r = 0.894)", fontsize=12, fontweight='bold')
ax1.set_xlabel("Year")
ax1.set_ylabel("WTI Oil Price (k IDR)", color='#c0392b', fontweight='bold')
ax1_twin.set_ylabel("Coal Reference Price (k IDR)", color='#2980b9', fontweight='bold')
ax1.set_xticks(macro_yearly['year'])

# Panel 2: Correlation Heatmap
corr_cols = ['stock_price', 'wti_oil_idr', 'coal_idr', 'eps', 'roa', 'roe', 'pbv', 'der', 'cr', 'per']
corr_mat = df[corr_cols].corr()
sns.heatmap(corr_mat, annot=True, fmt=".2f", cmap='Blues', cbar=True, ax=axes[0, 1], annot_kws={"size": 8})
axes[0, 1].set_title("2. Inter-variable Correlation Matrix", fontsize=12, fontweight='bold')

# Panel 3: Profitability vs Stock Price (Scatter & Trend)
sns.scatterplot(data=df, x='eps', y='stock_price', alpha=0.6, color='#27ae60', ax=axes[1, 0])
sns.regplot(data=df, x='eps', y='stock_price', scatter=False, color='#e74c3c', ax=axes[1, 0])
axes[1, 0].set_title("3. Profitability Transmission: EPS vs Closing Stock Price", fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel("Earnings Per Share (EPS in IDR)")
axes[1, 0].set_ylabel("Closing Stock Price (IDR)")
axes[1, 0].set_ylim(0, 20000)
axes[1, 0].set_xlim(0, 4000)

# Panel 4: PBV Valuation across Top Energy Tickers
top_tickers = df.groupby('ticker')['stock_price'].mean().sort_values(ascending=False).head(8).index
df_top = df[df['ticker'].isin(top_tickers)]
sns.boxplot(data=df_top, x='ticker', y='pbv', palette="mako", ax=axes[1, 1])
axes[1, 1].set_title("4. PBV Valuation Multiples across Major Energy Issuers", fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel("Company Ticker")
axes[1, 1].set_ylabel("Price-to-Book Value (PBV)")
axes[1, 1].set_ylim(0, 5)

plt.tight_layout()
plt.savefig('energy_commodity_analytics_dashboard.png', dpi=300)
print("Dashboard visual berhasil disimpan sebagai 'energy_commodity_analytics_dashboard.png'!")
