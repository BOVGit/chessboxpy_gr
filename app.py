import streamlit as st
import requests
import pandas as pd  # Для создания таблицы из данных — удобно отображать в Streamlit.
import json
import os

# Функция для загрузки никнеймов из файла
def load_nicknames():
    try:
        if os.path.exists('nicknames.json'):
            with open('nicknames.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('lichess', ''), data.get('chesscom', '')
    except Exception as e:
        st.error(f"Ошибка загрузки никнеймов: {e}")
    return '', ''

# Функция для сохранения никнеймов в файл
def save_nicknames(lichess, chesscom):
    try:
        with open('nicknames.json', 'w', encoding='utf-8') as f:
            json.dump({'lichess': lichess, 'chesscom': chesscom}, f, ensure_ascii=False)
    except Exception as e:
        st.error(f"Ошибка сохранения никнеймов: {e}")

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
    username = username.lower()
    url = f"https://api.chess.com/pub/player/{username}/stats"  # URL всегда с lowercase.
    try:
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
st.title("Рейтинги на Lichess и Chess.com")  # Заголовок страницы.

# CSS для тёмной темы с исправленной кнопкой
st.markdown("""
    <style>
    /* Основной фон и текст */
    .stApp {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }

    /* ВАЖНО: Label'ы для текстовых полей */
    label {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }

    /* Поля ввода */
    input {
        background-color: #3a3a3a !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
        caret-color: #ffffff !important;  /* Цвет курсора */
    }

    /* Поля ввода в фокусе */
    input:focus {
        border-color: #4a7c59 !important;  /* Зелёная рамка при фокусе */
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(74, 124, 89, 0.3) !important;
    }

    /* Стилизация кнопки */
    .stButton > button {
        background-color: #4a7c59 !important;  /* Зелёный шахматный цвет */
        color: #ffffff !important;  /* Белый текст */
        border: 2px solid #5a8c69 !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 5px !important;
        transition: all 0.3s ease !important;
    }

    /* Кнопка при наведении */
    .stButton > button:hover {
        background-color: #5a8c69 !important;
        border-color: #6a9c79 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
    }

    /* Кнопка при нажатии */
    .stButton > button:active {
        background-color: #3a6c49 !important;
        transform: translateY(0);
    }

    /* Кнопка в фокусе */
    .stButton > button:focus {
        color: #ffffff !important;  /* Текст всегда белый */
        background-color: #4a7c59 !important;
        border-color: #6a9c79 !important;
        box-shadow: 0 0 0 3px rgba(74, 124, 89, 0.3) !important;
    }

    /* Таблица */
    .dataframe {
        background-color: #3a3a3a !important;
        color: #e0e0e0 !important;
    }
    </style>

    <script>
    // Автофокус на первое поле при загрузке страницы
    window.addEventListener('load', function() {
        setTimeout(function() {
            const inputs = parent.document.querySelectorAll('input[type="text"]');
            if (inputs.length > 0) {
                inputs[0].focus();
            }
        }, 100);
    });

    // Обработка нажатия Enter для submit формы
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            const button = parent.document.querySelector('.stButton > button');
            if (button) {
                button.click();
            }
        }
    });
    </script>
""", unsafe_allow_html=True)

# Инициализируем session_state для ников, если их нет.
# Это обеспечивает сохранение данных между перезагрузками страницы.
if 'lichess_nicks' not in st.session_state:
    # Загружаем из файла при первом запуске
    lichess_saved, chesscom_saved = load_nicknames()
    st.session_state['lichess_nicks'] = lichess_saved
    st.session_state['chesscom_nicks'] = chesscom_saved
if 'chesscom_nicks' not in st.session_state:
    st.session_state['chesscom_nicks'] = ""

# Форма для ввода никнеймов с использованием on_change для автосохранения
def save_lichess():
    st.session_state['lichess_nicks'] = st.session_state['lichess_input']
    # Сохраняем в файл
    save_nicknames(st.session_state['lichess_nicks'], st.session_state['chesscom_nicks'])

def save_chesscom():
    st.session_state['chesscom_nicks'] = st.session_state['chesscom_input']
    # Сохраняем в файл
    save_nicknames(st.session_state['lichess_nicks'], st.session_state['chesscom_nicks'])

lichess_nicks = st.text_input(
    "Никнеймы на Lichess (через запятую, если несколько)",
    value=st.session_state['lichess_nicks'],
    key='lichess_input',
    on_change=save_lichess
)

chesscom_nicks = st.text_input(
    "Никнеймы на Chess.com (через запятую, если несколько)",
    value=st.session_state['chesscom_nicks'],
    key='chesscom_input',
    on_change=save_chesscom
)

# Кнопка для запуска.
if st.button("Получить рейтинги"):
    # Сохраняем введённые ники в session_state и файл.
    st.session_state['lichess_nicks'] = lichess_nicks
    st.session_state['chesscom_nicks'] = chesscom_nicks
    save_nicknames(lichess_nicks, chesscom_nicks)

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
        st.dataframe(df, width='stretch')
    else:
        st.warning("Введите никнеймы для получения данных.")