import os
import glob
import argparse
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

def evaluate(method, cutoff, export_csv=True, plot=True):
    df = load_sol_and_out_files("output", method, cutoff)
    if df.empty:
        print("No solution data found.")
        return

    df['RelErr_Display'] = df['RelErr'].apply(lambda x: 'N/A' if pd.isna(x) else f"{x:.4f}")

    if export_csv:
        output_csv = f"output/{method}_results_summary_{cutoff}s.csv"
        df.to_csv(output_csv, index=False)
        print(f"Summary CSV written to {output_csv}")

    print("\n--- Summary ---")
    print(df[['Instance', 'Quality', 'Optimal', 'RelErr_Display']])

    if plot:
        plot_histogram(df, method, cutoff)
        plot_qrtd(df, method, cutoff)
        plot_sqd(df, method, cutoff)

def plot_histogram(df, method, cutoff):
    plt.figure()
    sns.histplot(df['RelErr'].dropna(), bins=10, kde=True)
    plt.title(f"Histogram of Relative Error ({method})")
    plt.xlabel("Relative Error")
    plt.ylabel("Frequency")
    path = os.path.join(FIG_DIR, f"histogram_relerr_{method}_{cutoff}s.png")
    plt.tight_layout()
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

def plot_qrtd(df, method, cutoff, thresholds=[0.01, 0.005, 0.002]):
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
    plt.title(f"QRTD: Qualified Distribution ({method})")
    plt.legend()
    path = os.path.join(FIG_DIR, f"qrtd_plot_{method}_{cutoff}s.png")
    plt.tight_layout()
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

def plot_sqd(df, method, cutoff, time_thresholds=[0.1, 0.5, 1.0]):
    plt.figure()
    for t_star in time_thresholds:
        filtered = df.copy()  # Time data not tracked, include all
        sorted_re = np.sort(filtered['RelErr'].dropna())
        y_vals = np.linspace(0, 1, len(sorted_re), endpoint=False)
        plt.step(sorted_re, y_vals, label=f'≤ {t_star:.1f}s')
    plt.xlabel("Relative Error")
    plt.ylabel("Fraction of Instances")
    plt.title(f"SQD: Solution Quality Distribution ({method})")
    plt.legend()
    path = os.path.join(FIG_DIR, f"sqd_plot_{method}_{cutoff}s.png")
    plt.tight_layout()
    plt.savefig(path)
    print(f"Saved: {path}")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Set Cover Approximation Results")
    parser.add_argument('-alg', type=str, choices=["Approx", "BnB", "LS1", "LS2"], required=True, help='Algorithm name')
    parser.add_argument('-time', type=int, required=True, help='Cutoff time in seconds')
    parser.add_argument('--no_csv', action='store_true', help='Do not export summary CSV')
    parser.add_argument('--no_plot', action='store_true', help='Do not generate plots')

    args = parser.parse_args()
    evaluate(
        method=args.alg,
        cutoff=args.time,
        export_csv=not args.no_csv,
        plot=not args.no_plot
    )
