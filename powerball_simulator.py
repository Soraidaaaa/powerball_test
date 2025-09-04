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
if 'games_since_jackpot' not in st.session_state:
    st.session_state.games_since_jackpot = 0

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

def calculate_jackpot_increase(current_jackpot, games_since_jackpot, game_revenue=2):
    """
    현실적인 잭팟 증가 계산 (대폭 개선된 버전)
    - 42번 이월시 약 $1.1B 달성 목표
    - 매회 상당한 증가량으로 사용자 체감도 향상
    """
    # 기본 증가: 게임당 $15M (훨씬 현실적)
    base_increase = 15000000
    
    # 심리적 효과 (잭팟 크기별 참여자 증가)
    multiplier = 1.0
    if current_jackpot > 800000000:       # 8억 이상: 2.5배
        multiplier = 2.5
    elif current_jackpot > 400000000:     # 4억 이상: 2.0배
        multiplier = 2.0
    elif current_jackpot > 200000000:     # 2억 이상: 1.6배
        multiplier = 1.6
    elif current_jackpot > 100000000:     # 1억 이상: 1.3배
        multiplier = 1.3
    elif current_jackpot > 50000000:      # 5천만 이상: 1.15배
        multiplier = 1.15
    
    # 가뭄 효과 (20게임마다 50% 추가 증가)
    drought_multiplier = 1 + (games_since_jackpot / 20) * 0.5
    
    # 최종 증가 계산
    increase = base_increase * multiplier * drought_multiplier
    
    return int(increase)

def simulate_other_winners(current_jackpot, games_since_jackpot):
    """
    다른 당첨자가 나올 확률 계산
    잭팟이 클수록, 오래 이월될수록 다른 당첨자 확률 증가
    """
    import random
    
    # 기본 확률: 매우 낮음 (실제 파워볼과 유사)
    base_probability = 0.0001  # 0.01%
    
    # 잭팟 크기에 따른 확률 증가 (사람들이 더 많이 참여)
    if current_jackpot > 1000000000:      # 10억 이상
        jackpot_multiplier = 50
    elif current_jackpot > 500000000:     # 5억 이상
        jackpot_multiplier = 25
    elif current_jackpot > 200000000:     # 2억 이상
        jackpot_multiplier = 10
    elif current_jackpot > 100000000:     # 1억 이상
        jackpot_multiplier = 5
    else:
        jackpot_multiplier = 1
    
    # 가뭄 효과 (오래 안 나올수록 확률 증가)
    drought_multiplier = 1 + (games_since_jackpot / 100)
    
    # 최종 확률
    final_probability = base_probability * jackpot_multiplier * drought_multiplier
    
    # 최대 5%로 제한
    final_probability = min(final_probability, 0.05)
    
    return random.random() < final_probability

def calculate_prize(prize_level):
    """상금 계산"""
    if prize_level == 'jackpot':
        return st.session_state.current_jackpot
    else:
        return FIXED_PRIZES.get(prize_level, 0)

def format_currency(amount):
    """달러 형식으로 포맷"""
    return f"${amount:,.2f}"

