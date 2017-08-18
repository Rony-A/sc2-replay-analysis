from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.ensemble import BaggingClassifier,BaggingRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.decomposition import PCA

params_rfc = {'n_estimators':[100],
  'criterion':['entropy','gini'],
  'max_depth':[None],
  'min_samples_split':[2],
  'min_samples_leaf':[1],
  'min_weight_fraction_leaf':[0.0],
  'max_features':['auto','sqrt','log2',None,0.25,0.5,0.75],
  'max_leaf_nodes':[None],
  'min_impurity_split':[1e-07],
  'bootstrap':[True],
  'oob_score':[False],
  'n_jobs':[1],
  'random_state':[None],
  'verbose':[0],
  'warm_start':[False]}
