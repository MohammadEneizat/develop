# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:36:38 2022

@Author: Mohammad Maher Eneizat 
@Email: mohammad.eneizat@iu-study.org
@Github: 

The visualizition module performs visualize train data, ideal functions and mapping
 

"""

#import extranal
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource


class visualize_data:
    
    """ Class visualize_data is used for visualize train data, ideal functions and mapping """
    
    def visualize_training_data(train_np):
        
        """function visualize train data"""
        
    
        
        #add html output page
        output_file('index.html')
                
        #add plot
        p = figure(
        title = 'Training Function 1',
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        p.line(train_np[0:,0], train_np[0:,1],line_width = 2, color = "green")
        show(p)
        
        #add plot
        p = figure(
        title = 'Training Function 2',
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        p.line(train_np[0:,0], train_np[0:,2], line_width = 2, color = "red")
        show(p)
        
        #add plot
        p = figure(
        title = 'Training Function 3',
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        p.line(train_np[0:,0], train_np[0:,3], line_width = 2, color = "blue")
        show(p)
        #add plot
            
        p = figure(
        title = 'Training Function 4',
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        p.line(train_np[0:,0], train_np[0:,4], line_width = 2, color = "orange")
        show(p)
    
    
    def visualize_ideal_data(New_Ideal_Function_table,ideal_function_index):
        """function visualize ideal functions"""
    
        
        #add html output page
        output_file('index.html')
                
        #add plot
        p = figure(
        title = 'Ideal Function Y{}'.format(ideal_function_index[0]),
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,1], 
                 line_width = 2, color = "green")
        show(p)
        
        #add plot
        p = figure(
        title = 'Ideal Function Y{}'.format(ideal_function_index[1]),
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,2], 
                 line_width = 2, color = "red")
        show(p)
        
        #add plot
        p = figure(
        title = 'Ideal Function Y{}'.format(ideal_function_index[2]),
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,3], 
                 line_width = 2, color = "blue")
        show(p)
        
        #add plot
        p = figure(
        title = 'Ideal Function Y{}'.format(ideal_function_index[3]),
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,4], 
                 line_width = 2, color = "orange")
        show(p)
    
    
    
    def visualize_Before_Mapping(New_Ideal_Function_table,test,ideal_function_index):
        """function visualize ideal functions and test data before mapping"""
        
        #add source
        test = ColumnDataSource(test)
        
        
        #add html output page
        output_file('index.html')
                
        #add plot
        p = figure(
        title = 'Before Mapping',      
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,1], 
                 line_width = 2, color = "green",legend_label="Y{}".format(ideal_function_index[0]))
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,2], 
                 line_width = 2, color = "red",legend_label="Y{}".format(ideal_function_index[1]))
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,3], 
                 line_width = 2, color = "blue",legend_label="Y{}".format(ideal_function_index[2]))
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,4], 
                 line_width = 2, color = "orange",legend_label="Y{}".format(ideal_function_index[3]))
        
        #add scatter plot
        p.circle( source=test,size=4, color='Purple', alpha = 0.8,legend_label="Test points")
        
        
        show(p)
        
        
    
    
    def visualize_After_Mapping(New_Ideal_Function_table,X_test_results,Y_test_results,ideal_function_index):
        """function visualize ideal functions and test data After mapping"""
        
        
        
        #add html output page
        output_file('index.html')

        #add plot
        p = figure(
        title = 'After Mapping',      
        x_axis_label = 'X Axis',
        y_axis_label = 'Y Axis')
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,1], 
                 line_width = 2, color = "green",legend_label="Y{}".format(ideal_function_index[0]))
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,2], 
                 line_width = 2, color = "red",legend_label="Y{}".format(ideal_function_index[1]))
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,3], 
                 line_width = 2, color = "blue",legend_label="Y{}".format(ideal_function_index[2]))
        
        p.line(New_Ideal_Function_table.iloc[0:,0], New_Ideal_Function_table.iloc[0:,4], 
                 line_width = 2, color = "orange",legend_label="Y{}".format(ideal_function_index[3]))
        
        #add scatter plot
        p.circle(x = X_test_results, y = Y_test_results,color='Purple', size = 4, alpha = 0.8,legend_label="Test points Mapping")
        
        
        show(p)
   