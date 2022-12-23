# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:36:38 2022

@Author: Mohammad Maher Eneizat 
@Email: mohammad.eneizat@iu-study.org
@Github: 

The SQLiteBD module performs database functions  
Some of the functions include creating tables, updating tables, connecting to and disconnecting from databases

"""

#external import
from sqlalchemy import create_engine
import pandas as pd


class loading_Data_sqlite:
    """ Class DataAccess is used for loading database  """
    
    def load_train(train):
        
        """load train.csv file data to database"""
        
        
        # Create the db engine for file database 
        train_db= create_engine('sqlite:///train.db')
        
        # Change Table name 
        train.columns = ["X", "Y1 (training func)", 'Y2 (training func)', 'Y3 (training func)', 'Y4 (training func)']
        
        # Load the imported CSV into a database
        train.to_sql('train', train_db,if_exists="replace", index = False)
        
        
    def load_ideal(ideal):
        
        """load ideal.csv file data to database"""
        
        # Create the db engine for file database 
        ideal_db= create_engine('sqlite:///ideal.db')
        
        # Change Table name 
        ideal.columns = ['X','Y1 (ideal func)', 'Y2 (ideal func)','Y3 (ideal func)',
                    'Y4 (ideal func)','Y5 (ideal func)','Y6 (ideal func)', 
                    'Y7 (ideal func)','Y8 (ideal func)','Y9 (ideal func)',
                    'Y10 (ideal func)','Y11 (ideal func)','Y12 (ideal func)',
                    'Y13 (ideal func)','Y14 (ideal func)','Y15 (ideal func)',
                    'Y16 (ideal func)','Y17 (ideal func)','Y18 (ideal func)', 
                    'Y19 (ideal func)','Y20 (ideal func)','Y21 (ideal func)',
                    'Y22 (ideal func)','Y23 (ideal func)','Y24 (ideal func)', 
                    'Y25 (ideal func)', 'Y26 (ideal func)','Y27 (ideal func)',
                    'Y28 (ideal func)','Y29 (ideal func)','Y30 (ideal func)',
                    'Y31 (ideal func)', 'Y32 (ideal func)','Y33 (ideal func)', 
                    'Y34 (ideal func)','Y35 (ideal func)','Y36 (ideal func)',
                    'Y37 (ideal func)','Y38 (ideal func)','Y39 (ideal func)', 
                    'Y40 (ideal func)','Y41 (ideal func)','Y42 (ideal func)',
                    'Y43 (ideal func)','Y44 (ideal func)','Y45 (ideal func)',
                    'Y46 (ideal func)','Y47 (ideal func)','Y48 (ideal func)', 
                    'Y49 (ideal func)','Y50 (ideal func)']
        
        # Load the imported CSV into a database
        ideal.to_sql('train', ideal_db,if_exists="replace", index = False)
        
    
        
    
    def Mapping_data():
        """load ideal.csv file data to database"""
        
        #Load map_table.csv
        map_table_read = pd.read_csv("map_table.csv")
        
        # Create the db engine for file database
        map_db =create_engine('sqlite:///mapping_db.db')
        
        
        # Load the imported CSV into your database
        map_table_read.to_sql('test_db', map_db,if_exists='replace', index = False)    


        
        

        
        
