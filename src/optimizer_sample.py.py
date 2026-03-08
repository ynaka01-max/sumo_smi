import pandas as pd
import networkx as nx
import itertools

def solve_torikumi_matching(df_master: pd.DataFrame) -> list:
    G = nx.Graph()
    for idx, row in df_master.iterrows():
        G.add_node(row['Name'], heya=row['Heya'], score=row['Score'])
        
    for rikishi_A, rikishi_B in itertools.combinations(df_master['Name'], 2):
        data_A = G.nodes[rikishi_A]
        data_B = G.nodes[rikishi_B]
        
        if data_A['heya'] == data_B['heya']:
            continue
        cost = abs(data_A['score'] - data_B['score'])
        
        weight = -cost
        
        G.add_edge(rikishi_A, rikishi_B, weight=weight, cost=cost)

    print("最適化アルゴリズム（Blossom）を実行中...")
    matching = nx.max_weight_matching(G, maxcardinality=True)
    
    results = []
    total_cost = 0.0
    
    for pair in matching:
        rikishi_1, rikishi_2 = pair
        edge_data = G.get_edge_data(rikishi_1, rikishi_2)
        match_cost = edge_data['cost']
        total_cost += match_cost
        
        results.append({
            '力士1': rikishi_1,
            '力士2': rikishi_2,
            'スコア差(コスト)': round(match_cost, 2)
        })
        
    print("マッチング完了")
    print(f"全体の総コスト: {round(total_cost, 2)}")
    return results

# --- テスト実行用 ---
if __name__ == "__main__":
    # ダミーデータ（あなたが考えた1次元スコアと部屋情報）
    dummy_data = [
        {'Name': '照ノ富士', 'Heya': '伊勢ヶ濱', 'Score': 0.0},
        {'Name': '琴櫻',     'Heya': '佐渡ヶ嶽', 'Score': 1.0},
        {'Name': '豊昇龍',   'Heya': '立浪',     'Score': 1.5},
        {'Name': '大の里',   'Heya': '二所ノ関', 'Score': 2.0},
        {'Name': '阿炎',     'Heya': '錣山',     'Score': 3.0},
        {'Name': '大栄翔',   'Heya': '追手風',   'Score': 3.5},
        {'Name': '尊富士',   'Heya': '伊勢ヶ濱', 'Score': 4.0}, 
        {'Name': '王鵬',     'Heya': '大嶽',     'Score': 4.5},
    ]
    df_dummy = pd.DataFrame(dummy_data)
    
    matchups = solve_torikumi_matching(df_dummy)
    
    df_results = pd.DataFrame(matchups)
    df_results = df_results.sort_values('スコア差(コスト)')
    print("\n--- 生成された取組（最適解） ---")
    print(df_results.to_string(index=False))