import apartment_scrap
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams


listings = apartment_scrap.get_listings(
    ['https://www.apartments.com/rochester-ny/1-bedrooms/', 'https://www.apartments.com/providence-ri/1-bedrooms/',
     'https://www.apartments.com/new-york-ny/1-bedrooms/'])

listings.to_excel('Output.xlsx', index=False)

nyc_listings = listings[
    (listings['Town'] == 'Irondequoit') | (listings['Town'] == 'New York') | (listings['Town'] == 'Manhattan')]
providence_listings = listings[
    (listings['Town'] == 'North Providence') | (listings['Town'] == 'Pawtucket') | (listings['Town'] == 'Cranston') |
    (listings['Town'] == 'Johnston')]
rochester_listings = listings[
    (listings['Town'] == 'Rochester') | (listings['Town'] == 'Greece') | (listings['Town'] == 'Webster')]

nyc_listings['Group Area'] = 'NYC'
providence_listings['Group Area'] = 'Providence'
rochester_listings['Group Area'] = 'Rochester'

rcParams['font.sans-serif'] = ['Times New Roman']
sns.distplot(nyc_listings['Price'], hist=False)
sns.distplot(providence_listings['Price'], hist=False)
sns.distplot(rochester_listings['Price'], hist=False).set(xlim=(0, 5000))
plt.legend(['NYC', 'Providence', 'Rochester'])
plt.suptitle('Rent by Region', fontsize=20)
plt.xlabel('Rent ($)', fontsize=14)
plt.ylabel('Density', fontsize=14)
plt.show()

grouped_df = nyc_listings.append(providence_listings.append(rochester_listings))
sns.boxenplot(x='Group Area', y='Price', data=grouped_df, showfliers=False)
plt.show()
