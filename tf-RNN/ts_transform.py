
# DO NOT EDIT THIS FILE - GENERATED FROM 02_ts_utils.ipynb

import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import pickle

'''
    Utility that is derived from Column transformer to do inverse_transform

USAGE:
    Easiest way to use it:

        df = pd.read_csv("../data/processminer-rare-event-mts.csv.zip", sep=";")
        scaler, df2 = myColumnTransformer.scale_df(df1)

    Use it scale other data: 

        scaler.fit(df1)

'''
class myColumnTransformer(ColumnTransformer):
    def out_feature_names(self):

        if( not self.verbose_feature_names_out ):
            return self.get_feature_names_out()
        else:
            # Note Below is only valid if scaler is called without 'verbose_feature_names_out'
            out_feats = []
            for s,v in self.named_transformers_.items():
                if ( type(v) == str):       # Problem arises when dont drop remainders
                    out_feats.extend([v])
                    continue

                out_feats.extend(v.get_feature_names_out())

            return  out_feats

    def transform(self, df, returnDF=True):
        ret = super().transform(df)
        rdf = None
        if (returnDF):
            ret = pd.DataFrame(ret, columns= self.out_feature_names())

        return ret


    def inverse_transform(self, sdf, inplace=False):
        ret = sdf if (inplace) else pd.DataFrame()

        for s,v in self.named_transformers_.items():
            if (not hasattr(v, "inverse_transform")):
                continue;
            
            fo = v.get_feature_names_out()
            #print(f"Inverting {fo} => {v.feature_names_in_} {set(fo).issubset(sdf.columns)} ")
            if (not set(fo).issubset(sdf.columns)):
                continue;
            ret[v.feature_names_in_] = v.inverse_transform(sdf[fo])

        return ret

    def save(self, file="my", ext=".scaler.pkl"):
        pickle.dump(self, open(f'{file}.scaler.pkl', 'wb'))

    def load(self, file="my", ext=".scaler.pkl"):
        ret = pickle.load( open(f'{file}.scaler.pkl', 'rb'))
        return ret


    '''
        Finds numeric and categorical columns from DF.
        It returns empty lists if there are no columns matching the criteria.
        For ex: if there are no categorical variables, it returns empty list in categori.
    '''
    @staticmethod
    def find_cat_numerics_names(df, num_unique=5):
        unique = df.nunique()
        numerics = unique[unique  >  num_unique].index.to_list()
        numerics = [ i for i in numerics if is_numeric_dtype(df[i]) ]
        categori = unique[unique <= num_unique].index.to_list()

        return numerics, categori

    '''
        Scale data frame
    '''
    @staticmethod
    def scale_df(df, num_unique=5, numericScaler= StandardScaler, numerics = None, categorical = None):
        # Detect numerics if both not given; if one is given - we assume other is not required
        if ( numerics is None and categorical is None):
            numerics, categorical = myColumnTransformer.find_cat_numerics_names(df, num_unique)

        scaler = myColumnTransformer( transformers= 
                [(n  ,  numericScaler(), [n] ) for n in numerics] +
                [("categorical",  OneHotEncoder(sparse=False, handle_unknown="ignore"), categorical)]
            , remainder='drop',
            verbose_feature_names_out = False)

        x = scaler.fit_transform(df)
        scaler.numerics = numerics
        scaler.categorical = categorical

        return scaler, pd.DataFrame(x, columns= scaler.out_feature_names())





'''
    Here is a test and how to use it.
'''
def testMyColumnTransformer():
    df = pd.read_csv("../data/processminer-rare-event-mts.csv.zip", sep=";")
    nums, cats = myColumnTransformer.find_cat_numerics_names(df, 5)

    # Lets take and example of first 5 columsn and cats columns for our test
    # Eliminate first column because it is a time column
    #
    df1 = df[nums[1:5]+cats]
    display(df1[0:4])
    '''
        time       x1	       x2         x3	       x4          x5       y  x61
    --------------- -------     ---------   --------    --------    ---------   -  ---
    0	5/1/99 0:00	0.376665	-4.596435	-4.095756	13.497687	-0.118830	0	0
    1	5/1/99 0:02	0.475720	-4.542502	-4.018359	16.230659	-0.128733	0	0
    2	5/1/99 0:04	0.363848	-4.681394	-4.353147	14.127997	-0.138636	0	0
    3	5/1/99 0:06	0.301590	-4.758934	-4.023612	13.161566	-0.148142	0	0
    4	5/1/99 0:08	0.265578	-4.749928	-4.333150	15.267340	-0.155314	0	0
    '''

    scaler, df2 = myColumnTransformer.scale_df(df1)
    print("\nScaled Dataframe:")
    display(df2[0:4])


    # Now you can use scaler to scale other data - 
    # it will do the job as long as there are columns in dataframe matching i/p columns
    # It correctly returns the columns in correct order as original order 
    #
    # You can call transform set returnDF to False to get raw numpy
    #
    print("\nOut of order columns still work correctly:")
    df3 = scaler.transform(df[df.columns[::-1]], True)
    display(df3[0:4])


    # It throwns an error if the expected column is not in the dataframe
    # 
    cols = "x1 x2 x3 x4 x7 y x61"
    try:
        df3 = pd.DataFrame(scaler.transform(df[cols]), columns= scaler.out_feature_names())
    except Exception as e:
        print (f"+++ EXCEPTION IS CORRECT KeyError  missing 'x5' {e} {type(e)}")

    print("\nInverse dataframe correctly inverts it:")
    idf = scaler.inverse_transform(df3)
    display(idf[0:4])

    print('''\nInverse dataframe correctly inverts it: 
    Does it do it if columns or out of order?
    => It DOES!!! See below
    ''')
    odf = df3[df3.columns[::-1]]
    display(odf[0:4])
    idf = scaler.inverse_transform(odf)
    display(idf[0:4])


#testMyColumnTransformer()