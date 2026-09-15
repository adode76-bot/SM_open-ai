import streamlit as st
import requests
from datetime import datetime

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="보라고등학교 급식 정보",
    page_icon="🍱",
    layout="centered"
)

# 2. 고정 코드 값
ATPPT_OFCDC_SC_CODE = "J10"  # 경기도교육청
SD_SCHUL_CODE = "7530882"     # 보라고등학교

# 3. 급식 정보 불러오기 함수
def get_meal_info(date_str, api_key=""):
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "Type": "json",
        "pIndex": 1,
        "pSize": 10,
        "ATPT_OFCDC_SC_CODE": ATPPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,
        "MLSV_YMD": date_str
    }
    
    if api_key:
        params["KEY"] = api_key

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # 정상 처리 결과 확인
        if "mealServiceDietInfo" in data:
            row = data["mealServiceDietInfo"][1]["row"]
            return row
        else:
            return None
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return None

# 4. UI 구성
st.title("🍱 보라고등학교 급식 메뉴")
st.caption("NEIS OPEN API 기반 급식 조회 서비스")

# 날짜 선택기 (기본값: 오늘 날짜)
selected_date = st.date_input("조회할 날짜를 선택하세요", datetime.today())
date_str = selected_date.strftime("%Y%m%d")

# 사이드바 (선택 사항: API KEY 입력)
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("NEIS API Key (선택)", type="password", help="키가 없어도 기본 호출이 가능하지만, 하루 호출 제한이 완화됩니다.")
    st.markdown("---")
    st.markdown("**학교 정보**")
    st.text(f"교육청 코드: {ATPPT_OFCDC_SC_CODE}")
    st.text(f"학교 코드: {SD_SCHUL_CODE}")

# 5. 급식 데이터 출력
st.subheader(f"📅 {selected_date.strftime('%Y년 %m월 %d일')} 급식")

with st.spinner("급식 정보를 가져오는 중..."):
    meals = get_meal_info(date_str, api_key)

if meals:
    for meal in meals:
        meal_type = meal.get("MMEAL_SC_NM", "급식")
        
        # NEIS 데이터 내 <br/> 태그 및 알레르기 번호 제거 정제
        dish_name_raw = meal.get("DDISH_NM", "")
        # <br/> 태그 처리
        dishes = dish_name_raw.replace("<br/>", "\n").split("\n")
        
        # 칼로리 및 원산지 정보
        cal_info = meal.get("CAL_INFO", "정보 없음")
        
        with st.expander(f"🥣 {meal_type}", expanded=True):
            st.markdown("**[메뉴 목록]**")
            for dish in dishes:
                if dish.strip():
                    st.write(f"- {dish.strip()}")
            st.info(f"💡 **칼로리:** {cal_info}")
else:
    st.warning("해당 날짜에는 등록된 급식 정보가 없거나 주말/공휴일입니다.")
