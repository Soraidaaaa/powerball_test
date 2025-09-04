import streamlit as st
import random
import pandas as pd
from datetime import datetime
import math

# 페이지 설정
st.set_page_config(
    page_title="파워볼 시뮬레이터",
    page_icon="🎱",
    layout="wide"
)

# 세션 상태 초기화
if 'total_spent' not in st.session_state:
    st.session_state.total_spent = 0
if 'total_winnings' not in st.session_state:
    st.session_state.total_winnings = 0
if 'game_history' not in st.session_state:
    st.session_state.game_history = []
if 'current_jackpot' not in st.session_state:
    st.session_state.current_jackpot = 20000000  # 2천만 달러 시작
if 'games_played' not in st.session_state:
    st.session_state.games_played = 0

# 파워볼 확률 및 상금 설정
POWERBALL_ODDS = {
    'jackpot': 292201338,  # 5개 + 파워볼
    '2nd': 11688054,       # 5개
    '3rd': 913129,         # 4개 + 파워볼
    '4th': 36525,          # 4개
    '5th': 14494,          # 3개 + 파워볼
    '6th': 579,            # 3개
    '7th': 701,            # 2개 + 파워볼
    '8th': 92,             # 1개 + 파워볼
    '9th': 38              # 파워볼만
}

FIXED_PRIZES = {
    '2nd': 1000000,
    '3rd': 50000,
    '4th': 100,
    '5th': 100,
    '6th': 7,
    '7th': 7,
    '8th': 4,
    '9th': 4
}

def generate_winning_numbers():
    """당첨 번호 생성"""
    main_numbers = sorted(random.sample(range(1, 70), 5))
    powerball = random.randint(1, 26)
    return main_numbers, powerball

def check_winning(user_numbers, user_powerball, winning_numbers, winning_powerball):
    """당첨 확인 및 등수 반환"""
    main_matches = len(set(user_numbers) & set(winning_numbers))
    powerball_match = user_powerball == winning_powerball
    
    if main_matches == 5 and powerball_match:
        return 'jackpot'
    elif main_matches == 5:
        return '2nd'
    elif main_matches == 4 and powerball_match:
        return '3rd'
    elif main_matches == 4:
        return '4th'
    elif main_matches == 3 and powerball_match:
        return '5th'
    elif main_matches == 3:
        return '6th'
    elif main_matches == 2 and powerball_match:
        return '7th'
    elif main_matches == 1 and powerball_match:
        return '8th'
    elif powerball_match:
        return '9th'
    else:
        return None

def calculate_prize(prize_level):
    """상금 계산"""
    if prize_level == 'jackpot':
        return st.session_state.current_jackpot
    else:
        return FIXED_PRIZES.get(prize_level, 0)

def format_currency(amount):
    """달러 형식으로 포맷"""
    return f"${amount:,.2f}"

# 메인 타이틀
st.title("🎱 파워볼 시뮬레이터")
st.markdown("---")

# 상단 정보 표시
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("현재 잭팟", format_currency(st.session_state.current_jackpot))

with col2:
    st.metric("총 사용금액", format_currency(st.session_state.total_spent))

with col3:
    st.metric("총 당첨금액", format_currency(st.session_state.total_winnings))

with col4:
    profit = st.session_state.total_winnings - st.session_state.total_spent
    st.metric("순수익", format_currency(profit), 
              delta=format_currency(profit) if profit != 0 else None)

st.markdown("---")

# 게임 플레이 섹션
st.header("🎲 게임 플레이")

col_left, col_right = st.columns([2, 1])

with col_left:
    # 번호 선택 방식
    number_method = st.radio(
        "번호 선택 방식:",
        ["직접 선택", "랜덤 선택"],
        horizontal=True
    )
    
    if number_method == "직접 선택":
        st.write("**메인 번호 5개 선택 (1-69):**")
        col_nums = st.columns(5)
        main_numbers = []
        for i in range(5):
            with col_nums[i]:
                num = st.number_input(
                    f"번호 {i+1}", 
                    min_value=1, 
                    max_value=69, 
                    value=1, 
                    key=f"main_{i}"
                )
                main_numbers.append(num)
        
        st.write("**파워볼 번호 선택 (1-26):**")
        powerball_number = st.number_input(
            "파워볼", 
            min_value=1, 
            max_value=26, 
            value=1
        )
    else:
        main_numbers = sorted(random.sample(range(1, 70), 5))
        powerball_number = random.randint(1, 26)
        
        st.write("**랜덤 선택된 번호:**")
        st.write(f"메인 번호: {main_numbers}")
        st.write(f"파워볼: {powerball_number}")

