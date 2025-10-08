import streamlit as st
import pandas as pd
import numpy as np

# --- 1. Конфигурация страницы (Запускается первым) ---
st.set_page_config(
    page_title="Минималистичный Дэшборд",
    layout="wide"  # Делаем макет широким для лучшего отображения
)

# --- 2. Условные данные-константы (Фиктивные данные) ---

DATA = {
    'Месяц': ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн'],
    'Продажи ($)': [1500, 2200, 1800, 3100, 2500, 3800],
    'Клиенты': [15, 25, 20, 35, 30, 42]
}
df = pd.DataFrame(DATA)

# --- 3. Заголовок и ввод (Имитация интерактивности) ---

st.title("📊 Аналитика Продаж (Прототип)")
st.subheader("Обзор ключевых показателей")

# Имитация простого фильтра (но без реальной фильтрации данных)
time_frame = st.selectbox(
    "Выберите период:",
    ['Последние 6 месяцев', 'Последние 3 месяца', 'Весь год'],
    index=0
)

st.info(f"Отображаются данные за: **{time_frame}**")
st.markdown("---")


# --- 4. Основные метрики (Карточки KPI) ---

# Вычисление условных метрик
total_sales = df['Продажи ($)'].sum()
avg_sales = df['Продажи ($)'].mean()
total_clients = df['Клиенты'].sum()

# Разделение макета на 3 колонки
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Общий доход", value=f"${total_sales:,}", delta="15%")

with col2:
    st.metric(label="Средний чек", value=f"${avg_sales:,.2f}", delta="-2.5%")

with col3:
    st.metric(label="Новых клиентов", value=f"{total_clients}", delta="7")

st.markdown("---")

# --- 5. Визуализация и Таблица ---

st.header("Динамика и детальные данные")

# 1. График (Динамика продаж)
st.line_chart(df.set_index('Месяц')['Продажи ($)'])

# 2. Таблица с данными
st.subheader("Сводная таблица")
st.dataframe(df, use_container_width=True)

# 3. Дополнительный виджет (Просто для демонстрации)
st.sidebar.header("Панель настроек")
st.sidebar.slider("Уровень детализации", 0, 100, 50)
