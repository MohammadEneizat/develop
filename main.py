# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:36:38 2022

@Author: Mohammad Maher Eneizat 
@Email: mohammad.eneizat@iu-study.org
@Github: 

The main module performs call functions, print  results and all main commands

"""

#import external
import pandas as pd
import numpy as np

#import internal
from SQLiteDB import loading_Data_sqlite
from ideal_function import ideal_function
from visualizition import visualize_data


#import train.csv 
train = pd.read_csv("train.csv")
loading_Data_sqlite.load_train(train)

#import ideal.csv 
ideal = pd.read_csv("ideal.csv")
loading_Data_sqlite.load_ideal(ideal)


"""find ideal functions term"""

#convert train to Numpy array
train_np = np.array(train)

#convert ideal to Numpy array
ideal_np = np.array(ideal)


#loop to call ideal_function_fit and find 4 ideal function values,index,maximum deviation 
i = 1
ideal_function_values = []
ideal_function_index = []
ideal_function_max_div = []

while i < len(train.columns):
    value, index, max_div = ideal_function.ideal_function_fit(i,train,ideal,train_np,ideal_np)

    ideal_function_values.append(value)
    ideal_function_index.append(index)
    ideal_function_max_div.append(max_div)
    i += 1

print("Minimum sum of the squared errors = {} ".format(ideal_function_values)) #print Minimum SSE (sum of the squared errors)
print("the Four ideal functions Index = {} ".format(ideal_function_index)) #print the Four ideal functions Index
print("the largest divertion = {} ".format(ideal_function_max_div)) #print the largest divertion






#bulid new table contains x values and four y ideal functions
ideal_function_index_with_X = [0]
ideal_function_index_with_X = ideal_function_index_with_X + ideal_function_index

New_Ideal_Function_table = ideal.iloc[0:, ideal_function_index_with_X]
print(New_Ideal_Function_table)



"""Mapping term"""
    

#Load test.csv 
test = pd.read_csv("test.csv")

#find x ideal functions, y ideal functions, x test, y test from datasets
x_ideal =New_Ideal_Function_table.iloc[0: , 0:1]
y_ideal =New_Ideal_Function_table.iloc[0: , 1:5]

x_test =test.iloc[0: , 0:1]
y_test = test.iloc[0: , 1:2]

#find x ideal functions numpy array, y ideal functions numpy array, x testnumpy array
#y test numpy array to use it in calculations
x_ideal_np = np.array(x_ideal)
y_ideal_np = np.array(y_ideal)


x_test_np = np.array(x_test)
y_test_np =np.array(y_test)


#call mapping_find function to find test pairs map with ideal functions and store returns as tuple
results,X_test_results,Y_test_results = ideal_function.mapping_find(x_test_np,x_ideal_np,y_test_np,y_ideal_np,ideal_function_max_div,ideal_function_index)



results_pd = pd.DataFrame(results) #dataframe of results and print
print (results_pd)


#send results to csv file with name 'map_table.csv'
map_table = results_pd.to_csv('map_table.csv',index=False)


#call Mapping_data to bulid table in sqlite
loading_Data_sqlite.Mapping_data()





"""visualiztion term: 
    training data
    ideal functions
    ideal functions with test points before mapping
    ideal functions with test points After mapping"""
    
    

#visualize training data
visualize_data.visualize_training_data(train_np)

#visualize ideal functions
visualize_data.visualize_ideal_data(New_Ideal_Function_table,ideal_function_index)

#visualize ideal functions with test points before mapping
visualize_data.visualize_Before_Mapping(New_Ideal_Function_table,test,ideal_function_index)

#visualize ideal functions with test points After mapping
visualize_data.visualize_After_Mapping(New_Ideal_Function_table,X_test_results,Y_test_results,ideal_function_index)
