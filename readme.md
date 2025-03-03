# Minecraft Mod(pack) Translation Helper

A Python utility with both GUI and command-line interfaces that helps identify missing translation entries across different language files within Minecraft mods.

## Overview

This tool scans Minecraft mod JAR files, extracts their translation files, and compares the English source (`en_us.json`) with a target language to identify missing translations. It's designed to help mod(pack) translators efficiently locate which text entries need to be translated.

## Features

-   User-friendly graphical interface for easier operation
-   Command-line interface for advanced users and automation
-   Automatically processes multiple mod JAR files in a specified directory
-   Extracts translation JSON files from each mod
-   Compares source language (English) with target language files
-   Identifies and outputs missing translations as a `diff.json` file
-   GUI supports multiple target languages including Russian, French, German, Spanish, Italian, Japanese, Korean, Polish, Brazilian Portuguese, Simplified Chinese, and Traditional Chinese
-   Saves your preferences between sessions
-   Detailed logging with real-time progress tracking
-   Cleans up output directory by removing mods that have complete translations

## Requirements

-   Python 3.6 or higher
-   Tkinter (included with most Python installations)
-   No additional dependencies required (uses only standard library modules)

## Installation

1. Make sure you have Python 3.6+ installed
2. Clone this repository or download the source code
3. Navigate to the folder containing the code

## Usage

### Graphical Interface

Simply run the application without arguments to use the GUI:

```bash
python main.py
```

OR

Simply double-click on main.py file!

The GUI allows you to:

-   Select input mods folder through a file browser
-   Choose output directory (defaults to an "output" folder in the application directory)
-   Select target language from a dropdown menu
-   Monitor processing progress in real-time
-   View logs directly in the application window
-   Open the output folder with one click

### Command-line Interface

For automation or advanced usage, you can still use the command-line interface:

```bash
python main.py /path/to/mods
```

This will scan all JAR files in the specified directory, extract translation files, and compare English (`en_us.json`) with Russian (`ru_ru.json`) by default.

#### Specifying a Different Target Language

```bash
python main.py /path/to/mods --lang fr_fr
```

Use the `--lang` parameter to specify a different target language (e.g., `fr_fr` for French, `de_de` for German, etc.)

## Output

The script creates an `output` directory (or uses your specified output location) and generates:

-   A folder for each mod that has missing translations
-   The original `en_us.json` and target language JSON files
-   A `diff.json` file containing all the entries that need translation

Mods with complete translations (no missing entries) are automatically removed from the output to keep things organized.

## Supported Languages

The application supports the following languages:

-   Russian (ru_ru)
-   French (fr_fr)
-   German (de_de)
-   Spanish (es_es)
-   Italian (it_it)
-   Japanese (ja_jp)
-   Korean (ko_kr)
-   Polish (pl_pl)
-   Brazilian Portuguese (pt_br)
-   Simplified Chinese (zh_cn)
-   Traditional Chinese (zh_tw)

If you are using CLI you can specify any language you want, as long as you name it as minecraft translation file (ru_ru, uk_ua, fr_fr etc.)

## Example

When using the GUI:

1. Select your Minecraft mods folder
2. Choose your target language
3. Click "Start Processing"
4. When complete, click "Open Output Folder" to view the results

When using the command line:

```bash
python main.py ~/minecraft/mods --lang de_de
```

The application will:

1. Scan all JAR files in the `~/minecraft/mods` directory
2. For each mod, extract and compare `en_us.json` with `de_de.json`
3. Create a folder with the mod's name in the output directory
4. Generate a `diff.json` with missing translations
5. Skip mods with complete translations or missing files

## Configuration

The application saves your last used input directory and target language in a `config.json` file, making it convenient to perform repeated operations.

## Contributing

Feel free to submit issues or pull requests if you find bugs or have suggestions for improvements.

## License

This application is released as open source. You are free to use, modify, and distribute it as needed.
