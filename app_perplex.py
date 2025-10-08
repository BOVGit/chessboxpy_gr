import streamlit as st
import requests
import pandas as pd
import streamlit.components.v1 as components

def get_lichess_ratings(username):
    url = f"https://lichess.org/api/user/{username}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            perfs = data.get('perfs', {})
            bullet = perfs.get('bullet', {}).get('rating', 'NA')
            blitz = perfs.get('blitz', {}).get('rating', 'NA')
            return bullet, blitz
        else:
            return 'error', 'error'
    except Exception:
        return 'error', 'error'

def get_chesscom_ratings(username):
    username = username.lower()
    url = f"https://api.chess.com/pub/player/{username}/stats"
    headers = {"User-Agent": "my-app"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            bullet = data.get('chess_bullet', {}).get('last', {}).get('rating', 'NA')
            blitz = data.get('chess_blitz', {}).get('last', {}).get('rating', 'NA')
            return bullet, blitz
        else:
            return 'error', 'error'
    except Exception:
        return 'error', 'error'

st.title("v1.4 Lichess Chess.com — with localStorage")

html_code = """
<script>
window.onload = function() {
  const lichess = localStorage.getItem('lichess') || '';
  const chesscom = localStorage.getItem('chesscom') || '';
  document.getElementById('lichess').value = lichess;
  document.getElementById('chesscom').value = chesscom;
};

function saveValue(id) {
  const val = document.getElementById(id).value;
  localStorage.setItem(id, val);
  const event = new Event('input', { bubbles: true });
  document.getElementById(id + '_input').dispatchEvent(event);
}
</script>

<label for="lichess">Lichess:</label><br>
<input type="text" id="lichess" oninput="saveValue('lichess')" style="background-color:#3a3a3a;color:#fff;border:1px solid #555;padding:5px;width:300px;margin-bottom:10px;"><br>
<label for="chesscom">Chess.com:</label><br>
<input type="text" id="chesscom" oninput="saveValue('chesscom')" style="background-color:#3a3a3a;color:#fff;border:1px solid #555;padding:5px;width:300px;margin-bottom:10px;">
"""

components.html(html_code, height=140)

lichess_input = st.text_input("Lichess (синхр. с localStorage):", key="lichess_input", value="")
chesscom_input = st.text_input("Chess.com (синхр. с localStorage):", key="chesscom_input", value="")

if st.button("Получить рейтинги"):
    lichess_list = [nick.strip() for nick in lichess_input.split(',') if nick.strip()]
    chesscom_list = [nick.strip() for nick in chesscom_input.split(',') if nick.strip()]
    min_len = min(len(lichess_list), len(chesscom_list))

    results = []
    for i in range(min_len):
        l_user = lichess_list[i]
        c_user = chesscom_list[i]
        l_bullet, l_blitz = get_lichess_ratings(l_user)
        c_bullet, c_blitz = get_chesscom_ratings(c_user)
        results.append({
            "Lichess": l_user,
            "Chess.com": c_user,
            "Lichess Bullet": l_bullet,
            "Lichess Blitz": l_blitz,
            "Chess.com Bullet": c_bullet,
            "Chess.com Blitz": c_blitz
        })

    if results:
        df = pd.DataFrame(results)
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Введите никнеймы в обоих полях через запятую.")
