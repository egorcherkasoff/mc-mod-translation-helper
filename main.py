import os
import sys
import json
import zipfile
import logging
import shutil
import argparse
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants
SUPPORTED_LANGUAGES = {
    "ru_ru": "Russian",
    "fr_fr": "French",
    "de_de": "German",
    "es_es": "Spanish",
    "it_it": "Italian",
    "ja_jp": "Japanese",
    "ko_kr": "Korean",
    "pl_pl": "Polish",
    "pt_br": "Brazilian Portuguese",
    "zh_cn": "Simplified Chinese",
    "zh_tw": "Traditional Chinese"
}

# Config file for saving settings
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

class LogHandler(logging.Handler):
    """Custom logging handler to redirect logs to GUI."""
    
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget
        
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        # Schedule the append operation to be executed by the GUI thread
        self.text_widget.after(0, append)

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

def process_all_jars(input_dir, output_dir, target_lang, progress_var=None, status_var=None):
    """
    Process all JAR files in the input directory.
    
    Args:
        input_dir: Directory containing JAR files
        output_dir: Directory where output will be stored
        target_lang: Target language code
        progress_var: Optional tkinter variable for progress updates
        status_var: Optional tkinter variable for status updates
    """
    try:
        # Validate the input directory
        if not os.path.isdir(input_dir):
            logger.error(f"The input path {input_dir} is not a directory.")
            return
        
        logger.info(f"Scanning for JAR files in {input_dir}")
        logger.info(f"Target language: {target_lang}")
        
        jar_files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith('.jar')]
        
        if not jar_files:
            logger.warning(f"No JAR files found in {input_dir}")
            if status_var:
                status_var.set("No JAR files found")
            return
        
        logger.info(f"Found {len(jar_files)} JAR files. Starting processing...")
        
        # Process each JAR file
        for idx, jar_path in enumerate(jar_files):
            process_jar_file(jar_path, output_dir, target_lang)
            # Update progress if available
            if progress_var:
                progress_value = int((idx + 1) / len(jar_files) * 100)
                progress_var.set(progress_value)
            if status_var:
                status_var.set(f"Processing: {idx + 1}/{len(jar_files)}")
        
        logger.info("All processing completed.")
        if status_var:
            status_var.set("Processing complete")
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        if status_var:
            status_var.set(f"Error: {str(e)}")

