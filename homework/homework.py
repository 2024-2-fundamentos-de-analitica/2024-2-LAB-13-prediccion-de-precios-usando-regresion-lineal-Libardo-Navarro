import pandas as pd
import gzip
import json
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error,median_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import LinearRegression


path1 = "./files/input/test_data.csv.zip"
path2 = "./files/input/train_data.csv.zip"

test_data = pd.read_csv(
	path1,
	index_col=False,
	compression='zip'
)

train_data = pd.read_csv(
	path2,
	index_col=False,
	compression='zip'
)

current_year = 2021

train_data['Age'] = current_year - train_data['Year']
test_data['Age'] = current_year - test_data['Year']

columns_to_drop = ['Year', 'Car_Name']
train_data = train_data.drop(columns=columns_to_drop)
test_data = test_data.drop(columns=columns_to_drop)

x_train=train_data.drop(columns="Present_Price")
y_train=train_data["Present_Price"]

x_test=test_data.drop(columns="Present_Price")
y_test=test_data["Present_Price"]


categorical_features = ['Fuel_Type', 'Selling_type', 'Transmission']
numerical_features = list(set(x_train.columns) - set(categorical_features))

preprocessor = ColumnTransformer(
	transformers=[
		("num", MinMaxScaler(), numerical_features),
		("cat", OneHotEncoder(), categorical_features)
	],
	remainder="passthrough"
)

k_best = SelectKBest(f_regression, k='all')

model = LinearRegression()

pipeline = Pipeline(
	steps=[
		("preprocessor", preprocessor),
		("k_best", k_best),
		("model", model)
	]
)

param_grid = {
	"k_best__k": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
	"model__fit_intercept": [True, False]
}

grid_search = GridSearchCV(
	pipeline,
	param_grid=param_grid,
	cv=10,
	scoring="neg_mean_absolute_error",
	n_jobs=-1,
	refit=True,
	verbose=1
)

grid_search.fit(x_train, y_train)

with gzip.open("./files/models/model.pkl.gz", 'wb') as f:
	pickle.dump(grid_search, f)
	
metrics = {}

y_train_pred = grid_search.predict(x_train)
y_test_pred = grid_search.predict(x_test)

metrics['train'] = {
    'type': 'metrics',
    'dataset': 'train',
    'r2': r2_score(y_train, y_train_pred),
    'mse': mean_squared_error(y_train, y_train_pred),
    'mad': median_absolute_error(y_train, y_train_pred),
}

metrics['test'] = {
    'type': 'metrics',
    'dataset': 'test',
    'r2': r2_score(y_test, y_test_pred),
    'mse': mean_squared_error(y_test, y_test_pred),
    'mad': median_absolute_error(y_test, y_test_pred),
}


with open("./files/output/metrics.json", 'w') as f:
	f.write(json.dumps(metrics['train'])+'\n')
	f.write(json.dumps(metrics['test'])+'\n')
#
# En este dataset se desea pronosticar el precio de vhiculos usados. El dataset
# original contiene las siguientes columnas:
#
# - Car_Name: Nombre del vehiculo.
# - Year: Año de fabricación.
# - Selling_Price: Precio de venta.
# - Present_Price: Precio actual.
# - Driven_Kms: Kilometraje recorrido.
# - Fuel_type: Tipo de combustible.
# - Selling_Type: Tipo de vendedor.
# - Transmission: Tipo de transmisión.
# - Owner: Número de propietarios.
#
# El dataset ya se encuentra dividido en conjuntos de entrenamiento y prueba
# en la carpeta "files/input/".
#
# Los pasos que debe seguir para la construcción de un modelo de
# pronostico están descritos a continuación.
#
#
# Paso 1.
# Preprocese los datos.
# - Cree la columna 'Age' a partir de la columna 'Year'.
#   Asuma que el año actual es 2021.
# - Elimine las columnas 'Year' y 'Car_Name'.
#
#
# Paso 2.
# Divida los datasets en x_train, y_train, x_test, y_test.
#
#
# Paso 3.
# Cree un pipeline para el modelo de clasificación. Este pipeline debe
# contener las siguientes capas:
# - Transforma las variables categoricas usando el método
#   one-hot-encoding.
# - Escala las variables numéricas al intervalo [0, 1].
# - Selecciona las K mejores entradas.
# - Ajusta un modelo de regresion lineal.
#
#
# Paso 4.
# Optimice los hiperparametros del pipeline usando validación cruzada.
# Use 10 splits para la validación cruzada. Use el error medio absoluto
# para medir el desempeño modelo.
#
#
# Paso 5.
# Guarde el modelo (comprimido con gzip) como "files/models/model.pkl.gz".
# Recuerde que es posible guardar el modelo comprimido usanzo la libreria gzip.
#
#
# Paso 6.
# Calcule las metricas r2, error cuadratico medio, y error absoluto medio
# para los conjuntos de entrenamiento y prueba. Guardelas en el archivo
# files/output/metrics.json. Cada fila del archivo es un diccionario con
# las metricas de un modelo. Este diccionario tiene un campo para indicar
# si es el conjunto de entrenamiento o prueba. Por ejemplo:
#
# {'type': 'metrics', 'dataset': 'train', 'r2': 0.8, 'mse': 0.7, 'mad': 0.9}
# {'type': 'metrics', 'dataset': 'test', 'r2': 0.7, 'mse': 0.6, 'mad': 0.8}
#
