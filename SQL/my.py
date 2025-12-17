import psycopg2
import pandas as pd
# Подключение к базе данных
connection = psycopg2.connect(
    dbname='skillfactory',
    user='skillfactory',
    password='cCkxxLVrDE8EbvjueeMedPKt',
    host='84.201.134.129',
    port=5432
)

# Количество записей
n = 10

# SQL-запрос
query = f'''
SELECT *
FROM sql.pokemon
LIMIT {n};
'''

# Чтение результата запроса в DataFrame Pandas
df = pd.read_sql_query(query, connection)

# Закрытие соединения с базой данных
connection.close()
# Просмотр первых нескольких строк таблицы
print(df.head())
connection.close()