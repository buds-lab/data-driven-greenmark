import pandas as pd

types = ['Office', 'Office Interior', 'Others', 'Commercial', 'Data Centre', 'District', 'Hotel', 'Industrial', 'Institutional', 'Institutional (Healthcare)', 'Institutional (School)', 'Infrastructure', 'Park', 'Public Housing', 'Rapid Transit System', 'Residential', 'Retail', 'Retail (Tenant)', 'Restaurant', 'Supermarkets', 'Mixed Development', 'Healthier Workplaces', 'Laboratories']

dfs = []
for t in types:
    t = pd.read_csv(f"{t}.csv")
    dfs.append(t)

all_types = pd.concat(dfs)
all_types["bca_id"] = ''
for _,row in all_types.iterrows():
    row["bca_id"] = row["link"].split('=')[1]

all_types.to_csv("all_types.csv", index=False)
GM_buildings = pd.read_csv("GM_buildings_formatted.csv")

GM_buildings.\
merge(all_types, on='bca_id').\
drop(columns=['link']).\
to_csv("GM_new_types.csv", index=False)
