import streamlit as st
from openai import OpenAI
import datetime
import time

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

st.set_page_config(
    initial_sidebar_state="collapsed"
)

st.title("🐉 청룡신이 알려주는 2024년 신년 운세")
st.subheader("AI를 이용하여 2024년 운세를 점쳐보세요🔮")
st.info("운세를 보기 위해선 기본 정보가 꼭 필요합니다. 운세결과에 중요한 영향을 미치니 정확히 입력해주세요!")
st.info("태어난 시간 입력은 선택이지만 입력했을 때와 안 했을 때 결과가 달라질 수 있으니 되도록 입력하는 것을 권장합니다. (24시간 기준으로 입력해주세요)")

auto_complete = st.toggle(label="예시로 설정하기")
example = {
    "name": "홍길동",
    "birth": datetime.datetime(1900, 1, 1),
    "time": datetime.time(0,00),
}


# 태어난 시간을 아는 사람
def generate_prompt_birth(moon, year, month, day, hour, minute, gender, name, want, min_length, max_length):
    prompt = f"""
{year}년 {month}월 {day}일 {hour}시 {minute}분에 태어난 {gender}성인 {name} 님의 2024년 {want} 운세를 자연현상에 빗대어 자세히 설명해주세요.
반드시 {min_length} 단어 이상, {max_length} 단어 이내로 설명해주세요.
{moon} {year}에 태어난 사람이 2024년 기준 삼재에 해당하는지 여부도 알려주세요. 만약 삼재에 해당한다면 무엇을 조심해야하는지 알려주세요.
적절한 공감과 냉정함을 섞어 설명해주세요. 
2024년에 조심해야할 행동도 설명해주세요. 조심해야할 행동을 설명하기 전, 앞에 ❌를 붙여주세요.
마지막으로, 2024년 {want} 운세에서 좋음이 두드러지는 달은 몇월이고, 어떤 부분에서 좋은지 자세히 설명해주세요. 2024년 {want} 운세에서 나쁨이 두드러지는 달은 몇월이고, 어떤 부분에서 좋지 않은지 자세히 설명해주세요.
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
def generate_prompt(moon, year, month, day, gender, name, want, min_length, max_length):
    prompt = f"""
{year}년 {month}월 {day}일에 태어난 {gender}성 {name} 님의 2024년 {want} 운세에 대해 설명해주세요.
반드시 {min_length} 단어 이상, {max_length} 단어 이내로 설명해주세요.
{moon} {year}에 태어난 사람이 2024년 기준 삼재에 해당하는지 여부도 알려주세요. 만약 삼재에 해당한다면 무엇을 조심해야하는지 알려주세요.
적절한 공감과 냉정함을 섞어 설명해주세요. 
2024년에 조심해야할 행동도 설명해주세요. 조심해야할 행동을 설명하기 전, 앞에 ❌를 붙여주세요.
마지막으로, 2024년 {want} 운세에서 좋음이 두드러지는 달은 몇월이고, 어떤 부분에서 좋은지 자세히 설명해주세요. 2024년 {want} 운세에서 나쁨이 두드러지는 달은 몇월이고, 어떤 부분에서 좋지 않은지 자세히 설명해주세요.
이모지를 적절히 섞어 설명해주세요.
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
    # 이름
    with col1:
        name = st.text_input(
            "성명(필수)",
            value=example["name"] if auto_complete else "",
            placeholder=example["name"]
        )
    # 성별
    with col2:
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
        # 생년월일
        birth = st.date_input(
            "생년월일(필수)",
            min_value=datetime.datetime(1900, 1, 1),
            max_value=datetime.datetime(2024, 1, 1),
            value=example["birth"] if auto_complete else None
        )
    with col3:
        # 태어난 시간
        time = st.time_input(
            "태어난 시(HH : mm 형태로 입력)",
            # datetime.time(00, 00)
            value=example["time"] if auto_complete else None
        )
    fortune = st.selectbox(
        "보고 싶은 운세는?!",
        ("신년 전체🐉", "재물운💵", "직장운💼", "사업운🧑‍💼", "애정운🫶", "건강운💊")
    )
    submit = st.form_submit_button("확인하기")

# 확인 버튼
if submit:
    if not name:
        st.error("이름을 입력해주세요.")
    elif not birth:
        st.error("생년월일을 입력해주세요.")
        
    year = birth.year
    month = birth.month
    day = birth.day
    
    if not time:
        # year = birth.year
        # month = birth.month
        # day = birth.day
        # 태어난 시각 모를 때
        prompt = generate_prompt(
            moon=moon,
            year=year,
            month=month,
            day=day,
            gender=gender,
            name=name,
            want=fortune[:-1],
            min_length=200,
            max_length=300
        )
    else:
        # year = birth.year
        # month = birth.month
        # day = birth.day
        hour = time.hour
        minute = time.minute
        # 태어난 시각 알 때
        prompt = generate_prompt_birth(
            moon=moon,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            gender=gender,
            name=name,
            want=fortune[:-1],
            min_length=200,
            max_length=300
        )
    st.write(f"**{year}년 {month}월 {day}일 {name} 님의 2024년 {fortune} 풀이 중...**")
    st.divider()
    # st.success(f"{name} 님의 2024년 {fortune} 운세 확인중...")
    response = request_chat_completion(prompt)
    print_streaming_response(response)
    
    
    
    
    
