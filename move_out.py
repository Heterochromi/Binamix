import os
import shutil
from pathlib import Path
import csv


def move_files_to_parent(root_directory, create_csv=True, dry_run=False):
    """
    Move all files from the given directory and its subdirectories up to the parent directory.
    Optionally logs them in a CSV file.

    Args:
        root_directory (str): The directory whose contents will be moved up.
        create_csv (bool): If True, creates or appends to a CSV file with moved file info.
        dry_run (bool): If True, only print what would be done without actually moving files.

    Returns:
        tuple: (moved_count, skipped_count, error_count)
    """
    root_path = Path(root_directory)

    if not root_path.exists():
        raise FileNotFoundError(f"Error: '{root_directory}' does not exist")

    if not root_path.is_dir():
        raise NotADirectoryError(f"Error: '{root_directory}' is not a directory")

    # --- Start of new logic ---
    # The destination for the files is the parent of the specified directory.
    target_root_path = root_path.parent
    # --- End of new logic ---

    moved_count = 0
    skipped_count = 0
    error_count = 0

    print(f"Source directory: {root_path.absolute()}")
    print(f"Target directory: {target_root_path.absolute()}")
    print(f"Dry run mode: {'ON' if dry_run else 'OFF'}")
    print("-" * 50)

    csv_writer = None
    csv_file = None
    csv_path = None

    if create_csv:
        # --- Start of new logic ---
        # The CSV is created in the target directory.
        csv_path = target_root_path / 'moved_files.csv'
        # --- End of new logic ---
        file_exists = csv_path.exists()

        csv_file = open(csv_path, 'a', newline='')
        csv_writer = csv.writer(csv_file)

        if not file_exists:
            csv_writer.writerow(['name', 'class'])

    try:
        # Walk through all subdirectories
        for current_dir, subdirs, files in os.walk(root_directory):
            current_path = Path(current_dir)

            # The class is the name of the directory the file is in.
            class_name = current_path.name
            print(f"\nProcessing directory: {current_path.relative_to(root_path.parent)}")

            if not files:
                print("  No files found in this directory.")

            for file in files:
                # --- Start of new logic ---
                # Skip the CSV file itself if it's in the source directory
                if create_csv and (current_path / file) == csv_path:
                    continue
                # --- End of new logic ---

                source_file = current_path / file
                # --- Start of new logic ---
                # Target file is in the parent directory.
                target_file = target_root_path / file
                # --- End of new logic ---

                if source_file.name == 'awp':
                    skipped_count += 1
                    print(f"  Skipping file: {file} (reserved name)")
                    continue

                try:
                    counter = 1
                    original_target = target_file
                    while target_file.exists():
                        name = original_target.stem
                        suffix = original_target.suffix
                        # --- Start of new logic ---
                        # Ensure renamed files are also placed in the parent directory.
                        target_file = target_root_path / f"{name}_{counter}{suffix}"
                        # --- End of new logic ---
                        counter += 1

                    if dry_run:
                        print(f"  Would move: {source_file.relative_to(target_root_path)} -> {target_file.name}")
                    else:
                        print(f"  Moving: {source_file.relative_to(target_root_path)} -> {target_file.name}")
                        shutil.move(str(source_file), str(target_file))

                    if create_csv and csv_writer:
                        csv_writer.writerow([target_file.name, class_name])

                    moved_count += 1

                except Exception as e:
                    print(f"  Error moving {source_file.relative_to(target_root_path)}: {e}")
                    error_count += 1
    finally:
        if csv_file:
            csv_file.close()

    if not dry_run:
        print("\nRemoving empty subdirectories...")
        # --- Start of new logic ---
        # We now clean up from the original root_path
        remove_empty_directories(root_path)
        # --- End of new logic ---

    print("\n" + "=" * 50)
    print(f"Summary:")
    print(f"  Files moved: {moved_count}")
    print(f"  Files skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    if create_csv and csv_path:
        print(f"  CSV log updated at: {csv_path}")

    return moved_count, skipped_count, error_count


def remove_empty_directories(start_path):
    """
    Remove empty subdirectories.

    Args:
        start_path (Path): The root directory path to start cleaning from.
    """
    # Walk from bottom up to remove empty directories
    for current_dir, subdirs, files in os.walk(start_path, topdown=False):
        current_path = Path(current_dir)

        try:
            # Try to remove the directory if it's empty
            if not any(current_path.iterdir()):
                print(f"  Removing empty directory: {current_path.relative_to(start_path.parent)}")
                current_path.rmdir()
        except OSError as e:
            print(f"  Could not remove directory {current_path.relative_to(start_path.parent)}: {e}")


if __name__ == "__main__":
    # --- Start of new logic ---
    # Point this to the directory containing the files you want to move.
    # For example, if files are in '.../classifiables/doors', use that path.
    # The files will be moved to '.../classifiables'.
    move_files_to_parent("cs2 sounds/classifiables/footsteps", create_csv=True, dry_run=False)
    # --- End of new logic ---
