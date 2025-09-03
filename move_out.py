

import os
import shutil
from pathlib import Path


def move_files_to_parent(root_directory, dry_run=False):
    """
    Move all files from subdirectories to their parent directory.

    Args:
        root_directory (str): The root directory to process
        dry_run (bool): If True, only print what would be done without actually moving files

    Returns:
        tuple: (moved_count, skipped_count, error_count)
    """
    root_path = Path(root_directory)
    print(root_path)

    if not root_path.exists():
        raise FileNotFoundError(f"Error: '{root_directory}' does not exist")

    if not root_path.is_dir():
        raise NotADirectoryError(f"Error: '{root_directory}' is not a directory")

    moved_count = 0
    skipped_count = 0
    error_count = 0

    print(f"Processing directory: {root_path.absolute()}")
    print(f"Dry run mode: {'ON' if dry_run else 'OFF'}")
    print("-" * 50)

    # Walk through all subdirectories
    for current_dir, subdirs, files in os.walk(root_path):
        current_path = Path(current_dir)

        # Skip the root directory itself
        if current_path == root_path:
            continue

        print(f"\nProcessing subdirectory: {current_path.relative_to(root_path)}")

        for file in files:
            source_file = current_path / file
            target_file = root_path / file
            if source_file is 'awp':
                skipped_count += 1
                print(f"  Skipping file: {file} (reserved name)")
                continue

            try:
                # Handle name conflicts by adding a suffix
                counter = 1
                original_target = target_file
                while target_file.exists():
                    name = original_target.stem
                    suffix = original_target.suffix
                    target_file = root_path / f"{name}_{counter}{suffix}"
                    counter += 1

                if dry_run:
                    print(f"  Would move: {source_file.relative_to(root_path)} -> {target_file.name}")
                else:
                    print(f"  Moving: {source_file.relative_to(root_path)} -> {target_file.name}")
                    shutil.move(str(source_file), str(target_file))

                moved_count += 1

            except Exception as e:
                print(f"  Error moving {source_file.relative_to(root_path)}: {e}")
                error_count += 1

    # Remove empty subdirectories after moving files
    if not dry_run:
        print("\nRemoving empty subdirectories...")
        remove_empty_directories(root_path)

    print("\n" + "=" * 50)
    print(f"Summary:")
    print(f"  Files moved: {moved_count}")
    print(f"  Files skipped: {skipped_count}")
    print(f"  Errors: {error_count}")

    return moved_count, skipped_count, error_count


def remove_empty_directories(root_path):
    """
    Remove empty subdirectories after moving files.

    Args:
        root_path (Path): The root directory path
    """
    # Walk from bottom up to remove empty directories
    for current_dir, subdirs, files in os.walk(root_path, topdown=False):
        current_path = Path(current_dir)

        # Skip the root directory
        if current_path == root_path:
            continue

        try:
            # Try to remove the directory if it's empty
            if not any(current_path.iterdir()):
                print(f"  Removing empty directory: {current_path.relative_to(root_path)}")
                current_path.rmdir()
        except OSError as e:
            print(f"  Could not remove directory {current_path.relative_to(root_path)}: {e}")




if __name__ == "__main__":
    move_files_to_parent("cs2 sounds/weapons" , dry_run=False)