def load_config():
    """Load configuration from file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
    
    return {"input_dir": "", "target_lang": "ru_ru"}

def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")

class MinecraftTranslationApp:
    """GUI application for Minecraft translation helper."""
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Minecraft Mod Translation Helper")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Load saved configuration
        self.config = load_config()
        
        # Set up variables
        self.input_dir = tk.StringVar(value=self.config.get("input_dir", ""))
        self.output_dir = tk.StringVar()
        self.target_lang = tk.StringVar(value=self.config.get("target_lang", "ru_ru"))
        self.progress_var = tk.IntVar(value=0)
        self.status_var = tk.StringVar(value="Ready")
        
        # Set default output directory
        default_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        self.output_dir.set(default_output)
        
        # Create UI elements
        self.create_widgets()
        
        # Configure logging to GUI
        self.configure_logging()
        
        # Log startup info
        if self.input_dir.get():
            logger.info(f"Loaded saved input directory: {self.input_dir.get()}")
        else:
            logger.info("No saved input directory found. Please select a mods folder.")
    
    def create_widgets(self):
        """Create and arrange all UI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input directory selection
        input_frame = ttk.LabelFrame(main_frame, text="Input Directory (Mods Folder)", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Entry(input_frame, textvariable=self.input_dir, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input_dir).pack(side=tk.RIGHT, padx=5)
        
        # Output directory selection
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="10")
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir).pack(side=tk.RIGHT, padx=5)
        
        # Language selection
        lang_frame = ttk.LabelFrame(main_frame, text="Target Language", padding="10")
        lang_frame.pack(fill=tk.X, padx=5, pady=5)
        
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.target_lang, state="readonly")
        lang_combo["values"] = list(SUPPORTED_LANGUAGES.keys())
        lang_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Add language description label
        self.lang_desc = ttk.Label(lang_frame, text=f"({SUPPORTED_LANGUAGES.get(self.target_lang.get(), '')})")
        self.lang_desc.pack(side=tk.RIGHT, padx=5)
        
        # Update language description when selection changes
        lang_combo.bind("<<ComboboxSelected>>", self.update_lang_description)
        
        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(btn_frame, text="Start Processing", command=self.start_processing).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Open Output Folder", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exit", command=self.on_close).pack(side=tk.RIGHT, padx=5)
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        ttk.Progressbar(progress_frame, variable=self.progress_var, length=100, mode='determinate').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Status label
        ttk.Label(main_frame, textvariable=self.status_var).pack(fill=tk.X, padx=5)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Set up window close event handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def configure_logging(self):
        """Configure logging to display in the GUI."""
        # Create and add the custom handler
        log_handler = LogHandler(self.log_text)
        log_handler.setLevel(logging.INFO)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add the handler to the logger
        logger.addHandler(log_handler)
    
    def update_lang_description(self, event=None):
        """Update the language description when selection changes."""
        lang_code = self.target_lang.get()
        lang_name = SUPPORTED_LANGUAGES.get(lang_code, '')
        self.lang_desc.config(text=f"({lang_name})")
        
        # Save the selected language to config
        self.config["target_lang"] = lang_code
        save_config(self.config)
    
    def browse_input_dir(self):
        """Open file dialog to select input directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir.set(directory)
            # Save the input directory to config
            self.config["input_dir"] = directory
            save_config(self.config)
            logger.info(f"Input directory saved: {directory}")
    
    def browse_output_dir(self):
        """Open file dialog to select output directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        output_dir = self.output_dir.get()
        if os.path.exists(output_dir):
            # Open folder based on OS
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{output_dir}"')
            else:  # Linux and other Unix-like
                os.system(f'xdg-open "{output_dir}"')
        else:
            messagebox.showwarning("Warning", "Output directory does not exist yet.")
    
    def start_processing(self):
        """Start the JAR processing in a separate thread."""
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        target_lang = self.target_lang.get()
        
        if not input_dir:
            messagebox.showerror("Error", "Please select an input directory.")
            return
        
        if not os.path.exists(input_dir):
            messagebox.showerror("Error", "Input directory does not exist.")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting...")
        
        # Start processing in a separate thread
        thread = threading.Thread(
            target=process_all_jars,
            args=(input_dir, output_dir, target_lang, self.progress_var, self.status_var)
        )
        thread.daemon = True
        thread.start()
    
    def on_close(self):
        """Handle window close event."""
        # Save configuration before closing
        self.config["input_dir"] = self.input_dir.get()
        self.config["target_lang"] = self.target_lang.get()
        save_config(self.config)
        
        # Close the window
        self.root.destroy()

def main_gui():
    """Start the GUI application."""
    root = tk.Tk()
    app = MinecraftTranslationApp(root)
    root.mainloop()

def main_cli():
    """Command-line interface main function."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Minecraft Mod Translation Helper')
    parser.add_argument('input_dir', help='Directory containing JAR files to process')
    parser.add_argument('--lang', default='ru_ru', help='Target language code (default: ru_ru)')
    parser.add_argument('--gui', action='store_true', help='Launch GUI instead of command line mode')
    
    args = parser.parse_args()
    
    # Check if GUI mode is requested
    if args.gui:
        main_gui()
        return
    
    input_dir = args.input_dir
    target_lang = args.lang
    
    # Create the output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all JAR files
    process_all_jars(input_dir, output_dir, target_lang)

if __name__ == "__main__":
    # Modified to start GUI by default
    if len(sys.argv) > 1 and sys.argv[1] != '--gui':
        # Command line mode only if arguments are provided and first arg is not --gui
        main_cli()
    else:
        # GUI mode by default
        main_gui()