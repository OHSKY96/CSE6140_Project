# evaluate_gsc.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)

def load_data(csv_path):
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return None
    df = pd.read_csv(csv_path)
    df['RelErr'] = pd.to_numeric(df['RelErr_Display'], errors='coerce')
    df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
    df['Quality'] = pd.to_numeric(df['Quality'], errors='coerce')
    return df

def show_summary(df):
    print("\n--- Summary Statistics ---")
    print(df.describe())

def plot_histograms(df):
    plt.figure()
    sns.histplot(df['RelErr'].dropna(), bins=10, kde=True)
    plt.title("Histogram of Relative Error")
    plt.xlabel("Relative Error")
    plt.ylabel("Frequency")
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "histogram_relative_error.png")
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

def plot_boxplots(df):
    plt.figure()
    sns.boxplot(data=df, x='Method', y='Time')
    plt.title("Box Plot of Execution Times by Method")
    plt.ylabel("Time (s)")
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "boxplot_execution_times.png")
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

def plot_scatter_quality_vs_relerr(df):
    plt.figure()
    sns.scatterplot(data=df, x='Quality', y='RelErr')
    plt.title("Solution Size vs Relative Error")
    plt.xlabel("Solution Size (Quality)")
    plt.ylabel("Relative Error")
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "scatter_quality_vs_relerr.png")
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

def plot_qrtd(df, thresholds=[0.01, 0.005, 0.002]):
    plt.figure()
    for q_star in thresholds:
        filtered = df[df['RelErr'].notna()].copy()
        filtered['Qualified'] = filtered['RelErr'] <= q_star
        sorted_times = np.sort(filtered['Time'])
        success_flags = filtered.sort_values('Time')['Qualified'].values
        cum_success = np.cumsum(success_flags) / len(success_flags)
        plt.step(sorted_times, cum_success, label=f'q* ≤ {q_star:.2%}')
    plt.xlabel("Runtime (seconds)")
    plt.ylabel("Fraction of Instances Solved")
    plt.title("QRTD: Qualified Runtime Distribution")
    plt.legend()
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "qrtd_plot.png")
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

def plot_sqd(df, time_thresholds=[0.1, 0.5, 1.0]):
    plt.figure()
    for t_star in time_thresholds:
        filtered = df[df['Time'] <= t_star]
        if filtered.empty:
            continue
        sorted_re = np.sort(filtered['RelErr'].dropna())
        y_vals = np.linspace(0, 1, len(sorted_re), endpoint=False)
        plt.step(sorted_re, y_vals, label=f'Time ≤ {t_star:.1f}s')
    plt.xlabel("Relative Error")
    plt.ylabel("Fraction of Instances")
    plt.title("SQD: Solution Quality Distribution")
    plt.legend()
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "sqd_plot.png")
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

def evaluate(csv_path):
    df = load_data(csv_path)
    if df is None:
        return

    show_summary(df)
    plot_histograms(df)
    plot_boxplots(df)
    plot_scatter_quality_vs_relerr(df)
    plot_qrtd(df)
    plot_sqd(df)


if __name__ == "__main__":
    csv_file = os.path.join("output", "greedy_results_summary.csv")
    evaluate(csv_file)