def execute_single_game(main_numbers, powerball_number):
    """단일 게임 실행"""
    # 당첨 번호 생성
    winning_main, winning_powerball = generate_winning_numbers()
    
    # 당첨 확인
    prize_level = check_winning(main_numbers, powerball_number, winning_main, winning_powerball)
    
    # 상금 계산
    prize_amount = calculate_prize(prize_level) if prize_level else 0
    
    # 다른 당첨자 확인
    other_winner = simulate_other_winners(st.session_state.current_jackpot, st.session_state.games_since_jackpot)
    
    # 세션 상태 업데이트
    st.session_state.total_spent += 2
    st.session_state.total_winnings += prize_amount
    st.session_state.games_played += 1
    
    # 잭팟 증가량 계산 (결과 표시용)
    increase_before = calculate_jackpot_increase(
        st.session_state.current_jackpot, 
        st.session_state.games_since_jackpot
    )
    
    # 잭팟 업데이트
    if prize_level == 'jackpot' or other_winner:
        if other_winner and prize_level != 'jackpot':
            st.warning("🎰 **다른 당첨자가 나타났습니다!** 잭팟이 초기화됩니다.")
        st.session_state.current_jackpot = 20000000  # 잭팟 리셋
        st.session_state.games_since_jackpot = 0
    else:
        st.session_state.current_jackpot += increase_before
        st.session_state.games_since_jackpot += 1
    
    # 게임 히스토리 추가
    game_record = {
        'game_number': st.session_state.games_played,
        'timestamp': datetime.now(),
        'user_numbers': main_numbers.copy(),
        'user_powerball': powerball_number,
        'winning_numbers': winning_main.copy(),
        'winning_powerball': winning_powerball,
        'prize_level': prize_level,
        'prize_amount': prize_amount,
        'other_winner': other_winner
    }
    st.session_state.game_history.append(game_record)
    
    # 결과 표시
    display_single_game_result(main_numbers, powerball_number, winning_main, winning_powerball, 
                              prize_level, prize_amount, other_winner, increase_before)
    
    # 페이지 새로고침
    st.rerun()

def display_single_game_result(main_numbers, powerball_number, winning_main, winning_powerball, 
                              prize_level, prize_amount, other_winner, jackpot_increase):
    """단일 게임 결과 표시"""
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
            st.success(f"🎉 🎊 **잭팟 대박!** 🎊 🎉")
            st.success(f"**축하합니다! {format_currency(prize_amount)} 당첨!**")
            if prize_amount >= 1000000000:  # 10억 달러 이상
                st.balloons()
                st.write("🌟 **역사적인 메가 잭팟 당첨!** 🌟")
            elif prize_amount >= 500000000:  # 5억 달러 이상  
                st.balloons()
                st.write("🚀 **슈퍼 잭팟 당첨!** 🚀")
            else:
                st.balloons()
        else:
            level_names = {
                '2nd': '2등 ($1M)', '3rd': '3등 ($50K)', '4th': '4등 ($100)', 
                '5th': '5등 ($100)', '6th': '6등 ($7)', '7th': '7등 ($7)',
                '8th': '8등 ($4)', '9th': '9등 ($4)'
            }
            st.success(f"🎊 {level_names[prize_level]} 당첨! {format_currency(prize_amount)}")
    else:
        st.info("😅 아쉽게도 당첨되지 않았습니다.")
    
    # 잭팟 증가 정보 표시
    if prize_level != 'jackpot' and not other_winner:
        st.info(f"💰 다음 잭팟이 {format_currency(jackpot_increase)} 증가했습니다!")
        
        # 잭팟 수준 변화 알림
        new_jackpot = st.session_state.current_jackpot
        old_jackpot = new_jackpot - jackpot_increase
        
        if new_jackpot >= 1000000000 and old_jackpot < 1000000000:
            st.warning("🔥 **메가 잭팟 달성!** 10억 달러 돌파!")
        elif new_jackpot >= 500000000 and old_jackpot < 500000000:
            st.warning("🚀 **슈퍼 잭팟 달성!** 5억 달러 돌파!")
        elif new_jackpot >= 100000000 and old_jackpot < 100000000:
            st.warning("💎 **대형 잭팟 달성!** 1억 달러 돌파!")

