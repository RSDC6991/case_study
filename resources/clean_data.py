# #####################################3
# Name             : clean_data.py    #3
# Author           : Arpit Mathur     #3
# #####################################3

import os
import pandas as pd
from sklearn import preprocessing

filePath = os.path.realpath(__file__)
filePath = filePath[:filePath.rfind('\\')]

file_path = filePath+"\\..\\data_orig\\case_study_ML.xlsx"
csv_file_path = filePath+"\\..\\data_orig\\case_study_ML.csv"

case_study_data = pd.read_excel(file_path)
case_study_data.to_csv(csv_file_path, index=False)

print('basic information about the database')
case_study_data.info()
print('data head')
print(case_study_data.head())

print('dataset - promotion')
promotion = pd.read_csv(filePath+'\\..\\data_orig\\promotion.csv')
promotion.rename(columns={
        'FU': 'SKU',
        'Weeks': 'ISO_Week'
        }, inplace=True)
promotion['Promotion'] = 1
print(promotion.head())
print(promotion.describe())


def plotting(dat, titlePrefix=""):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    title = titlePrefix+"Item_{0}".format(dat['SKU'].iloc[0])
    plt.plot(dat['ISO_Week'], dat['Sales'])
    plt.title(title)
    plt.ylabel('Net Sales')
    plt.xlabel('Date')
    plt.show()
    plt.savefig(filePath+'\\..\\visualizations\\{0}.png'.format(title))
    plt.close()


print('\n\ndescriptive statistics\n')
uniqueColNames = case_study_data.SKU.unique()

final_data = []
for colName in uniqueColNames:
    print('\n\n\t\t Item : {0}'.format(colName))
    # obtain unique rows for that particular consumer good
    uniqueData = case_study_data[case_study_data['SKU'] == colName]
    # filling all NaN's with mean values
    uniqueData.fillna(uniqueData.mean(), inplace=True)

    # plotting to get better idea
    plotting(uniqueData, "Before Cleaning ")

    # obtaining mean and Standard Deviation of Sales data
    print("\nColumn 'Sales' Mean {0}\nSTD : {1}".format(
            uniqueData['Sales'].mean(), uniqueData['Sales'].std()))

    # merging dataframe with promotion dataframe as a left join
    # and then replace all NaN's with default value 0, denoting not a promotion
    mergedDataframe = pd.merge(uniqueData, promotion, on=['SKU', 'ISO_Week'],
                               how='left')
    mergedDataframe.fillna(0, inplace=True)

    # label encoding for all seasons
    mergedDataframe.loc[mergedDataframe['Season'] == 'WINTER', 'Season'] = 0
    mergedDataframe.loc[mergedDataframe['Season'] == 'SPRING', 'Season'] = 1
    mergedDataframe.loc[mergedDataframe['Season'] == 'SUMMER', 'Season'] = 2
    mergedDataframe.loc[mergedDataframe['Season'] == 'AUTUMN', 'Season'] = 3

    # outlier handling
    mergedDataframe["Sales"] = mergedDataframe["Sales"].mask(
            mergedDataframe['Sales'] > mergedDataframe['Sales'].mean() +
            2*mergedDataframe['Sales'].std(), mergedDataframe['Sales'].mean())

    # scale the Sale Data
    x = mergedDataframe[['Sales']].values.astype(float)
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    # print(x_scaled)
    mergedDataframe.drop("Sales", inplace=True, axis=1)
    mergedDataframe.insert(2, "Sales", x_scaled, True)

    # save the data frame to a csv in the 'data_clean' folder with name
    # same as item name
    mergedDataframe.to_csv(
            filePath+'\\..\\data_clean\\{0}.csv'.format(colName),
            index=False
            )

    # plotting to get better idea
    plotting(mergedDataframe, "After Cleaning ")
    final_data.append(mergedDataframe)

final_data = pd.concat(final_data, ignore_index=True)
# print(final_data)
final_data.to_csv(filePath+'\\..\\data_clean\\overall.csv', index=False)
