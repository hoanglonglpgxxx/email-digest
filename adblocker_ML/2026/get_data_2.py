#Handle image for dataset 01032026
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df_dom = pd.read_csv("dataset_01032026.csv")

plt.figure(figsize=(8, 6))
sns.boxplot(x='is_ad', y='dom_depth', data=df_dom, palette='Set2')
plt.title('Hình 2. Phân phối Độ sâu DOM giữa mẫu Sạch (0) và Quảng cáo (1)')
plt.ylabel('Độ sâu DOM (Depth)')
plt.savefig('dom_distribution.png')
plt.show()