def execute_auto_until_prize(target_prize, max_games, number_method, fixed_main=None, fixed_powerball=None):
    """특정 등수 당첨까지 자동 플레이"""
    target_levels = {
        "9등 이상 ($4+)": ['9th', '8th', '7th', '6th', '5th', '4th', '3rd', '2nd', 'jackpot'],
        "7등 이상 ($7+)": ['7th', '6th', '5th', '4th', '3rd', '2nd', 'jackpot'],
        "5등 이상 ($100+)": ['5th', '4th', '3rd', '2nd', 'jackpot'],
        "3등 이상 ($50K+)": ['3rd', '2nd', 'jackpot'],
        "2등 이상 ($1M+)": ['2nd', 'jackpot'],
        "1등 (잭팟)": ['jackpot']
    }
    
    target_list = target_levels[target_prize]
    games_played = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while games_played < max_games:
        games_played += 1
        
        # 번호 생성
        if number_method == "고정 번호 사용":
            main_numbers = fixed_main
            powerball_number = fixed_powerball
        else:
            main_numbers = sorted(random.sample(range(1, 70), 5))
            powerball_number = random.randint(1, 26)
        
        # 게임 실행
        winning_main, winning_powerball = generate_winning_numbers()
        prize_level = check_winning(main_numbers, powerball_number, winning_main, winning_powerball)
        
        # 결과 처리
        prize_amount = calculate_prize(prize_level) if prize_level else 0
        other_winner = simulate_other_winners(st.session_state.current_jackpot, st.session_state.games_since_jackpot)
        
        # 상태 업데이트
        st.session_state.total_spent += 2
        st.session_state.total_winnings += prize_amount
        st.session_state.games_played += 1
        
        # 잭팟 관리
        if prize_level == 'jackpot' or other_winner:
            st.session_state.current_jackpot = 20000000
            st.session_state.games_since_jackpot = 0
        else:
            jackpot_increase = calculate_jackpot_increase(st.session_state.current_jackpot, st.session_state.games_since_jackpot)
            st.session_state.current_jackpot += jackpot_increase
            st.session_state.games_since_jackpot += 1
        
        # 진행상황 업데이트
        progress_bar.progress(games_played / max_games)
        status_text.text(f"진행: {games_played}/{max_games}게임 | 현재 잭팟: ${st.session_state.current_jackpot/1000000:.1f}M")
        
        # 목표 달성 확인
        if prize_level in target_list:
            st.success(f"🎊 **목표 달성!** {games_played}게임 만에 {target_prize} 당첨!")
            st.success(f"당첨금: {format_currency(prize_amount)}")
            break
        
        # 다른 당첨자로 인한 잭팟 초기화 알림
        if other_winner:
            st.info(f"🎰 {games_played}게임: 다른 당첨자 출현으로 잭팟 초기화")
    
    if games_played >= max_games:
        st.warning(f"⏰ 최대 게임 수({max_games}게임)에 도달했습니다. 목표를 달성하지 못했습니다.")
    
    st.info(f"📊 자동 플레이 결과: {games_played}게임, 총 비용 ${games_played * 2:,}")
    st.rerun()

