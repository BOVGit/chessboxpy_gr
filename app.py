import streamlit as st
import requests
import pandas as pd
import streamlit.components.v1 as components

# Функции для работы с рейтингами (оставляем без изменений)
def get_lichess_ratings(username):
    url = f"https://lichess.org/api/user/{username}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            perfs = data.get('perfs', {})
            bullet = perfs.get('bullet', {}).get('rating', 'N/A')
            blitz = perfs.get('blitz', {}).get('rating', 'N/A')
            return {'bullet': bullet, 'blitz': blitz}
        else:
            return {'error': 'Игрок не найден'}
    except Exception as e:
        return {'error': str(e)}

def get_chesscom_ratings(username):
    username = username.lower()
    url = f"https://api.chess.com/pub/player/{username}/stats"
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

# Основная часть приложения
st.title("v1.5 Рейтинги на Lichess и Chess.com")

# Инициализация session_state для хранения реальных значений
if 'real_lichess' not in st.session_state:
    st.session_state.real_lichess = ""
if 'real_chesscom' not in st.session_state:
    st.session_state.real_chesscom = ""

# JavaScript компонент для работы с cookies и синхронизацией
components.html(f"""
<script>
// Функции для работы с cookies
function setCookie(name, value, days) {{
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + encodeURIComponent(value) + ";" + expires + ";path=/";
}}

function getCookie(name) {{
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {{
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }}
    return null;
}}

// Восстанавливаем значения при загрузке и сообщаем Streamlit
window.addEventListener('load', function() {{
    setTimeout(function() {{
        const lichessValue = getCookie('lichess_nicks') || '';
        const chesscomValue = getCookie('chesscom_nicks') || '';

        console.log('Loading cookies:', {{ lichess: lichessValue, chesscom: chesscomValue }});

        // Заполняем поля
        const inputs = parent.document.querySelectorAll('input[type="text"]');
        if (inputs.length >= 2) {{
            if (lichessValue) {{
                inputs[0].value = lichessValue;
            }}
            if (chesscomValue) {{
                inputs[1].value = chesscomValue;
            }}
        }}

        // Сообщаем Streamlit о реальных значениях
        if (lichessValue || chesscomValue) {{
            const message = {{
                lichess: lichessValue,
                chesscom: chesscomValue
            }};
            parent.window.postMessage({{type: 'COOKIE_VALUES', data: message}}, '*');
        }}
    }}, 500);
}});

// Слушаем сообщения от полей ввода
window.addEventListener('message', function(event) {{
    if (event.data.type === 'INPUT_CHANGE') {{
        setCookie('lichess_nicks', event.data.lichess, 30);
        setCookie('chesscom_nicks', event.data.chesscom, 30);
    }}
}});
</script>
""", height=0)

# Слушаем сообщения от JavaScript
def handle_js_messages():
    # Этот код будет выполнен при загрузке для получения значений из cookies
    pass

handle_js_messages()

# Поля ввода, которые синхронизируются с реальными значениями
lichess_nicks = st.text_input(
    "Никнеймы на Lichess (через запятую, если несколько)",
    value=st.session_state.real_lichess,
    key="lichess_input"
)

chesscom_nicks = st.text_input(
    "Никнеймы на Chess.com (через запятую, если несколько)",
    value=st.session_state.real_chesscom,
    key="chesscom_input"
)

# JavaScript для отслеживания изменений в полях ввода
components.html(f"""
<script>
// Отслеживаем изменения в полях ввода
function setupInputListeners() {{
    const inputs = parent.document.querySelectorAll('input[type="text"]');
    if (inputs.length >= 2) {{
        inputs[0].addEventListener('input', function() {{
            updateCookies();
        }});
        inputs[1].addEventListener('input', function() {{
            updateCookies();
        }});
    }}
}}

function updateCookies() {{
    const inputs = parent.document.querySelectorAll('input[type="text"]');
    if (inputs.length >= 2) {{
        const lichessValue = inputs[0].value;
        const chesscomValue = inputs[1].value;

        setCookie('lichess_nicks', lichessValue, 30);
        setCookie('chesscom_nicks', chesscomValue, 30);

        // Сообщаем Streamlit о текущих значениях
        const message = {{
            lichess: lichessValue,
            chesscom: chesscomValue
        }};
        parent.window.postMessage({{type: 'CURRENT_VALUES', data: message}}, '*');
    }}
}}

// Инициализируем слушатели
setupInputListeners();

// Также обновляем при загрузке, если есть значения в полях
const inputs = parent.document.querySelectorAll('input[type="text"]');
if (inputs.length >= 2 && (inputs[0].value || inputs[1].value)) {{
    updateCookies();
}}
</script>
""", height=0)

# Кнопка для запуска - используем реальные значения из полей
if st.button("Получить рейтинги"):
    # Берем значения напрямую из полей ввода
    current_lichess = lichess_nicks
    current_chesscom = chesscom_nicks

    # Сохраняем в session_state
    st.session_state.real_lichess = current_lichess
    st.session_state.real_chesscom = current_chesscom

    # Разбиваем ники на списки
    lichess_list = [nick.strip() for nick in current_lichess.split(',') if nick.strip()]
    chesscom_list = [nick.strip() for nick in current_chesscom.split(',') if nick.strip()]

    # Если списки разной длины — берём минимальную.
    min_len = min(len(lichess_list), len(chesscom_list))
    results = []

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
        df.insert(0, '№', df.index + 1)
        st.dataframe(df, width='stretch', hide_index=True)
    else:
        st.warning("Введите никнеймы для получения данных.")

# Кнопка для очистки
if st.button("Очистить поля"):
    st.session_state.real_lichess = ""
    st.session_state.real_chesscom = ""
    components.html("""
    <script>
    setCookie('lichess_nicks', '', 30);
    setCookie('chesscom_nicks', '', 30);
    console.log('Cookies cleared');
    </script>
    """, height=0)
    st.success("Поля очищены!")
    st.rerun()

# Отладочная информация
st.write("🔧 Отладочная информация:")
st.write(f"Lichess в session_state: '{st.session_state.real_lichess}'")
st.write(f"Chess.com в session_state: '{st.session_state.real_chesscom}'")
st.write(f"Lichess в поле: '{lichess_nicks}'")
st.write(f"Chess.com в поле: '{chesscom_nicks}'")

# CSS стили
st.markdown("""
    <style>
    .stApp {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }

    label {
        color: grey !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }

    input {
        background-color: #3a3a3a !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
        caret-color: #ffffff !important;
    }

    input:focus {
        border-color: #4a7c59 !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(74, 124, 89, 0.3) !important;
    }

    .stButton > button {
        background-color: #4a7c59 !important;
        color: #ffffff !important;
        border: 2px solid #5a8c69 !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 5px !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background-color: #5a8c69 !important;
        border-color: #6a9c79 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
    }

    .stButton > button:active {
        background-color: #3a6c49 !important;
        transform: translateY(0);
    }

    .stButton > button:focus {
        color: #ffffff !important;
        background-color: #4a7c59 !important;
        border-color: #6a9c79 !important;
        box-shadow: 0 0 0 3px rgba(74, 124, 89, 0.3) !important;
    }

    .dataframe {
        background-color: #3a3a3a !important;
        color: #e0e0e0 !important;
    }
    </style>
""", unsafe_allow_html=True)