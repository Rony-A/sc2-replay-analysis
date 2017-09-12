#Standard Library imports
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#Essential modeling imports
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_predict, cross_val_score
from sklearn.preprocessing import MinMaxScaler, StandardScaler, QuantileTransformer

#Configurations
def common_configs():
    print ("%config InlineBackend.figure_format = 'retina'")
    print("%matplotlib inline")

def common_markdown():
    print ('<right><img src="" style=" margin: 15px; height: 80px"></right>')

#Print Lists in a pretty way

def plist(iterable, col_num = 3, spacing = None, _chars_per_line = 98):
    '''Prints an iterable in a pretty way - python 3'''
    if spacing == None:
        spacing = int(_chars_per_line/col_num)

    list_items = [str(item).ljust(spacing) for item in iterable]

    for i in range(0,len(list_items),col_num):
        [print(list_items[j],end='')
            for j in range(i,i+col_num) if j < len(list_items)]
        print()

#Scales DataFrame
def scale_dataframe(df, method = 'StandardScaler', scaler=None):
    if method == 'StandardScaler':
        if scaler is None:
            scaler = StandardScaler()
            scaler.fit(df)
        return pd.DataFrame(columns=df.columns,data=scaler.transform(df))
        
    elif method == 'MinMaxScaler':
        if scaler is None:
            scaler = MinMaxScaler()
            scaler.fit(df)
        return pd.DataFrame(columns=df.columns,data=scaler.transform(df))
        
    elif method == 'QuantileTransformer':
        if scaler is None:
            scaler = QuantileTransformer(output_distribution='normal')
            scaler.fit(df)
        return pd.DataFrame(columns=df.columns,data=scaler.transform(df))
        
    elif method == 'Mixed':
        df_mixed = df.copy()
        binary = df.applymap(lambda x:
            1 if x ==0 or x == 1
            else np.nan).dropna(how='any',axis = 1).columns
        for col in [col for col in df.columns if col not in binary]:
            std = df[col].std()
            xbar = df[col].std()
            df_mixed[col] = df[col].apply(lambda x:float(x-xbar)/std)
        return df_mixed

# Make a toggle for code visibility
from IPython.core.display import HTML
html_script = '''<script>code_show=true;function code_toggle(){if
    (code_show){$('div.input').hide();}else{$('div.input').show();}
    code_show = !code_show}$(document).ready(code_toggle);</script>
    <form action="javascript:code_toggle()"><input type="submit"
    value="Click here to toggle on/off the raw code."></form>'''

def code_toggle():
    return HTML(html_script.replace('true','false'))

# Mess around with cell width
from IPython.core.display import display, HTML
def cell_width(chars = 80):
    display(HTML("<style>.container { width:"
                 +str(52*chars/80.0)
                 +"% !important; }</style>"))

def extended_type(x):
    if x != x:
        return 'missing'
    else:
        return str(type(x)).split("'")[1]

def explore_types(df, columns = None):
    if columns == None: columns = df.columns
    di = {key:df[key].apply(extended_type).value_counts() for key in columns}
    return pd.DataFrame(columns = columns, data = di).fillna(0)

def plot_types(df, columns = None, figsize = (17,2), xsize = 15):
    _ = plt.clf();
    _ = explore_types(df,columns = columns).T.plot(kind='bar',
                                                   figsize=figsize,
                                                   stacked=True,
                                                   legend=None);

    _ = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102),loc=3,ncol=2,
                   mode="expand", borderaxespad=0.);

    _ = plt.suptitle('Occurence of types in attributes',fontsize=25);
    _ = plt.xticks(fontsize=xsize);
    _ = plt.subplots_adjust(top=0.80);
    _ = plt.show();
    return None
