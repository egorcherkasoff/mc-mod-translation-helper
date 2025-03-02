import os
import sys
import json
import zipfile
import logging
import shutil
import argparse
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def process_jar_file(jar_path, output_dir, target_lang):
    """
    Process a single JAR file to extract and compare translation files.
    
    Args:
        jar_path: Path to the JAR file
        output_dir: Base directory where extracted files will be saved
        target_lang: Target language code (e.g., 'ru_ru', 'fr_fr', etc.)
    """
    jar_name = os.path.basename(jar_path)
    mod_name = os.path.splitext(jar_name)[0]
    mod_output_dir = os.path.join(output_dir, mod_name)
    
    # Create the output directory for this mod if it doesn't exist
    os.makedirs(mod_output_dir, exist_ok=True)
    
    logger.info(f"Processing mod: {mod_name}")
    
    # Open the JAR file as a ZIP archive
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            # List all files in the archive
            file_list = jar.namelist()
            
            # Look for translation files
            en_us_path = None
            target_lang_path = None
            
            # Search for translation files in the archive
            for file_path in file_list:
                if file_path.endswith('en_us.json'):
                    en_us_path = file_path
                elif file_path.endswith(f'{target_lang}.json'):
                    target_lang_path = file_path
            
            # Check if English translation exists
            if not en_us_path:
                logger.warning(f"en_us.json not found in {jar_name}. Skipping this mod.")
                shutil.rmtree(mod_output_dir)
                return
            
            # Extract the English translation file
            logger.info(f"Extracting {en_us_path}")
            en_us_content = jar.read(en_us_path)
            en_us_file_path = os.path.join(mod_output_dir, "en_us.json")
            with open(en_us_file_path, 'wb') as f:
                f.write(en_us_content)
            
            # Load the English translation
            en_us_data = json.loads(en_us_content)
            
            # If target language translation exists, extract and compare
            if target_lang_path:
                logger.info(f"Extracting {target_lang_path}")
                target_lang_content = jar.read(target_lang_path)
                target_lang_file_path = os.path.join(mod_output_dir, f"{target_lang}.json")
                with open(target_lang_file_path, 'wb') as f:
                    f.write(target_lang_content)
                
                # Load the target language translation
                target_lang_data = json.loads(target_lang_content)
                
                # Compare translations and find missing keys
                missing_translations = {}
                for key, value in en_us_data.items():
                    if key not in target_lang_data:
                        missing_translations[key] = value
                
                # Write the diff file if there are missing translations
                if missing_translations:
                    logger.info(f"Found {len(missing_translations)} missing translations. Writing diff.json")
                    diff_file_path = os.path.join(mod_output_dir, "diff.json")
                    with open(diff_file_path, 'w', encoding='utf-8') as f:
                        json.dump(missing_translations, f, ensure_ascii=False, indent=2)
                else:
                    logger.info("All keys are translated. Removing mod folder as no diff needed.")
                    shutil.rmtree(mod_output_dir)
            else:
                logger.warning(f"{target_lang}.json not found in {jar_name}. Only extracted en_us.json.")
            
            logger.info(f"Finished processing {mod_name}")
            
    except Exception as e:
        logger.error(f"Error processing {jar_path}: {str(e)}")

def main():
    """
    Main function to process all JAR files in the input directory.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Minecraft Mod Translation Helper')
    parser.add_argument('input_dir', help='Directory containing JAR files to process')
    parser.add_argument('--lang', default='ru_ru', help='Target language code (default: ru_ru)')
    
    args = parser.parse_args()
    
    input_dir = args.input_dir
    target_lang = args.lang
    
    # Create the output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Validate the input directory
    if not os.path.isdir(input_dir):
        logger.error(f"The input path {input_dir} is not a directory.")
        sys.exit(1)
    
    logger.info(f"Scanning for JAR files in {input_dir}")
    logger.info(f"Target language: {target_lang}")
    
    jar_files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith('.jar')]
    
    if not jar_files:
        logger.warning(f"No JAR files found in {input_dir}")
        sys.exit(0)
    
    logger.info(f"Found {len(jar_files)} JAR files. Starting processing...")
    
    # Process each JAR file
    for jar_path in jar_files:
        process_jar_file(jar_path, output_dir, target_lang)
    
    logger.info("All processing completed.")

if __name__ == "__main__":
    main()