def execute_auto_fixed_games(game_count, number_method, fixed_main=None, fixed_powerball=None):
    """정해진 횟수만큼 자동 플레이"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    best_prize = None
    best_amount = 0
    jackpot_resets = 0
    
    for i in range(game_count):
        # 번호 생성
        if number_method == "고정 번호 사용":
            main_numbers = fixed_main
            powerball_number = fixed_powerball
        else:
            main_numbers = sorted(random.sample(range(1, 70), 5))
            powerball_number = random.randint(1, 26)
        
        # 게임 실행
        winning_main, winning_powerball = generate_winning_numbers()
        prize_level = check_winning(main_numbers, powerball_number, winning_main, winning_powerball)
        
        # 결과 처리
        prize_amount = calculate_prize(prize_level) if prize_level else 0
        other_winner = simulate_other_winners(st.session_state.current_jackpot, st.session_state.games_since_jackpot)
        
        # 최고 상금 기록
        if prize_amount > best_amount:
            best_prize = prize_level
            best_amount = prize_amount
        
        # 상태 업데이트
        st.session_state.total_spent += 2
        st.session_state.total_winnings += prize_amount
        st.session_state.games_played += 1
        
        # 잭팟 관리
        if prize_level == 'jackpot' or other_winner:
            st.session_state.current_jackpot = 20000000
            st.session_state.games_since_jackpot = 0
            if other_winner:
                jackpot_resets += 1
        else:
            jackpot_increase = calculate_jackpot_increase(st.session_state.current_jackpot, st.session_state.games_since_jackpot)
            st.session_state.current_jackpot += jackpot_increase
            st.session_state.games_since_jackpot += 1
        
        # 진행상황 업데이트
        progress_bar.progress((i + 1) / game_count)
        current_jackpot_display = f"${st.session_state.current_jackpot/1000000:.1f}M" if st.session_state.current_jackpot < 1000000000 else f"${st.session_state.current_jackpot/1000000000:.2f}B"
        status_text.text(f"진행: {i + 1}/{game_count}게임 | 현재 잭팟: {current_jackpot_display} | 최고상금: ${best_amount:,}")
    
    # 결과 요약
    st.success(f"🎯 **{game_count}게임 자동 플레이 완료!**")
    
    col1, col2 = st.columns(2)
    with col1:
        if best_amount > 0:
            level_names = {
                'jackpot': '잭팟', '2nd': '2등', '3rd': '3등', '4th': '4등', 
                '5th': '5등', '6th': '6등', '7th': '7등', '8th': '8등', '9th': '9등'
            }
            st.info(f"🏆 최고 당첨: {level_names.get(best_prize, '알 수 없음')} - {format_currency(best_amount)}")
        else:
            st.info("😅 아쉽게도 당첨되지 않았습니다.")
    
    with col2:
        total_cost = game_count * 2
        if jackpot_resets > 0:
            st.info(f"🎰 다른 당첨자로 인한 잭팟 초기화: {jackpot_resets}번")
        st.info(f"💸 총 비용: ${total_cost:,}")
    
    st.rerun()

def execute_auto_until_jackpot(max_games, number_method, fixed_main=None, fixed_powerball=None):
    """잭팟 당첨까지 자동 플레이"""
    games_played = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    st.warning("⚠️ 잭팟 당첨 확률은 매우 낮습니다. 시간이 오래 걸릴 수 있습니다!")
    
    while games_played < max_games:
        games_played += 1
        
        # 번호 생성
        if number_method == "고정 번호 사용":
            main_numbers = fixed_main
            powerball_number = fixed_powerball
        else:
            main_numbers = sorted(random.sample(range(1, 70), 5))
            powerball_number = random.randint(1, 26)
        
        # 게임 실행
        winning_main, winning_powerball = generate_winning_numbers()
        prize_level = check_winning(main_numbers, powerball_number, winning_main, winning_powerball)
        
        # 결과 처리
        prize_amount = calculate_prize(prize_level) if prize_level else 0
        other_winner = simulate_other_winners(st.session_state.current_jackpot, st.session_state.games_since_jackpot)
        
        # 상태 업데이트
        st.session_state.total_spent += 2
        st.session_state.total_winnings += prize_amount
        st.session_state.games_played += 1
        
        # 잭팟 당첨 확인
        if prize_level == 'jackpot':
            st.success(f"🎉 **잭팟 당첨!** {games_played}게임 만에 달성!")
            st.success(f"🎊 당첨금: {format_currency(prize_amount)}")
            st.balloons()
            break
        
        # 잭팟 관리
        if other_winner:
            st.session_state.current_jackpot = 20000000
            st.session_state.games_since_jackpot = 0
        else:
            jackpot_increase = calculate_jackpot_increase(st.session_state.current_jackpot, st.session_state.games_since_jackpot)
            st.session_state.current_jackpot += jackpot_increase
            st.session_state.games_since_jackpot += 1
        
        # 진행상황 업데이트
        progress_bar.progress(games_played / max_games)
        current_jackpot_display = f"${st.session_state.current_jackpot/1000000:.1f}M" if st.session_state.current_jackpot < 1000000000 else f"${st.session_state.current_jackpot/1000000000:.2f}B"
        status_text.text(f"진행: {games_played}/{max_games}게임 | 현재 잭팟: {current_jackpot_display}")
        
        # 중간에 다른 당첨자가 나타난 경우
        if other_winner:
            st.info(f"🎰 {games_played}게임: 다른 당첨자 출현으로 잭팟 초기화")
    
    if games_played >= max_games:
        st.warning(f"⏰ 최대 게임 수({max_games}게임)에 도달했습니다. 잭팟을 당첨하지 못했습니다.")
        st.info("😅 확률상 잭팟 당첨은 매우 어렵습니다. 다시 도전해보세요!")
    
    st.info(f"📊 자동 플레이 결과: {games_played}게임, 총 비용 ${games_played * 2:,}")
    st.rerun()

# 메인 타이틀
st.title("🎱 파워볼 시뮬레이터")
st.markdown("---")

# 상단 정보 표시
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    jackpot_billions = st.session_state.current_jackpot / 1000000000
    if jackpot_billions >= 1:
        jackpot_display = f"${jackpot_billions:.2f}B"
    else:
        jackpot_display = format_currency(st.session_state.current_jackpot)
    st.metric("현재 잭팟", jackpot_display)

with col2:
    st.metric("연속 미당첨", f"{st.session_state.games_since_jackpot}회")

with col3:
    st.metric("총 사용금액", format_currency(st.session_state.total_spent))

with col4:
    st.metric("총 당첨금액", format_currency(st.session_state.total_winnings))

with col5:
    profit = st.session_state.total_winnings - st.session_state.total_spent
    st.metric("순수익", format_currency(profit), 
              delta=format_currency(profit) if profit != 0 else None)

st.markdown("---")

# 게임 플레이 섹션
st.header("🎲 게임 플레이")

# 자동 플레이 옵션 추가
play_mode = st.radio(
    "플레이 모드:",
    ["단일 게임", "자동 플레이"],
    horizontal=True
)

col_left, col_right = st.columns([2, 1])

with col_left:
    if play_mode == "단일 게임":
        # 기존 단일 게임 로직
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
            
    else:  # 자동 플레이 모드
        st.write("**자동 플레이 설정:**")
        
        auto_mode = st.selectbox(
            "자동 플레이 종류:",
            [
                "특정 등수 당첨까지",
                "정해진 횟수만큼",
                "잭팟 당첨까지 (위험!)"
            ]
        )
        
        if auto_mode == "특정 등수 당첨까지":
            target_prize = st.selectbox(
                "목표 등수:",
                ["9등 이상 ($4+)", "7등 이상 ($7+)", "5등 이상 ($100+)", 
                 "3등 이상 ($50K+)", "2등 이상 ($1M+)", "1등 (잭팟)"]
            )
            max_games = st.number_input("최대 게임 수 (안전장치):", min_value=1, max_value=10000, value=1000)
            
        elif auto_mode == "정해진 횟수만큼":
            fixed_games = st.selectbox("게임 횟수:", [10, 25, 50, 100, 250, 500])
            
        else:  # 잭팟까지
            st.warning("⚠️ 잭팟 당첨까지는 매우 오랜 시간이 걸릴 수 있습니다!")
            max_games = st.number_input("최대 게임 수:", min_value=1, max_value=50000, value=10000)
        
        # 번호 선택 방식 (자동 플레이용)
        auto_number_method = st.radio(
            "번호 선택 방식:",
            ["매번 랜덤", "고정 번호 사용"],
            horizontal=True
        )
        
        if auto_number_method == "고정 번호 사용":
            st.write("**고정 번호 설정:**")
            col_nums = st.columns(5)
            fixed_main_numbers = []
            for i in range(5):
                with col_nums[i]:
                    num = st.number_input(
                        f"메인{i+1}", 
                        min_value=1, 
                        max_value=69, 
                        value=i+1, 
                        key=f"fixed_main_{i}"
                    )
                    fixed_main_numbers.append(num)
            
            fixed_powerball = st.number_input(
                "고정 파워볼", 
                min_value=1, 
                max_value=26, 
                value=1
            )

with col_right:
    st.write("**파워볼 룰**")
    st.write("• 메인 번호: 1-69 중 5개")
    st.write("• 파워볼: 1-26 중 1개")
    st.write("• 게임당 비용: $2")
    st.write("• 잭팟 당첨 확률: 1/292,201,338")
    
    st.write("**💰 현재 잭팟 수준**")
    current_jackpot = st.session_state.current_jackpot
    if current_jackpot >= 1000000000:
        st.write("🔥 **메가 잭팟!** (10억+ 달러)")
    elif current_jackpot >= 500000000:
        st.write("🚀 **슈퍼 잭팟!** (5억+ 달러)")
    elif current_jackpot >= 100000000:
        st.write("💎 **대형 잭팟!** (1억+ 달러)")
    elif current_jackpot >= 50000000:
        st.write("⭐ **고액 잭팟** (5천만+ 달러)")
    else:
        st.write("🎱 **기본 잭팟** (2천만+ 달러)")

# 게임 플레이 버튼
if play_mode == "단일 게임":
    if st.button("🎯 게임 플레이 ($2)", type="primary", use_container_width=True):
        # 기존 단일 게임 로직
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
            # 단일 게임 실행 함수 호출
            execute_single_game(main_numbers, powerball_number)

else:  # 자동 플레이 모드
    if st.button("🚀 자동 플레이 시작", type="primary", use_container_width=True):
        # 자동 플레이 실행
        if auto_mode == "특정 등수 당첨까지":
            execute_auto_until_prize(target_prize, max_games, auto_number_method, 
                                   fixed_main_numbers if auto_number_method == "고정 번호 사용" else None,
                                   fixed_powerball if auto_number_method == "고정 번호 사용" else None)
        elif auto_mode == "정해진 횟수만큼":
            execute_auto_fixed_games(fixed_games, auto_number_method,
                                   fixed_main_numbers if auto_number_method == "고정 번호 사용" else None,
                                   fixed_powerball if auto_number_method == "고정 번호 사용" else None)
        else:  # 잭팟까지
            execute_auto_until_jackpot(max_games, auto_number_method,
                                     fixed_main_numbers if auto_number_method == "고정 번호 사용" else None,
                                     fixed_powerball if auto_number_method == "고정 번호 사용" else None)

# 리셋 버튼
st.markdown("---")
if st.button("🔄 게임 초기화", type="secondary"):
    for key in ['total_spent', 'total_winnings', 'game_history', 'games_played', 'games_since_jackpot']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.current_jackpot = 20000000
    st.rerun()

# 게임 히스토리 표시
if st.session_state.game_history:
    st.markdown("---")
    st.header("📊 게임 히스토리")
    
    # 최근 10게임만 표시
    recent_games = st.session_state.game_history[-10:]
    
    history_data = []
    for game in reversed(recent_games):
        other_info = " (타인당첨)" if game.get('other_winner', False) else ""
        history_data.append({
            '게임 번호': game['game_number'],
            '시간': game['timestamp'].strftime("%H:%M:%S"),
            '선택 번호': f"{sorted(game['user_numbers'])} + {game['user_powerball']}",
            '당첨 번호': f"{game['winning_numbers']} + {game['winning_powerball']}",
            '등수': (game['prize_level'] if game['prize_level'] else '미당첨') + other_info,
            '상금': format_currency(game['prize_amount'])
        })
    
    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True)
    
    # 통계 정보
    if len(st.session_state.game_history) >= 3:
        st.subheader("📈 상세 통계")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        # 당첨 관련 통계
        winning_games = [game for game in st.session_state.game_history if game['prize_level']]
        total_games = len(st.session_state.game_history)
        other_winner_games = [game for game in st.session_state.game_history if game.get('other_winner', False)]
        
        with col_stat1:
            win_rate = len(winning_games) / total_games * 100
            st.metric("전체 당첨률", f"{win_rate:.1f}%")
        
        with col_stat2:
            if winning_games:
                avg_prize = sum(game['prize_amount'] for game in winning_games) / len(winning_games)
                st.metric("평균 당첨금", format_currency(avg_prize))
            else:
                st.metric("평균 당첨금", "$0")
        
        with col_stat3:
            avg_loss_per_game = (st.session_state.total_spent - st.session_state.total_winnings) / st.session_state.games_played
            st.metric("게임당 평균 손실", format_currency(avg_loss_per_game))
        
        with col_stat4:
            roi = (st.session_state.total_winnings / st.session_state.total_spent - 1) * 100 if st.session_state.total_spent > 0 else 0
            st.metric("투자 수익률", f"{roi:.1f}%")
        
        # 추가 통계
        if other_winner_games:
            st.info(f"🎰 다른 당첨자로 인한 잭팟 초기화: {len(other_winner_games)}번")
        
        # 등수별 당첨 현황
        st.subheader("🏆 등수별 당첨 현황")
        
        prize_counts = {}
        prize_earnings = {}
        
        for game in st.session_state.game_history:
            if game['prize_level']:
                level = game['prize_level']
                prize_counts[level] = prize_counts.get(level, 0) + 1
                prize_earnings[level] = prize_earnings.get(level, 0) + game['prize_amount']
        
        if prize_counts:
            level_names = {
                'jackpot': '잭팟', '2nd': '2등', '3rd': '3등', '4th': '4등', 
                '5th': '5등', '6th': '6등', '7th': '7등', '8th': '8등', '9th': '9등'
            }
            
            stat_data = []
            for level in ['jackpot', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']:
                if level in prize_counts:
                    stat_data.append({
                        '등수': level_names[level],
                        '당첨 횟수': prize_counts[level],
                        '총 당첨금': format_currency(prize_earnings[level]),
                        '당첨률': f"{(prize_counts[level] / total_games * 100):.2f}%"
                    })
            
            if stat_data:
                df_stats = pd.DataFrame(stat_data)
                st.dataframe(df_stats, use_container_width=True)
        else:
            st.info("아직 당첨 기록이 없습니다.")

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
        future_jackpots.append((temp_jackpot, increase))
    
    st.write("**다음 5번 이월 예상:**")
    for i, (future_jackpot, increase) in enumerate(future_jackpots, 1):
        if future_jackpot >= 1000000000:
            display = f"${future_jackpot/1000000000:.2f}B"
        else:
            display = f"${future_jackpot/1000000:.0f}M"
        st.write(f"{games_since + i}회: {display}")
        st.caption(f"증가: +${increase/1000000:.1f}M")
    
    # 대형 잭팟까지 예상 게임수
    st.write("**목표 잭팟까지 예상:**")
    targets = [100000000, 500000000, 1000000000]  # 1억, 5억, 10억
    target_names = ["1억 달러", "5억 달러", "10억 달러"]
    
    temp_jackpot = current
    temp_games = games_since
    
    for target, name in zip(targets, target_names):
        if current < target:
            games_needed = 0
            test_jackpot = temp_jackpot
            test_games = temp_games
            
            while test_jackpot < target and games_needed < 100:  # 최대 100게임
                test_games += 1
                games_needed += 1
                increase = calculate_jackpot_increase(test_jackpot, test_games)
                test_jackpot += increase
            
            if games_needed < 100:
                st.write(f"• {name}: 약 {games_needed}게임 후")
            else:
                st.write(f"• {name}: 100게임+ 후")
        else:
            st.write(f"• {name}: ✅ 달성!")
    
    # 다른 당첨자 확률 정보
    st.header("🎰 시스템 정보")
    current_jackpot = st.session_state.current_jackpot
    games_since_jackpot = st.session_state.games_since_jackpot
    
    # 다른 당첨자 확률 계산 (표시용)
    base_prob = 0.0001
    if current_jackpot > 1000000000:
        jackpot_mult = 50
    elif current_jackpot > 500000000:
        jackpot_mult = 25
    elif current_jackpot > 200000000:
        jackpot_mult = 10
    elif current_jackpot > 100000000:
        jackpot_mult = 5
    else:
        jackpot_mult = 1
    
    drought_mult = 1 + (games_since_jackpot / 100)
    final_prob = min(base_prob * jackpot_mult * drought_mult, 0.05)
    
    st.write(f"**다른 당첨자 확률:** {final_prob*100:.3f}%")
    st.caption("잭팟이 클수록, 오래 이월될수록 확률 증가")
    
    # 잭팟 증가량 정보
    next_increase = calculate_jackpot_increase(current_jackpot, games_since_jackpot + 1)
    st.write(f"**다음 게임 예상 증가:** ${next_increase/1000000:.1f}M")
    
    st.caption("💡 팁: 자동 플레이로 빠르게 여러 게임을 시도해보세요!")