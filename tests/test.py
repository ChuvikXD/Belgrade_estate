import pandas as pd
df = pd.read_csv('apartments.csv')
df['floor'] = df['floor'].replace('PR', '1').replace('SU', '-1').replace('VPR', '0').replace('2_4', '2').replace('5_10', '3').replace('11+', '4').replace('PTK', '5').replace('NPR', '1') #VPR-верхний цокольный, #PR-первый, #SU - подвал, PTK-лофт, NPR-нижний этаж
print(df['floor'])