# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:36:38 2022

@Author: Mohammad Maher Eneizat 
@Email: mohammad.eneizat@iu-study.org
@Github: 

The ideal_function module performs finding ideal functions and mapping
 with test points

"""

#import external
import  numpy as np



class ideal_function:
    
    """ Class ideal_function is used for find ideal functions and mapping """
    

    
    
    def ideal_function_fit(i,train,ideal,train_np,ideal_np):
        
        """
        function finds matches between training functions and ideal functions based on 
        Minimum SSE (sum of the squared errors)
        return: Minimum SSE, index ideal functions, the largest divertion
        """
        
        
        # Loop to find sequred divertion between train data and ideal data
        Div_squerd_sum_list = []
        for x in range (len(ideal.columns)):
            Div_squerd = (train_np[0:,i:i+1] - ideal_np[0:,1:x+1])**2
            
        # Loop to find sum of sequred divertion between train data and ideal data    
        for y in range (len(ideal.columns)-1):
            Div_squerd_sum = np.sum(Div_squerd[0:,y:y+1])
            Div_squerd_sum_list.append(Div_squerd_sum)
            
        # find Minimum SSE, index ideal functions, the largest divertion  
        Index_Y_ideal = Div_squerd_sum_list.index(min(Div_squerd_sum_list))+1
        min_Div_squerd_sum = min(Div_squerd_sum_list)
    
    
        Div = abs(train_np[0:,i:i+1] - ideal_np[0:,Index_Y_ideal:Index_Y_ideal+1])
        max_div = np.max(Div)
        
        return min_Div_squerd_sum,Index_Y_ideal,max_div
              
    
    
    def mapping_find(x_test_np,x_ideal_np,y_test_np,y_ideal_np,ideal_function_max_div,ideal_function_indexs):
        
        """
        determine for each and every x-y-pair test points are mapping with four ideal functions
        :return: test function paired,divertion and No. of ideal function
        """
    
        X_test_results=[] 
        Y_test_results = []
        Delta_results = []
        No_of_y_results = []
        
        """
        # Loop to find absolute divertion between test data and ideal data, compare results with 
        the largest divertion between ideal functions and train data multiply with mappaing error = sqrt(2)
        if less than or equal thats mean test pairs are mapping with the ideal function
        """
        
        
        map_error= np.sqrt(2)
        ideal_function_max_div = np.array(ideal_function_max_div)
        for i in range (100):
            for j in range(400):
                if x_test_np[i] == x_ideal_np[j]:
                    for y in range (4):
                        if (abs(y_test_np[i] - y_ideal_np[j:j+1,y])<= (ideal_function_max_div*map_error)).any():
                            X_test_results = np.append(X_test_results,x_test_np[i])
                            Y_test_results = np.append(Y_test_results,y_test_np[i])
                            Delta_results=np.append(Delta_results,abs(y_test_np[i] - y_ideal_np[j:j+1,y]))
                            No_of_y_results=np.append(No_of_y_results,ideal_function_indexs[y:y+1])
                            
                            
        # find est function paired,divertion and No. of ideal function                    
        results_dict = {"X (test func)":X_test_results,"Y (test func)":Y_test_results,"Delta Y (test func)":Delta_results,
                    "No. of ideal func":No_of_y_results}
        
        return results_dict,X_test_results,Y_test_results
    
    
    

    
    


    
    
    
