import streamlit as st
from openai import OpenAI
from datetime import timedelta
import datetime
import time

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
    
st.title("🐉 청룡신이 알려주는 오늘의 운세")
st.subheader("🔮AI를 이용하여 오늘의 운세를 점쳐보세요🔮")
st.info("운세를 보기 위해선 기본 정보가 꼭! 필요합니다. 운세결과에 중요한 영향을 미치니 정확히 입력해주세요!")
st.info("태어난 시간 입력은 선택이지만 입력했을 때와 안 했을 때 결과가 달라질 수 있으니 되도록 입력하는 것을 권장합니다. (24시간 기준으로 입력해주세요)")

# 예시로 설정
auto_complete = st.toggle(label="예시로 설정하기")
example = {
    "name": "홍길동",
    "birth": datetime.datetime(1900, 1, 1),
    "time": datetime.time(0,00),
}

# 내일 날짜 가져오기
tomorrow_date = (datetime.datetime.now() + timedelta(days=1)).date()
tomorrow = st.toggle(label="내일 운세 미리보기")
if tomorrow:
    st.write(f"{tomorrow_date.month}월 {tomorrow_date.day}일 운세를 미리 확인해보세요!")
else:
    st.write(f"오늘의 운세를 확인해보세요!")


# 태어난 시간을 아는 사람 
def generate_prompt_birth(moon, year, month, day, hour, minute, gender, name, t_year, t_month, t_day, want, min_length, max_length):
    prompt = f"""
{t_year}년 {t_month}월 {t_day}일의 {want} 운세를 0부터 100까지 중에서 하나의 숫자로 표현해주세요. 0에 가까울수록 오늘의 운세가 안 좋음을 나타내고, 100에 가까울수록 오늘의 운세가 좋음을 나타냅니다. 
반드시 ({t_year}년 {t_month}월 {t_day}일 {want} 점수: 숫자) 형태로 나타내주세요.
숫자는 굵은 글씨로 표현해주세요. 
만약 숫자가 50점 이하라면 🔅, 50점 이상이라면 🔆를 반드시 점수 오른쪽에 붙여주세요.
{moon} {year}년 {month}월 {day}일 {hour}시 {minute}분에 태어난 {gender}성 {name} 님의 {t_year}년 {t_month}월 {t_day}일의 {want} 운세에 대해 설명해주세요.
반드시 {min_length} 단어 이상, {max_length} 단어 이내로 설명해주세요.
오늘이 어떤 날인지 간단히 설명하고 그에 대한 자세한 설명을 덧붙여주세요.
오늘 하루동안 어떤 일을 조심해야하는지, 어떤 사람을 피해야하는지도 설명해주세요.
만약 {want}가 "행운 상승"이라면 마지막에 행운의 색상 2가지, 행운의 숫자 2개, 행운의 방향 1곳을 알려주세요. {want}가 "행운 상승🍀📈"이 아니라면 행운의 색상, 행운의 숫자, 행운의 방향은 알려주지 않아도 됩니다.
행운의 색상을 알려줄 때에는 색상 이름 오른쪽에 색깔 이모지를 넣어서 알려주세요.
행운의 숫자는 0부터 9까지의 수이고, 행운의 방향은 동, 서, 남, 북 중 하나입니다.
이모지를 적절히 섞어 설명해주세요.
---
연도: {year}
월: {month}
일: {day}
시간: {hour}
분: {minute}
---
    """.strip()
    return prompt
    
