import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import pytz

# определение начала недели
start_of_week = datetime.now(pytz.timezone('Asia/Yekaterinburg')) - timedelta(days=datetime.now(pytz.timezone('Asia/Yekaterinburg')).weekday())
start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

# Создание соединения с базой данных SQLite
conn = sqlite3.connect('pull_ups_data.db')
c = conn.cursor()
# Создание веб-страницы с полем для ввода
input_count = st.text_input("Введите количество подтягиваний")
if input_count:
    # Запись в базу данных
    c.execute("INSERT INTO pull_ups (date, count) VALUES (?, ?)", (datetime.now(pytz.timezone('Asia/Yekaterinburg')),
                                                                   int(input_count)))
    conn.commit()
# Получение данных из базы данных за последнюю неделю и подготовка их для графика
df_fact = pd.read_sql_query("SELECT * FROM pull_ups WHERE date >= ? ORDER BY date", conn, params=(start_of_week,))
conn.close()
fact_y = df_fact['count'].cumsum().tolist()
fact_x = df_fact['date'].tolist()
fact_x = pd.to_datetime(fact_x)
# Подготовка данных плана для графика
number = 168
df_plan = pd.DataFrame(pd.date_range(start_of_week,periods=8, freq='24H'), columns=['date'])
df_plan['plan_x'] = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС', 'ПН']
df_plan['plan_y'] = [round(number / 7) * i for i in range(7)] + [number]
df_plan['date'] = pd.to_datetime(df_plan['date'])
# определение цвета графика
last_date = df_plan['date'].max()
last_plan = df_plan.loc[df_plan['date'] == last_date, 'plan_y'].values[0]
seconds_since_last_date = (datetime.now(pytz.timezone('Asia/Yekaterinburg')) - start_of_week).total_seconds()
increment_per_second = last_plan / (last_date - df_plan['date'].min()).total_seconds()
current_plan = increment_per_second * seconds_since_last_date
if len(fact_y) > 0:
    if fact_y[-1] > number:
        color = 'g'
    elif fact_y[-1] > current_plan:
        color = 'blue'
    else:
        color = 'red'
else:
    color = 'g'
# Построение графика
plt.figure(figsize=(10, 6))
plt.plot(df_plan['date'], df_plan['plan_y'], marker='o', linestyle='--', color='grey')
plt.plot(fact_x, fact_y, marker='s', linestyle='-', color=color)
plt.xticks(df_plan['date'], df_plan['plan_x'])
plt.title('Количество подтягиваний за эту неделю')
st.pyplot(plt)
