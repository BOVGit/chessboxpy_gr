import streamlit as st  # Импорт Streamlit для создания веб-интерфейса. Это основная библиотека.
import requests  # Для отправки запросов к API (получения данных с серверов).
import pandas as pd  # Для создания таблицы из данных — удобно отображать в Streamlit.
import json  # Для работы с JSON-данными из API.

# Функция для получения рейтингов с Lichess.
# Принимает никнейм, возвращает словарь с рейтингами или ошибку.
def get_lichess_ratings(username):
    url = f"https://lichess.org/api/user/{username}"  # API-эндпоинт для Lichess.
    try:
        response = requests.get(url)  # Отправляем GET-запрос.
        if response.status_code == 200:  # Если ответ успешный (200 — OK).
            data = response.json()  # Преобразуем ответ в JSON.
            perfs = data.get('perfs', {})  # Берём раздел "perfs" (рейтинги).
            bullet = perfs.get('bullet', {}).get('rating', 'N/A')  # Рейтинг пули.
            blitz = perfs.get('blitz', {}).get('rating', 'N/A')  # Рейтинг блица.
            return {'bullet': bullet, 'blitz': blitz}  # Возвращаем словарь.
        else:
            return {'error': 'Игрок не найден'}  # Если ошибка — возвращаем сообщение.
    except Exception as e:  # Если что-то сломалось (например, нет интернета).
        return {'error': str(e)}  # Возвращаем текст ошибки.

# Функция для получения рейтингов с Chess.com.
# Аналогично Lichess, но другой эндпоинт и структура JSON.
def get_chesscom_ratings(username):
    username = username.lower()  # Добавь эту строку: приводим ник к нижнему регистру.
    url = f"https://api.chess.com/pub/player/{username}/stats"  # Теперь URL всегда с lowercase.
    try:
        # response = requests.get(url)
        response = requests.get(url, headers={'User-Agent': 'my-app'})
        if response.status_code == 200:
            data = response.json()
            bullet = data.get('chess_bullet', {}).get('last', {}).get('rating', 'N/A')
            blitz = data.get('chess_blitz', {}).get('last', {}).get('rating', 'N/A')
            return {'bullet': bullet, 'blitz': blitz}
        else:
            return {'error': 'Игрок не найден'}
    except Exception as e:
        return {'error': str(e)}

# Основная часть приложения в Streamlit.
st.title("Шахматные рейтинги с Lichess и Chess.com")  # Заголовок страницы.

# CSS для тёмной темы — чтобы дизайн был привлекательным.
# Вставляем через markdown (unsafe_allow_html=True позволяет HTML/CSS).
st.markdown("""
    <style>
    .stApp { background-color: #1a1a1a; color: white; }  /* Тёмный фон, белый текст. */
    input { background-color: #333; color: white; }  /* Поля ввода тёмные. */
    button { background-color: #556b2f; color: white; }  /* Кнопка зелёная (шахматный стиль). */
    </style>
""", unsafe_allow_html=True)

# НОВОЕ: Инициализируем session_state для ников, если их нет.
# Это как проверка: если ключа нет в словаре, добавляем пустую строку.
if 'lichess_nicks' not in st.session_state:
    st.session_state['lichess_nicks'] = ""
if 'chesscom_nicks' not in st.session_state:
    st.session_state['chesscom_nicks'] = ""

# Форма для ввода никнеймов.
# НОВОЕ: value берём из session_state — так ники сохраняются автоматически.
lichess_nicks = st.text_input("Никнеймы на Lichess (через запятую, если несколько)", value=st.session_state['lichess_nicks'])
chesscom_nicks = st.text_input("Никнеймы на Chess.com (через запятую, если несколько)", value=st.session_state['chesscom_nicks'])

# Кнопка для запуска.
if st.button("Получить рейтинги"):
    # НОВОЕ: Сохраняем введённые ники в session_state.
    # Это обновляет значения — теперь они останутся при перезагрузке.
    st.session_state['lichess_nicks'] = lichess_nicks
    st.session_state['chesscom_nicks'] = chesscom_nicks

    # Разбиваем ники на списки (удаляем пробелы).
    lichess_list = [nick.strip() for nick in lichess_nicks.split(',') if nick.strip()]
    chesscom_list = [nick.strip() for nick in chesscom_nicks.split(',') if nick.strip()]

    # Если списки разной длины — берём минимальную.
    min_len = min(len(lichess_list), len(chesscom_list))
    results = []

    # Цикл по игрокам (предполагаем пары: первый Lichess с первым Chess.com и т.д.).
    for i in range(min_len):
        lichess_user = lichess_list[i]
        chesscom_user = chesscom_list[i]

        lichess_ratings = get_lichess_ratings(lichess_user)
        chesscom_ratings = get_chesscom_ratings(chesscom_user)

        row = {
            'Игрок (Lichess / Chess.com)': f"{lichess_user} / {chesscom_user}",
            'Lichess Bullet': lichess_ratings.get('bullet', lichess_ratings.get('error', 'Ошибка')),
            'Lichess Blitz': lichess_ratings.get('blitz', lichess_ratings.get('error', 'Ошибка')),
            'Chess.com Bullet': chesscom_ratings.get('bullet', chesscom_ratings.get('error', 'Ошибка')),
            'Chess.com Blitz': chesscom_ratings.get('blitz', chesscom_ratings.get('error', 'Ошибка'))
        }
        results.append(row)

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.write("Введите никнеймы для получения данных.")