# 태어난 시간을 모르는 사람 
def generate_prompt(moon, year, month, day, gender, name, t_year, t_month, t_day, want, min_length, max_length):
    prompt = f"""
{t_year}년 {t_month}월 {t_day}일의 {want} 운세를 0부터 100까지 중에서 하나의 숫자로 표현해주세요. 0에 가까울수록 오늘의 운세가 안 좋음을 나타내고, 100에 가까울수록 오늘의 운세가 좋음을 나타냅니다. 
반드시 ({t_year}년 {t_month}월 {t_day}일 {want} 점수: 숫자) 형태로 나타내주세요.
숫자는 굵은 글씨로 표현해주세요. 
만약 숫자가 50점 이하라면 🔅, 50점 이상이라면 🔆를 반드시 점수 오른쪽에 붙여주세요.
{moon} {year}년 {month}월 {day}일에 태어난 {gender}성 {name} 님의 {t_year}년 {t_month}월 {t_day}일의 {want} 운세에 대해 설명해주세요.
반드시 {min_length} 단어 이상, {max_length} 단어 이내로 설명해주세요.
오늘이 어떤 날인지 간단히 설명하고 그에 대한 자세한 설명을 덧붙여주세요.
오늘 하루동안 어떤 일을 조심해야하는지, 어떤 사람을 피해야하는지도 설명해주세요.
만약 {want}가 "행운 상승🍀📈"이라면 마지막에 행운의 색상 2가지, 행운의 숫자 2개, 행운의 방향 1곳을 알려주세요. {want}가 "행운 상승🍀📈"이 아니라면 행운의 색상, 행운의 숫자, 행운의 방향은 알려주지 않아도 됩니다.
행운의 숫자는 0부터 9까지의 수이고, 행운의 방향은 동, 서, 남, 북 중 하나입니다.
이모지를 적절히 섞어 설명해주세요.
---
연도: {year}
월: {month}
일: {day}
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
# 이름, 성별, 생년월일, 보고싶은 운세
with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        # 이름
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
    col1, col2 = st.columns(2)
    with col1:
        # 양력/음력
        moon = st.radio(
            "양/음력(필수)",
            ["양력", "음력-평달", "음력-윤달"]
        )
    with col2:
        # 생년월일
        birth = st.date_input(
            "생년월일(필수)",
            min_value=datetime.datetime(1900, 1, 1),
            max_value=datetime.datetime(2024, 1, 1),
            value=example["birth"] if auto_complete else None
        )
    col1, col2 = st.columns(2)
    with col1:
        # 태어난 시간
        time = st.time_input(
            "태어난 시(HH : mm 형태로 입력)",
            # datetime.time(00, 00)
            value=example["time"] if auto_complete else None
        )
    with col2:
        date = st.date_input(
            "날짜",
            min_value=datetime.datetime.now(),
            value=tomorrow_date if tomorrow else "today",
        )
    fortune = st.selectbox(
        "보고 싶은 운세는?!",
        ("전체🌈", "성공 재물운🐖", "행운 상승🍀📈")
    )
    # st.write(f"오늘 나의 {fortune} 운세를 확인해보세요.")
    
    submit = st.form_submit_button("확인하기")

if submit:
    if not name:
        st.error("이름을 입력해주세요.")
    if not birth:
        st.error("생년월일을 입력해주세요.")
        
    year = birth.year
    month = birth.month
    day = birth.day
    t_year = date.year
    t_month = date.month
    t_day = date.day
        
    # 태어난 시각 모를 때
    if not time:
        prompt = generate_prompt(
            moon=moon,
            year=year,
            month=month,
            day=day,
            gender=gender,
            name=name,
            t_year=t_year,
            t_month=t_month,
            t_day=t_day,
            want=fortune[:-1],
            min_length=150,
            max_length=200
        )
    # 태어난 시각 알 때
    else:
        hour = time.hour
        minute = time.minute
        prompt = generate_prompt_birth(
            moon=moon,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            gender=gender,
            name=name,
            t_year=t_year,
            t_month=t_month,
            t_day=t_day,
            want=fortune[:-1],
            min_length=150,
            max_length=200
        )
    st.write(f"**{name} 님의 {t_month}월 {t_day}일 {fortune} 운세를 확인 중...**")
    st.divider()
    response = request_chat_completion(prompt)
    print_streaming_response(response)
    









 
    
    
    
    
   
