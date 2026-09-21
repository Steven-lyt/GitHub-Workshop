import argparse
import sys

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "SimHei", "Arial Unicode MS"]
matplotlib.rcParams["axes.unicode_minus"] = False

SCORE_COLUMN_CANDIDATES = ["score", "Score", "SCORE", "分數", "分数", "成績", "成绩"]


def find_score_column(df, column_arg):
    if column_arg:
        if column_arg not in df.columns:
            raise ValueError(f"找不到欄位「{column_arg}」，CSV 欄位有：{list(df.columns)}")
        return column_arg

    for name in SCORE_COLUMN_CANDIDATES:
        if name in df.columns:
            return name

    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) == 0:
        raise ValueError("CSV 中找不到數字欄位，請用 --column 指定分數欄位")
    return numeric_cols[0]


def main():
    parser = argparse.ArgumentParser(description="計算 CSV 分數統計並畫出分數分布長條圖")
    parser.add_argument("csv_path", help="CSV 檔案路徑")
    parser.add_argument("--column", help="分數欄位名稱（不指定則自動偵測）")
    parser.add_argument("--output", default="score_distribution.png", help="輸出圖檔路徑")
    args = parser.parse_args()

    df = pd.read_csv(args.csv_path)
    score_col = find_score_column(df, args.column)
    scores = df[score_col].dropna()

    if scores.empty:
        print("錯誤：沒有可用的分數資料", file=sys.stderr)
        sys.exit(1)

    avg_score = scores.mean()
    max_score = scores.max()
    min_score = scores.min()

    print(f"分數欄位：{score_col}")
    print(f"樣本數：{len(scores)}")
    print(f"平均分：{avg_score:.2f}")
    print(f"最高分：{max_score:.2f}")
    print(f"最低分：{min_score:.2f}")

    if scores.min() >= 0 and scores.max() <= 100:
        bins = [0, 60, 70, 80, 90, 101]
        labels = ["0-59", "60-69", "70-79", "80-89", "90-100"]
        grouped = pd.cut(scores, bins=bins, labels=labels, right=False)
    else:
        grouped = pd.cut(scores, bins=10)

    counts = grouped.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(counts.index.astype(str), counts.values, color="#4C72B0")
    ax.set_xlabel("分數區間")
    ax.set_ylabel("人數")
    ax.set_title(f"分數分布（{score_col}）")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for i, v in enumerate(counts.values):
        ax.text(i, v, str(v), ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(args.output, dpi=150)
    print(f"圖表已儲存：{args.output}")
    plt.show()


if __name__ == "__main__":
    main()
