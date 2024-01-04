import streamlit as st
from openai import OpenAI
from datetime import timedelta
import datetime

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

st.set_page_config(
    # 사이드바 숨김
    initial_sidebar_state="collapsed"
)

# 사용자가 토글을 조절할 수 있는 다크모드 체크 박스 생성
dark_mode = st.toggle("🌙")

# 다크 모드가 활성화되었다면, 테마를 "dark"로 설정
if dark_mode:
    st.set_theme("dark")

st.title("🐉 청룡신이 알려주는 오늘의 띠별 운세")
st.subheader("오늘의 운세를 동물띠로 확인해보세요.")
st.info("띠별 운세를 확인하기 위해서는 태어난 연도와 정확한 동물띠가 필요합니다. 정확히 선택하시고 운세를 확인해주세요.")
st.info("띠별 운세는 1948년 이후 출생자를 대상으로 합니다(2024년 기준).")

auto_complete = st.toggle(label="예시로 설정하기")
example = {
    "name": "홍길동",
    "birth": datetime.datetime(1948, 1, 1),
}

# 내일 날짜 가져오기
tomorrow_date = (datetime.datetime.now() + timedelta(days=1)).date()
tomorrow = st.toggle(label="내일 운세 미리보기")
if tomorrow:
    st.write(f"{tomorrow_date.month}월 {tomorrow_date.day}일 동물띠 운세를 미리 확인해보세요!")
else:
    st.write(f"오늘의 동물띠 운세를 확인해보세요!")


# prompt
def generate_prompt(year, gender, name, t_year, t_month, t_day, animal, min_length, max_length):
    prompt = f"""
{t_year}년 {t_month}월 {t_day}일의 {year}년에 태어난 {animal}띠 운세를 0부터 100까지 중에서 하나의 숫자로 표현해주세요. 0에 가까울수록 오늘의 운세가 안 좋음을 나타내고, 100에 가까울수록 오늘의 운세가 좋음을 나타냅니다. 
반드시 ({t_year}년 {t_month}월 {t_day}일 {animal}띠 점수: 숫자) 형태로 나타내주세요.
숫자는 굵은 글씨로 표현해주세요. 
동물띠 운세는 {year}만 가지고 운세를 풀이해주세요.
만약 숫자가 50점 이하라면 🔅, 50점 이상이라면 🔆를 반드시 점수 오른쪽에 붙여주세요.
{year}년에 태어난 {gender}성 {name} 님의 {t_year}년 {t_month}월 {t_day}일의 {animal}띠 운세에 대해 자세히 설명해주세요.
반드시 {min_length} 단어 이상, {max_length} 단어 이내로 설명해주세요.
{t_year}년 {t_month}월 {t_day}일이 {year}년에 태어난 {animal}띠에게 어떤 날인지 간단히 설명하고 그에 대한 자세한 설명을 덧붙여주세요.
{t_year}년 {t_month}월 {t_day}일 하루동안 어떤 일을 조심해야하는지, 어떤 사람을 피해야하는지도 설명해주세요.
이모지를 적절히 섞어 설명해주세요.
---
연도: {year}
동물띠: {animal}
---
    """.strip()
    return prompt 

def request_chat_completion(prompt):
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "당신은 한평생 명리학만 공부해온 명리학 전문가입니다."}, 
            {"role": "user", "content": prompt}
        ],
        stream = True
    )
    # print_streaming_response(response)
    return response

# 스트리밍 방식으로 화면에 보여주기
def print_streaming_response(response):
    message = ""
    placeholder = st.empty()
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            message += delta.content
            placeholder.markdown(message + "▌")
    placeholder.markdown(message)


# 폼 생성
# 이름, 태어난 연도, 동물띠, 확인 날짜(오늘 or 내일)
with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "성명(필수)",
            value=example["name"] if auto_complete else "",
            placeholder=example["name"]
        )
    with col2:
        # 성별
        gender = st.radio(
            "성별(필수)",
            ["남", "여"]
        )
    col1, col2, col3 = st.columns(3)
    with col1:
        # 양력/음력
        moon = st.radio(
            "양/음력(필수)",
            ["양력", "음력-평달", "음력-윤달"]
        )
    with col2:
        birth = st.date_input(
            "생년월일(필수)",
            min_value=datetime.datetime(1900, 1, 1),
            max_value=datetime.datetime(2024, 1, 1),
            value=example["birth"] if auto_complete else None
        )
    with col3:
        date = st.date_input(
            "확인 날짜",
            min_value=datetime.datetime.now(),
            value=tomorrow_date if tomorrow else "today",
        )
    
    animal = st.selectbox(
        "동물띠 선택",
        ("쥐🐭", "소🐮", "호랑이🐯", "토끼🐰", "용🐲", "뱀🐍", "말🐴", 
         "양🐑", "원숭이🐵", "닭🐔", "개🐶", "돼지🐷"),
        index=0
    )
    submit = st.form_submit_button("확인하기")

if submit:
    if not name:
        st.error("이름을 입력해주세요.")
    elif not birth:
        st.error("생년월일을 입력해주세요.")
    else:
        # st.success(f"{name} 님의 오늘의 {animal}띠 운세 확인중...")
        
        year = birth.year
        t_year = date.year
        t_month = date.month
        t_day = date.day
        # prompt 생성
        prompt = generate_prompt(
            year=year,
            gender=gender,
            name=name,
            t_year=t_year,
            t_month=t_month,
            t_day=t_day,
            animal=animal[:-1],
            min_length=80,
            max_length=150
        )
        st.write(f"**{name} 님의 {t_year}년 {t_month}월 {t_day}일의 {animal}띠 운세 확인 중...**")
        st.divider()
        response = request_chat_completion(prompt)
        print_streaming_response(response)







