"""
Helper to prepare CK+ sequences mapping to emotion labels for OpenFace processing.

Usage:
  python scripts/prepare_ckplus.py --ckdir PATH_TO_CKPLUS --out mapping.csv

This script attempts to locate emotion label files and create a CSV mapping sequence -> emotion.
Modify as needed for your CK+ layout.
"""
import os
import argparse
import csv


def find_emotion_labels(ckdir):
    # CK+ typically stores sequences under 'cohn-kanade-images' and labels in 'Emotion' or via separate files.
    # This helper looks for any file named 'emotion.txt' or directories named by subject/sequence containing a file 'emotion.txt'
    mappings = []
    for root, dirs, files in os.walk(ckdir):
        for fname in files:
            if fname.lower() in ('emotion.txt', 'label.txt', 'emotions.txt'):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as fh:
                        label = fh.read().strip()
                except Exception:
                    continue
                # sequence id as folder name
                seq = os.path.basename(root)
                mappings.append((seq, label, fpath))
    return mappings


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ckdir', required=True)
    p.add_argument('--out', default='ckplus_mapping.csv')
    args = p.parse_args()

    mappings = find_emotion_labels(args.ckdir)
    if not mappings:
        print('No emotion label files found. You may need to adapt this helper to your CK+ layout.')
        return

    with open(args.out, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['sequence','emotion_label','source_file'])
        for seq, label, src in mappings:
            writer.writerow([seq, label, src])

    print('Wrote mapping to', args.out)


if __name__ == '__main__':
    main()
