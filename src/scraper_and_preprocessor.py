import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

def fetch_and_clean_banzuke(year: int, month: int) -> pd.DataFrame:
    url = f"https://sumodb.sumogames.de/Banzuke.aspx?b={year}{month:02d}&l=j"
    print(f"Fetching data from: {url} ...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        raise ConnectionError(f"HTTP Error: {res.status_code}")
        
    tables = pd.read_html(res.text)
    df_raw = tables[0]
    
    df_raw.columns = range(df_raw.shape[1])
    
    rikishi_list = []
    
    for _, row in df_raw.iterrows():
        east_name = str(row[1]).strip()
        rank_str = str(row[2]).strip()
        west_name = str(row[3]).strip()
        if rank_str == 'nan' or rank_str == '位':
            continue
            
        if east_name != 'nan' and east_name != 'None':
            rikishi_list.append({
                'Name': east_name,
                'Rank_Raw': rank_str,
                'Direction': '東',
                'W_Flag': 0.0  # 東はそのまま
            })
            
        if west_name != 'nan' and west_name != 'None':
            rikishi_list.append({
                'Name': west_name,
                'Rank_Raw': rank_str,
                'Direction': '西',
                'W_Flag': 0.5  # 西は0.5落とす
            })

    df = pd.DataFrame(rikishi_list)
    return df

def calculate_1d_score(rank_str: str, w_flag: float) -> float:
    base_score = 0.0
    
    if '横綱' in rank_str:
        base_score = 0.0
    elif '大関' in rank_str:
        base_score = 1.0
    elif '関脇' in rank_str:
        base_score = 2.0
    elif '小結' in rank_str:
        base_score = 3.0
    elif '前' in rank_str:
        match = re.search(r'\d+', rank_str)
        if match:
            base_score = 3.0 + float(match.group())
    else:
        return None

    return base_score + w_flag

def fetch_daily_torikumi(year: int, month: int, day: int):
    url = f"https://sumodb.sumogames.de/Results.aspx?b={year}{month:02d}&d={day}&l=j"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {year}/{month} Day {day}: {e}")
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    
    tk_table = soup.find('table', class_='tk_table')
    if not tk_table:
        return []

    daily_results = []
    
    for row in tk_table.find_all('tr'):
        east_td = row.find('td', class_='tk_east')
        west_td = row.find('td', class_='tk_west')
        kekka_tds = row.find_all('td', class_='tk_kekka')
        
        if east_td and west_td and len(kekka_tds) == 2:
            east_name_tag = east_td.find('a')
            west_name_tag = west_td.find('a')
            
            if not east_name_tag or not west_name_tag:
                continue
            east_name = east_td.get_text(strip=True)
            west_name = west_td.get_text(strip=True)

            east_img = kekka_tds[0].find('img')
            west_img = kekka_tds[1].find('img')
            
            east_win = 1 if east_img and 'shiro' in east_img.get('src', '') else 0
            west_win = 1 if west_img and 'shiro' in west_img.get('src', '') else 0
            kimarite_td = row.find('td', class_='tk_kim')
            kimarite = ""
            if kimarite_td:
                kimarite = "".join(kimarite_td.find_all(text=True, recursive=False)).strip()
                
            daily_results.append({
                'Year': year,
                'Month': month,
                'Day': day,
                'East': east_name,
                'West': west_name,
                'East_Win': east_win,
                'West_Win': west_win,
                'Kimarite': kimarite
            })
            
    return daily_results

def run_5years_scraper():
    years = range(2021, 2026)
    months = [1, 3, 5, 7, 9, 11]
    days = range(1, 16)
    
    all_results_torikumi = []
    os.makedirs('../data/raw/banzuke', exist_ok=True)
    os.makedirs('../data/raw/torikumi', exist_ok=True)
    print("5年分スクレイピングを開始します。")
    for y in years:
        for m in months:
            print(f"Fetching {y}年 {m}月場所 ", end="")
            banzuke = fetch_and_clean_banzuke(y, m)
            banzuke['Score'] = banzuke.apply(
                lambda row: calculate_1d_score(row['Rank_Raw'], row['W_Flag']), axis=1
            )
            banzuke = banzuke.sort_values('Score').reset_index(drop=True)
            if banzuke.shape[0]>0:
                file_name = f"../data/raw/banzuke/banzuke_{y}{m:02d}.csv"
                banzuke.to_csv(file_name, index=False, encoding='utf-8-sig')
                print("番付データ: 保存")
            else:
                print("番付データ: なし")
            for d in days:
                results = fetch_daily_torikumi(y, m, d)
                all_results_torikumi.extend(results)
                time.sleep(2)
            df_torikumi = pd.DataFrame(all_results_torikumi)
            if df_torikumi.shape[0]>0:
                file_name = f"../data/raw/torikumi/torikumi_{y}{m:02d}.csv"
                df_torikumi.to_csv(file_name, index=False, encoding='utf-8-sig')
                print("取組データ: 保存")
            else:
                print("取組データ: なし")
                
    print(f"完了")

if __name__ == "__main__":
    run_5years_scraper()
    print(df_master.head(10))
    print(f"\n総数: {len(df_master)}名")