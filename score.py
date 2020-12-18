import pandas as pd
import numpy as np
import seaborn as sns
import math
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf



# Create % Columns to be able to compare with OMS
def add_perc_column(nutrient, df) : 
    
    # Name of energy column 
    energy = 'energy_' + nutrient  
    
    # Name of new column 
    name = 'perc_' + nutrient
    
    # Create new column 
    df.loc[:,name] = df.loc[:, energy] / df.energy_tot
    
    
    
    
# Get the outliers 
def get_outliers(nutrient, std_treshold, df) : 
    
    '''
    Imput : tresh ( treshold on standard dev  ) 
    Nutrient - string 
    OMS_recom - dict 
    df - dataframe 
    '''     
    
    # Name of column 
    energy = 'energy_' + nutrient
    
    # Mean and std across areas 
    mean_nutrient = df[energy].describe()[1]
    std_nutrient = df[energy].describe()[2]  
    
    outliers_left = df[energy].apply(lambda x: x < (mean_nutrient - std_treshold * std_nutrient))
    outliers_right = df[energy].apply(lambda x: x > (mean_nutrient + std_treshold * std_nutrient))
    
    return outliers_left, outliers_right


# Outliers needs to have a score as well 

def assign_outliers_score(nutrient, OMS_recom, df) : 
    
    '''
    recom_type 
    'less' : when the recomandation is to eat less of that nutrient 
    'more' : when the recomandation is to eat more of that nutrient  
    '''
    # Define outlier treshold
    std_treshold = 2
    
    # Creating array of scores 
    name = nutrient + '_omsScore'
    energy = 'energy_' + nutrient
    perc_col = 'perc_' + nutrient
    df.loc[:, name] = -1 
    
    # Get outliers
    outliers_left, outliers_right = get_outliers(nutrient, std_treshold, df)
    
    # Transform nutrient energy into %
    perc_left  = df.loc[outliers_left,  energy] / df.loc[outliers_left,  'energy_tot']
    perc_right = df.loc[outliers_right, energy] / df.loc[outliers_right, 'energy_tot']
    
    if OMS_recom[0] == 'less_than' :
        df.loc[outliers_left,  name] = perc_left.apply(lambda x : 0 if x < OMS_recom[1] else -1)
        df.loc[outliers_right, name] = 1
        
    elif OMS_recom[0] == 'more_than' :
        df.loc[outliers_right, name] = perc_right.apply(lambda x : 0 if x > OMS_recom[1] else -1)
        df.loc[outliers_left,  name] = 1 
        
    elif OMS_recom[0] == 'around' :
        
        # Min and Max amongst non-outliers areas  
        outliers = outliers_left | outliers_right
        mini = df.loc[~outliers, perc_col].describe()[3]
        maxi = df.loc[~outliers, perc_col].describe()[7]
        
        # Define what is the worst case 
        worst_case = max(abs(OMS_recom[1]-mini), abs(OMS_recom[1]-maxi))   
        df.loc[outliers, name] = perc_right.apply(lambda x : 1 if abs(x-OMS_recom[1]) > worst_case else -1)
        
        
        
def set_scores(nutrient, OMS_val, df) : 
    
    '''
    Imput : x ( pourcentage ) 
    Nutrient - string 
    OMS_recom - dict 
    df - dataframe 
    '''
    
    # Outliers treshhold 
    tresh = 2
    
    # Names of columns 
    energy = 'energy_' + nutrient
    oms_score_col = nutrient + '_omsScore'
    minmax_col = nutrient + '_minmax'
    perc_col = 'perc_' + nutrient
    
    # Get outliers 
    outliers_left, outliers_right = get_outliers(nutrient, tresh, df)
    outliers = outliers_left | outliers_right

    # Get min max after removing outliers 
    mean = df.loc[~outliers, perc_col].describe()[1]
    mini = df.loc[~outliers, perc_col].describe()[3]
    maxi = df.loc[~outliers, perc_col].describe()[7]    
    
    # Depasse les recom 
    if(mini>OMS_val) : 
        df.loc[~outliers, oms_score_col] = df.loc[~outliers, perc_col].apply(lambda x : (x-OMS_val)/(maxi-OMS_val))
        df.loc[outliers, oms_score_col]  = df.loc[outliers,  perc_col].apply(lambda x : (x-OMS_val)/(maxi-OMS_val) 
                                                                             if (x>OMS_val and x<mini) else x)
    # En dessous des recom 
    elif(maxi<OMS_val) : 
        df.loc[~outliers, oms_score_col] = df.loc[~outliers, perc_col].apply(lambda x : (OMS_val-x)/(OMS_val-mini))
        df.loc[outliers,  oms_score_col] = df.loc[outliers,  perc_col].apply(lambda x : (OMS_val-x)/(OMS_val-mini) 
                                                                             if (x<OMS_val and x>maxi) else x)
    # Recom 
    elif(maxi>OMS_val and mini<OMS_val) :
        worst_case = max(abs(OMS_val-mini), abs(OMS_val-maxi)) 
        
        df.loc[~outliers, oms_score_col] = df.loc[~outliers, perc_col].apply(lambda x : abs(OMS_val-x)/worst_case)      
        df.loc[outliers,  oms_score_col] = df.loc[outliers,  perc_col].apply(lambda x : abs(OMS_val-x)/worst_case 
                                                                             if abs(x-OMS_val) < worst_case else x)   

        
        

    
    

    

    
