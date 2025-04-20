import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)

def load_sol_and_out_files(output_dir, method_name, cutoff_time):
    results = []
    pattern = f"*_{method_name}_{cutoff_time}.sol"
    sol_files = sorted(glob.glob(os.path.join(output_dir, pattern)))

    for sol_file in sol_files:
        base = os.path.basename(sol_file).replace(f"_{method_name}_{cutoff_time}.sol", "")
        out_file = os.path.join("data", f"{base}.out")

        try:
            with open(sol_file, 'r') as f:
                quality = int(f.readline().strip())

            opt_val = None
            if os.path.exists(out_file):
                with open(out_file, 'r') as f:
                    opt_val = int(f.readline().strip())

            rel_err = None
            if opt_val is not None:
                rel_err = (quality - opt_val) / opt_val if opt_val > 0 else float('inf')

            results.append({
                'Instance': base,
                'Method': method_name,
                'Quality': quality,
                'Optimal': opt_val if opt_val is not None else 'N/A',
                'RelErr': rel_err
            })
        except Exception as e:
            print(f"Error processing {sol_file}: {e}")
            continue

    return pd.DataFrame(results)

def evaluate(method="Approx", cutoff=600, export_csv=True, plot=True):
    df = load_sol_and_out_files("output", method, cutoff)
    if df.empty:
        print("No solution data found.")
        return

    df['RelErr_Display'] = df['RelErr'].apply(lambda x: 'N/A' if pd.isna(x) else f"{x:.4f}")

    if export_csv:
        output_csv = f"output/{method}_results_summary.csv"
        df.to_csv(output_csv, index=False)
        print(f"Summary CSV written to {output_csv}")

    print("\n--- Summary ---")
    print(df[['Instance', 'Quality', 'Optimal', 'RelErr_Display']])

    if plot:
        plot_histogram(df)
        plot_qrtd(df)
        plot_sqd(df)

def plot_histogram(df):
    plt.figure()
    sns.histplot(df['RelErr'].dropna(), bins=10, kde=True)
    plt.title("Histogram of Relative Error")
    plt.xlabel("Relative Error")
    plt.ylabel("Frequency")
    path = os.path.join(FIG_DIR, "histogram_relerr.png")
    plt.tight_layout()
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

def plot_qrtd(df, thresholds=[0.01, 0.005, 0.002]):
    plt.figure()
    for q_star in thresholds:
        filtered = df[df['RelErr'].notna()].copy()
        filtered['Qualified'] = filtered['RelErr'] <= q_star
        sorted_quality = np.sort(filtered['Quality'])
        success_flags = filtered.sort_values('Quality')['Qualified'].values
        cum_success = np.cumsum(success_flags) / len(success_flags)
        plt.step(sorted_quality, cum_success, label=f'q* ≤ {q_star:.2%}')
    plt.xlabel("Solution Size")
    plt.ylabel("Fraction of Qualified Solutions")
    plt.title("QRTD: Qualified Runtime Distribution (by Quality)")
    plt.legend()
    path = os.path.join(FIG_DIR, "qrtd_plot.png")
    plt.tight_layout()
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

def plot_sqd(df, time_thresholds=[0.1, 0.5, 1.0]):
    plt.figure()
    for t_star in time_thresholds:
        filtered = df.copy()  # Time not available; skipping time filter
        sorted_re = np.sort(filtered['RelErr'].dropna())
        y_vals = np.linspace(0, 1, len(sorted_re), endpoint=False)
        plt.step(sorted_re, y_vals, label=f'≤ {t_star:.1f}s')
    plt.xlabel("Relative Error")
    plt.ylabel("Fraction of Instances")
    plt.title("SQD: Solution Quality Distribution")
    plt.legend()
    path = os.path.join(FIG_DIR, "sqd_plot.png")
    plt.tight_layout()
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

if __name__ == "__main__":
    evaluate(method="Approx", cutoff=600)

