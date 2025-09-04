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
            # 단일 게임 실행
            play_single_game(main_numbers, powerball_number)

else:  # 자동 플레이 모드
    if st.button("🚀 자동 플레이 시작", type="primary", use_container_width=True):
        # 자동 플레이 실행
        if auto_mode == "특정 등수 당첨까지":
            play_auto_until_prize(target_prize, max_games, auto_number_method, 
                                fixed_main_numbers if auto_number_method == "고정 번호 사용" else None,
                                fixed_powerball if auto_number_method == "고정 번호 사용" else None)
        elif auto_mode == "정해진 횟수만큼":
            play_auto_fixed_games(fixed_games, auto_number_method,
                                fixed_main_numbers if auto_number_method == "고정 번호 사용" else None,
                                fixed_powerball if auto_number_method == "고정 번호 사용" else None)
        else:  # 잭팟까지
            play_auto_until_jackpot(max_games, auto_number_method,
                                  fixed_main_numbers if auto_number_method == "고정 번호 사용" else None,
                                  fixed_powerball if auto_number_method == "고정 번호 사용" else None)

# 게임 실행 함수들
def play_single_game(main_numbers, powerball_number):
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
    
    # 잭팟 업데이트
    if prize_level == 'jackpot' or other_winner:
        if other_winner and prize_level != 'jackpot':
            st.warning("🎰 **다른 당첨자가 나타났습니다!** 잭팟이 초기화됩니다.")
        st.session_state.current_jackpot = 20000000  # 잭팟 리셋
        st.session_state.games_since_jackpot = 0
    else:
        # 잭팟 증가
        jackpot_increase = calculate_jackpot_increase(
            st.session_state.current_jackpot, 
            st.session_state.games_since_jackpot
        )
        st.session_state.current_jackpot += jackpot_increase
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
    display_game_result(main_numbers, powerball_number, winning_main, winning_powerball, 
                       prize_level, prize_amount, other_winner)

def play_auto_until_prize(target_prize, max_games, number_method, fixed_main=None, fixed_powerball=None):
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

def play_auto_fixed_games(game_count, number_method, fixed_main=None, fixed_powerball=None):
    """정해진 횟수만큼 자동 플레이"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    best_prize = None
    best_amount = 0
    
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
        else:
            jackpot_increase = calculate_jackpot_increase(st.session_state.current_jackpot, st.session_state.games_since_jackpot)
            st.session_state.current_jackpot += jackpot_increase
            st.session_state.games_since_jackpot += 1
        
        # 진행상황 업데이트
        progress_bar.progress((i + 1) / game_count)
        status_text.text(f"진행: {i + 1}/{game_count}게임 | 현재 잭팟: ${st.session_state.current_jackpot/1000000:.1f}M | 최고상금: ${best_amount:,}")
    
    # 결과 요약
    st.success(f"🎯 **{game_count}게임 자동 플레이 완료!**")
    if best_amount > 0:
        level_names = {
            'jackpot': '잭팟', '2nd': '2등', '3rd': '3등', '4th': '4등', 
            '5th': '5등', '6th': '6등', '7th': '7등', '8th': '8등', '9th': '9등'
        }
        st.info(f"🏆 최고 당첨: {level_names.get(best_prize, '알 수 없음')} - {format_currency(best_amount)}")
    else:
        st.info("😅 아쉽게도 당첨되지 않았습니다.")
    
    total_costimport streamlit as st
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

# 게임 히스토리 표시 (기존 코드와 동일하지만 other_winner 정보 추가)
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
    st.dataframe(df, use_container_width=True)기화", type="secondary"):
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