with col_right:
    st.write("**파워볼 룰**")
    st.write("• 메인 번호: 1-69 중 5개")
    st.write("• 파워볼: 1-26 중 1개")
    st.write("• 게임당 비용: $2")
    st.write("• 잭팟 당첨 확률:")
    st.write("  1/292,201,338")

# 게임 플레이 버튼
if st.button("🎯 게임 플레이 ($2)", type="primary", use_container_width=True):
    # 번호 유효성 검사
    if number_method == "직접 선택":
        if len(set(main_numbers)) != 5:
            st.error("메인 번호 5개는 모두 다른 숫자여야 합니다!")
        elif any(num < 1 or num > 69 for num in main_numbers):
            st.error("메인 번호는 1-69 사이여야 합니다!")
        elif powerball_number < 1 or powerball_number > 26:
            st.error("파워볼 번호는 1-26 사이여야 합니다!")
        else:
            valid_numbers = True
    else:
        valid_numbers = True
    
    if valid_numbers:
        # 당첨 번호 생성
        winning_main, winning_powerball = generate_winning_numbers()
        
        # 당첨 확인
        prize_level = check_winning(main_numbers, powerball_number, winning_main, winning_powerball)
        
        # 상금 계산
        prize_amount = calculate_prize(prize_level) if prize_level else 0
        
        # 세션 상태 업데이트
        st.session_state.total_spent += 2
        st.session_state.total_winnings += prize_amount
        st.session_state.games_played += 1
        
        # 잭팟 업데이트
        if prize_level == 'jackpot':
            st.session_state.current_jackpot = 20000000  # 잭팟 리셋
        else:
            st.session_state.current_jackpot += 1000000  # 잭팟 증가
        
        # 게임 히스토리 추가
        game_record = {
            'game_number': st.session_state.games_played,
            'timestamp': datetime.now(),
            'user_numbers': main_numbers.copy(),
            'user_powerball': powerball_number,
            'winning_numbers': winning_main.copy(),
            'winning_powerball': winning_powerball,
            'prize_level': prize_level,
            'prize_amount': prize_amount
        }
        st.session_state.game_history.append(game_record)
        
        # 결과 표시
        st.markdown("---")
        st.header("🎊 게임 결과")
        
        col_result1, col_result2 = st.columns(2)
        
        with col_result1:
            st.write("**당신의 번호:**")
            st.write(f"메인: {sorted(main_numbers)}")
            st.write(f"파워볼: {powerball_number}")
        
        with col_result2:
            st.write("**당첨 번호:**")
            st.write(f"메인: {winning_main}")
            st.write(f"파워볼: {winning_powerball}")
        
        if prize_level:
            if prize_level == 'jackpot':
                st.success(f"🎉 잭팟 당첨! {format_currency(prize_amount)}")
                st.balloons()
            else:
                level_names = {
                    '2nd': '2등', '3rd': '3등', '4th': '4등', 
                    '5th': '5등', '6th': '6등', '7th': '7등',
                    '8th': '8등', '9th': '9등'
                }
                st.success(f"🎊 {level_names[prize_level]} 당첨! {format_currency(prize_amount)}")
        else:
            st.info("😅 아쉽게도 당첨되지 않았습니다.")
        
        # 페이지 새로고침
        st.rerun()

