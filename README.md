# Sumo Smi　(Sumo Matching Intelligence, SMI)
**大相撲取組編成の数理最適化と「意図」のリバースエンジニアリング**

## プロジェクト概要(Overview)
本プロジェクトは、大相撲の「取組編成（マッチング）」を高度な**制約付き組み合わせ最適化問題（一般グラフの最小重み完全マッチング）**として定式化し、編成委員会の「暗黙の意図」をデータから抽出・学習する数理モデリングの取り組みです。

最終的には、ここで構築したネットワーク構造の配置最適化モデルを別の課題へ応用するための基盤と位置付けています。

## 数理モデリング(Mathematical Formulation)

大相撲の編成は、単なる二部グラフの問題ではありません。同片（東同士・西同士）の対戦も許容されるため、単一のノード集合における完全マッチング問題として解く必要があります。

### 1. 特徴量エンジニアリング: 1次元番付スコア ($S_i$)
カテゴリカル変数である番付（東・西）を、距離計算可能な連続値にマッピングします。
力士 $i$ の階級基本値を $R_i \in \{0, 1, 2, \dots\}$、東西フラグを $W_i \in \{0(\text{東}), 1(\text{西})\}$ としたとき、実力スコア $S_i$ を以下で定義します。
$$S_i = R_i + 0.5 \cdot W_i$$

### 2. コスト関数 (Cost Function)
力士 $i$ と力士 $j$ を対戦させる際の実力差（コスト） $C_{ij}$ を定義します。
場所の進行に伴い、編成の意図が「番付重視」から「勝敗重視」へ遷移することを表現するため、動的重みパラメータ $\alpha_t, \beta_t$ を導入します。


$$C_{ij} = \alpha_t |S_i - S_j| + \beta_t |\text{Win}_i - \text{Win}_j| - \gamma \cdot \text{sim}(T_i, T_j)$$


*(※ $\gamma$項は将来的な「取り口（戦型）の親和性ボーナス」)*

### 3. 最適化問題の定式化 (Optimization Problem)
決定変数を $x_{ij} \in \{0, 1\}$ （力士 $i, j$ が対戦する場合 $1$）とします。

**目的関数:**
$$\min \sum_{i} \sum_{j} C_{ij} x_{ij}$$

**制約条件:**
1. 完全マッチング（全員が1日1回対戦する）:
   $$\forall i, \sum_{j} x_{ij} = 1$$
2. 同部屋対決の禁止（ハード制約）:
   $$\text{If } \text{Heya}_i = \text{Heya}_j, \text{ then } x_{ij} = 0 \text{ (or } C_{ij} = \infty)$$



## システム・アーキテクチャ (System Architecture)

1. **データ取得・前処理層 (`scraper_preprocessor.py`)**
   - Webスクレイピングによる日次データの自動取得とクリーニング。
   - 勝敗画像タグの文字列パースと、1次元スコア（$S_i$）への変換。
2. **最適化ソルバー (`optimizer.py`)**
   - `networkx` を用いた一般グラフの Blossom Algorithm の実装。
   - 最大重みマッチングを逆転させた、最小コスト対戦カードの生成。
3. **シミュレーション層 (`simulator.py`) - *WIP***
   - モンテカルロ法と Bradley-Terry モデルを用いた、場所中盤からの動的な優勝確率予測。

## ディレクトリ構成 (Directory Structure)
```text
sumo_smi/
├── data/
│   ├── raw/             # 生のスクレイピングデータ
│   ├── master/          # 力士・部屋マスターデータ
│   └── daily/           # 日次の勝敗トランザクション
├── src/
│   ├── scraper_preprocessor.py  # データ取得・特徴量生成・クレンジング
│   ├── optimizer.py     # 組み合わせ最適化ソルバー (Blossom Algorithm)
│   └── simulator.py     # 優勝確率モンテカルロシミュレータ
├── notebooks/           # EDA・パラメータチューニング検証用
├── README.md
├── .gitignore
└── requirements.txt
