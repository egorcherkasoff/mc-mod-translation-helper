# Minecraft Mod(pack) Translation Helper

A Python utility script that assists in identifying missing translation entries across different language files within your Minecraft mods.

## Overview

This tool scans Minecraft mod JAR files, extracts their translation files, and compares the English source (`en_us.json`) with a target language to identify missing translations. It's designed to help mod(pack) translators efficiently locate which text entries need to be translated.

## Features

-   Automatically processes multiple mod JAR files in a specified directory
-   Extracts translation JSON files from each mod
-   Compares source language (English) with target language files
-   Identifies and outputs missing translations as a `diff.json` file
-   Supports any target language through configuration
-   Cleans up output directory by removing mods that have complete translations

## Requirements

-   Python 3.6 or higher
-   No additional dependencies required (uses only standard library modules)

## Installation

1. Make sure you have Python 3.6+ installed
2. Clone this repository
3. Go to folder you've just cloned

## Usage

### Basic Usage

```bash
python main.py /path/to/mods
```

This will scan all JAR files in the specified directory, extract translation files, and compare English (`en_us.json`) with Russian (`ru_ru.json`) by default.

### Specifying a Different Target Language

```bash
python main.py /path/to/mods --lang fr_fr
```

Use the `--lang` parameter to specify a different target language (e.g., `fr_fr` for French, `de_de` for German, etc.)

## Output

The script creates an `output` directory in the same location as the script itself. Inside, it generates:

-   A folder for each mod that has missing translations
-   The original `en_us.json` and target language JSON files
-   A `diff.json` file containing all the entries that need translation

Mods with complete translations (no missing entries) are automatically removed from the output.

## Example

When running:

```bash
python main.py ~/minecraft/mods --lang de_de
```

The script will:

1. Scan all JAR files in the `~/minecraft/mods` directory
2. For each mod, extract and compare `en_us.json` with `de_de.json`
3. Create a folder with the mod's name in the `output` directory
4. Generate a `diff.json` with missing translations
5. Skip mods with complete translations or missing files

## Logging

The script provides detailed logging of its operation, including:

-   Which mods are being processed
-   Whether translation files are found and extracted
-   Number of missing translations identified
-   Information about mods that are skipped or removed

## Contributing

Feel free to submit issues or pull requests if you find bugs or have suggestions for improvements.

## License

This script is released as open source. You are free to use, modify, and distribute it as needed.
