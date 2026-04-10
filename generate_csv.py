import pandas as pd

lunar_data = {
    "Company": ["Lunar Consulting"] * 12,
    "Quarter": ["Q4 2023", "Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", 
                "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", 
                "Q1 2026", "Q2 2026", "Q3 2026"],
    "Revenue": [8.00, 9.00, 10.00, 11.50, 13.00, 14.50, 15.00, 14.50, 13.50, 12.50, 11.25, 10.00],
    "COGS": [4.00, 4.40, 4.80, 5.20, 5.50, 6.00, 6.30, 6.40, 6.20, 6.25, 5.85, 5.50],
    "Opex": [2.00, 2.20, 2.40, 2.60, 2.90, 3.20, 3.50, 3.70, 3.80, 3.75, 3.50, 3.20],
    "AI_Costs": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.50, 0.0],
    "D_and_A": [0.50]*12,
    "Interest_Expense": [1.00]*12,
    "Tax": [0.15, 0.25, 0.35, 0.55, 0.85, 1.15, 1.10, 0.80, 0.50, 0.45, 0.16, 0.12],
    "Scheduled_Principal": [0.675]*12
}

stellar_data = {
    "Company": ["Stellar Analytics"] * 12,
    "Quarter": ["Q4 2023", "Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", 
                "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", 
                "Q1 2026", "Q2 2026", "Q3 2026"],
    "Revenue": [20.0, 21.0, 22.0, 23.0, 25.0, 26.0, 28.0, 30.0, 32.0, 35.0, 38.0, 40.0],
    "COGS": [10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0],
    "Opex": [5.0, 5.0, 5.0, 5.5, 6.0, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0],
    "AI_Costs": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    "D_and_A": [1.0]*12,
    "Interest_Expense": [1.5]*12,
    "Tax": [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.3, 1.5, 1.6, 1.8, 2.0, 2.1],
    "Scheduled_Principal": [1.0]*12
}

df_lunar = pd.DataFrame(lunar_data)
df_stellar = pd.DataFrame(stellar_data)
df_combined = pd.concat([df_lunar, df_stellar], ignore_index=True)

df_combined.to_csv("companies_financial_data.csv", index=False)
print("CSV generated successfully.")