# 게임 히스토리
if st.session_state.game_history:
    st.markdown("---")
    st.header("📊 게임 히스토리")
    
    # 최근 10게임만 표시
    recent_games = st.session_state.game_history[-10:]
    
    history_data = []
    for game in reversed(recent_games):
        history_data.append({
            '게임 번호': game['game_number'],
            '시간': game['timestamp'].strftime("%H:%M:%S"),
            '선택 번호': f"{sorted(game['user_numbers'])} + {game['user_powerball']}",
            '당첨 번호': f"{game['winning_numbers']} + {game['winning_powerball']}",
            '등수': game['prize_level'] if game['prize_level'] else '미당첨',
            '상금': format_currency(game['prize_amount'])
        })
    
    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True)
    
    # 통계 정보
    if len(st.session_state.game_history) >= 5:
        st.subheader("📈 통계")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            win_rate = sum(1 for game in st.session_state.game_history if game['prize_level']) / len(st.session_state.game_history) * 100
            st.metric("당첨률", f"{win_rate:.1f}%")
        
        with col_stat2:
            avg_loss_per_game = (st.session_state.total_spent - st.session_state.total_winnings) / st.session_state.games_played
            st.metric("게임당 평균 손실", format_currency(avg_loss_per_game))
        
        with col_stat3:
            roi = (st.session_state.total_winnings / st.session_state.total_spent - 1) * 100 if st.session_state.total_spent > 0 else 0
            st.metric("투자 수익률", f"{roi:.1f}%")

# 리셋 버튼
st.markdown("---")
if st.button("🔄 게임 초기화", type="secondary"):
    for key in ['total_spent', 'total_winnings', 'game_history', 'games_played', 'games_since_jackpot']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.current_jackpot = 20000000
    st.rerun()

# 사이드바에 확률 정보 표시
with st.sidebar:
    st.header("🎯 당첨 확률 & 상금")
    st.write("**각 등수별 당첨 확률:**")
    
    probability_info = [
        ("잭팟 (5+PB)", "1:292,201,338", f"${st.session_state.current_jackpot/1000000:.0f}M+"),
        ("2등 (5개)", "1:11,688,054", "$1M"),
        ("3등 (4+PB)", "1:913,129", "$50K"),
        ("4등 (4개)", "1:36,525", "$100"),
        ("5등 (3+PB)", "1:14,494", "$100"),
        ("6등 (3개)", "1:579", "$7"),
        ("7등 (2+PB)", "1:701", "$7"),
        ("8등 (1+PB)", "1:92", "$4"),
        ("9등 (PB)", "1:38", "$4")
    ]
    
    for level, odds, prize in probability_info:
        st.write(f"**{level}**")
        st.write(f"확률: {odds}")
        st.write(f"상금: {prize}")
        st.write("---")
    
    # 잭팟 예측 정보
    st.header("📈 잭팟 예측")
    current = st.session_state.current_jackpot
    games_since = st.session_state.games_since_jackpot
    
    # 다음 5번의 예상 잭팟 증가
    future_jackpots = []
    temp_jackpot = current
    temp_games = games_since
    
    for i in range(1, 6):
        temp_games += 1
        increase = calculate_jackpot_increase(temp_jackpot, temp_games)
        temp_jackpot += increase
        future_jackpots.append(temp_jackpot)
    
    st.write("**다음 5번 이월 예상:**")
    for i, future_jackpot in enumerate(future_jackpots, 1):
        if future_jackpot >= 1000000000:
            display = f"${future_jackpot/1000000000:.2f}B"
        else:
            display = f"${future_jackpot/1000000:.0f}M"
        st.write(f"{games_since + i}회: {display}")
    
    # 대형 잭팟까지 예상 게임수
    st.write("**목표 잭팟까지 예상:**")
    targets = [100000000, 500000000, 1000000000]  # 1억, 5억, 10억
    target_names = ["1억 달러", "5억 달러", "10억 달러"]
    
    temp_jackpot = current
    temp_games = games_since
    
    for target, name in zip(targets, target_names):
        if current < target:
            games_needed = 0
            while temp_jackpot < target and games_needed < 100:  # 최대 100게임
                temp_games += 1
                games_needed += 1
                increase = calculate_jackpot_increase(temp_jackpot, temp_games)
                temp_jackpot += increase
            
            if games_needed < 100:
                st.write(f"• {name}: 약 {games_needed}게임 후")
            else:
                st.write(f"• {name}: 100게임+ 후")
        else:
            st.write(f"• {name}: ✅ 달성!")