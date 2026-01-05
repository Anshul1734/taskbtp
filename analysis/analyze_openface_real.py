"""
Analyze real OpenFace AU extraction results from JAFFE dataset.
Adds emotion labels from filenames and generates statistics and visualizations.
"""
import os
import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

# Add analysis module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


def parse_emotion_from_filename(filename):
    """Extract emotion from JAFFE filename format: SUBJECT.EMOTION#.ID"""
    try:
        parts = filename.replace('.jpg', '').split('.')
        emotion_code = parts[1][:2]
        emotion_map = {
            'HA': 'happy',
            'SA': 'sad',
            'NE': 'neutral',
            'AN': 'anger',
            'DI': 'disgust',
            'FE': 'fear',
            'SU': 'surprise'
        }
        return emotion_map.get(emotion_code, 'unknown')
    except:
        return 'unknown'


def load_and_preprocess(csv_file):
    """Load OpenFace CSV, add emotion labels, and normalize."""
    print(f"Loading: {csv_file}")
    
    # Read OpenFace CSV
    df = pd.read_csv(csv_file)
    
    # Rename columns to remove leading spaces
    df.columns = [col.strip() for col in df.columns]
    
    # Extract AU columns
    au_cols = [col for col in df.columns if 'AU' in col and '_r' in col]
    
    print(f"Found {len(au_cols)} AU columns: {au_cols[:5]}...")
    
    # Extract emotion from filename
    if 'filename' in df.columns:
        df['emotion_label'] = df['filename'].apply(parse_emotion_from_filename)
    else:
        print("Warning: 'filename' column not found!")
        df['emotion_label'] = 'unknown'
    
    print(f"Loaded {len(df)} rows, AUs: {au_cols[:5]}")
    print(f"Emotion distribution:\n{df['emotion_label'].value_counts()}")
    
    # Filter to only happy and sad for primary analysis
    df_filtered = df[df['emotion_label'].isin(['happy', 'sad'])].copy()
    print(f"\nFiltered to Happy + Sad: {len(df_filtered)} rows")
    
    # Handle missing values
    df_filtered[au_cols] = df_filtered[au_cols].fillna(df_filtered[au_cols].mean())
    
    return df_filtered, au_cols


def compute_stats(df, au_cols, out_dir):
    """Compute statistics for happy vs sad emotions."""
    os.makedirs(out_dir, exist_ok=True)
    
    print("\nComputing statistics...")
    
    # Summary statistics
    summary = df.groupby('emotion_label')[au_cols].agg(['mean', 'std', 'count']).round(4)
    print(f"\nSummary statistics:")
    print(summary.head(10))
    
    # Save summary
    summary.to_csv(os.path.join(out_dir, 'au_summary_by_emotion_real.csv'))
    
    # T-tests (Happy vs Sad)
    happy_data = df[df['emotion_label'] == 'happy'][au_cols]
    sad_data = df[df['emotion_label'] == 'sad'][au_cols]
    
    ttests = []
    for au in au_cols:
        if happy_data[au].std() > 0 and sad_data[au].std() > 0:
            t_stat, p_val = stats.ttest_ind(happy_data[au].dropna(), sad_data[au].dropna())
            ttests.append({
                'AU': au,
                't_statistic': t_stat,
                'p_value': p_val,
                'significant': 'Yes' if p_val < 0.05 else 'No'
            })
    
    ttest_df = pd.DataFrame(ttests)
    print(f"\nT-test results (Happy vs Sad):")
    print(ttest_df.head(15))
    ttest_df.to_csv(os.path.join(out_dir, 'au_ttests_real.csv'), index=False)
    
    return summary, ttest_df


def plot_distributions(df, au_cols, out_dir):
    """Generate distribution plots."""
    os.makedirs(out_dir, exist_ok=True)
    
    # Select key AUs for visualization
    key_aus = ['AU06_r', 'AU12_r', 'AU01_r', 'AU04_r', 'AU15_r']
    available_aus = [au for au in key_aus if au in au_cols]
    
    if not available_aus:
        print("Warning: No key AUs found for plotting")
        return
    
    print(f"\nGenerating distribution plots for: {available_aus}")
    
    # Violin plot
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.violinplot(data=df, x='emotion_label', y=available_aus[0], ax=ax)
    ax.set_title(f'{available_aus[0]} Distribution by Emotion (OpenFace Real)')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'violin_aus_by_emotion_real.png'), dpi=150)
    print(f"✓ Saved: violin_aus_by_emotion_real.png")
    plt.close()
    
    # Multiple AU boxplot
    fig, axes = plt.subplots(1, len(available_aus), figsize=(15, 4))
    if len(available_aus) == 1:
        axes = [axes]
    
    for idx, au in enumerate(available_aus):
        sns.boxplot(data=df, x='emotion_label', y=au, ax=axes[idx])
        axes[idx].set_title(f'{au}')
    
    plt.suptitle('AU Distributions by Emotion (OpenFace Real)', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'boxplots_real.png'), dpi=150)
    print(f"✓ Saved: boxplots_real.png")
    plt.close()
    
    # Bar chart of mean AUs
    means = df.groupby('emotion_label')[available_aus].mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    means.T.plot(kind='bar', ax=ax)
    ax.set_title('Mean AU Intensities by Emotion (OpenFace Real)')
    ax.set_ylabel('Intensity')
    ax.set_xlabel('Action Unit')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'mean_au_by_emotion_real.png'), dpi=150)
    print(f"✓ Saved: mean_au_by_emotion_real.png")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Analyze real OpenFace AU output')
    parser.add_argument('--input', required=True, help='Input OpenFace CSV file')
    parser.add_argument('--out', default='outputs_real', help='Output directory')
    args = parser.parse_args()
    
    # Load and preprocess
    df, au_cols = load_and_preprocess(args.input)
    
    # Compute statistics
    summary, ttest_df = compute_stats(df, au_cols, args.out)
    
    # Generate plots
    plot_distributions(df, au_cols, args.out)
    
    print("\n✓ Analysis complete!")
    print(f"✓ Results saved to: {args.out}/")


if __name__ == '__main__':
    main()
