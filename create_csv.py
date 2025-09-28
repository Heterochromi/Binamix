#!/usr/bin/env python3
"""
Script to create separate CSV files for each directory containing audio files.
Each subdirectory gets its own CSV file with filename and class columns.
"""

import os
import csv
import argparse
from pathlib import Path


def get_audio_files_by_directory(directory):
    """
    Recursively find all audio files in the given directory.
    Returns a dictionary: {class_name: [(filename, full_path), ...]}
    """
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.opus'}
    files_by_class = {}

    directory_path = Path(directory)

    if not directory_path.exists():
        raise FileNotFoundError(f"Directory '{directory}' does not exist")

    # Walk through all subdirectories
    for root, dirs, files in os.walk(directory_path):
        root_path = Path(root)

        # Skip the root directory itself - we want files in subdirectories
        if root_path == directory_path:
            continue

        # Get the immediate parent directory name as the class
        class_name = root_path.name

        for file in files:
            file_path = root_path / file

            # Check if it's an audio file
            if file_path.suffix.lower() in audio_extensions:
                if class_name not in files_by_class:
                    files_by_class[class_name] = []
                files_by_class[class_name].append((file, str(file_path)))

    return files_by_class


def create_csv_for_class(class_name, files_data, output_dir):
    """
    Create a CSV file for a specific class.
    """
    output_file = Path(output_dir) / f"{class_name}.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(['name', 'class'])

        # Write data rows
        for filename, full_path in files_data:
            writer.writerow([filename, class_name])

    return output_file, len(files_data)


def main():
    parser = argparse.ArgumentParser(
        description='Create separate CSV files for each directory containing audio files'
    )
    parser.add_argument(
        'directory',
        help='Path to the directory containing subdirectories with audio files'
    )
    parser.add_argument(
        '-o', '--output-dir',
        default='.',
        help='Output directory for CSV files (default: current directory)'
    )
    parser.add_argument(
        '--show-stats',
        action='store_true',
        help='Show statistics about classes found'
    )

    args = parser.parse_args()

    try:
        # Get all audio files organized by class
        files_by_class = get_audio_files_by_directory(args.directory)

        if not files_by_class:
            print("No audio files found in the specified directory structure.")
            return

        # Create output directory if it doesn't exist
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        total_files = 0
        csv_files_created = []

        # Create a CSV file for each class
        for class_name, files_data in files_by_class.items():
            csv_file, file_count = create_csv_for_class(class_name, files_data, output_dir)
            csv_files_created.append(csv_file)
            total_files += file_count
            print(f"Created: {csv_file} ({file_count} files)")

        print(f"\nTotal CSV files created: {len(csv_files_created)}")
        print(f"Total audio files processed: {total_files}")

        # Show statistics if requested
        if args.show_stats:
            print("\nClass Statistics:")
            print("-" * 50)

            for class_name, files_data in sorted(files_by_class.items()):
                print(f"{class_name}: {len(files_data)} files")

            print(f"\nTotal classes: {len(files_by_class)}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
