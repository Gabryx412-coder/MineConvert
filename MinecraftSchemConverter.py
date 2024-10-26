import os
import json
import glob
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class MinecraftFileConverter:
    """Classe per gestire la conversione dei file Minecraft tra .schem e .schematic."""

    def __init__(self, verbose=False):
        self.verbose = verbose

    def log(self, message):
        """Log messages to the console if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def read_json_file(self, file_path):
        """Leggi un file JSON e restituisci il suo contenuto."""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"File non trovato: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Formato JSON non valido: {file_path}")

    def write_json_file(self, file_path, data):
        """Scrivi i dati in un file JSON."""
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)  # Indentazione migliorata per la leggibilità
        except IOError as e:
            raise IOError(f"Errore nella scrittura del file: {file_path}. {str(e)}")

    def convert_schem_to_schematic(self, input_file, output_file):
        """Converti file .schem in formato .schematic."""
        self.log(f"Inizio conversione: {input_file} a {output_file}")
        data = self.read_json_file(input_file)

        schematic_data = {
            'Version': 1.0,
            'Width': data['width'],
            'Height': data['height'],
            'Length': data['length'],
            'Materials': data['blocks'],
            'Entities': data.get('entities', [])
        }

        self.write_json_file(output_file, schematic_data)
        self.log("Conversione completata con successo.")

    def convert_schematic_to_schem(self, input_file, output_file):
        """Converti file .schematic in formato .schem."""
        self.log(f"Inizio conversione: {input_file} a {output_file}")
        data = self.read_json_file(input_file)

        schem_data = {
            'version': '1.0',
            'width': data['Width'],
            'height': data['Height'],
            'length': data['Length'],
            'blocks': data['Materials'],
            'entities': data.get('Entities', [])
        }

        self.write_json_file(output_file, schem_data)
        self.log("Conversione completata con successo.")

class MinecraftConverterApp:
    """Classe per l'interfaccia grafica dell'applicazione di conversione Minecraft."""

    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft File Converter")
        self.converter = MinecraftFileConverter(verbose=True)  # Abilitare il logging per debug
        
        self.create_widgets()
        self.layout_widgets()

    def create_widgets(self):
        """Crea i widget dell'interfaccia grafica."""
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.conversion_type = tk.StringVar(value='schem')

        self.input_entry = ttk.Entry(self.root, textvariable=self.input_dir, width=50)
        self.output_entry = ttk.Entry(self.root, textvariable=self.output_dir, width=50)

        self.browse_input_button = ttk.Button(self.root, text="Browse", command=self.browse_input)
        self.browse_output_button = ttk.Button(self.root, text="Browse", command=self.browse_output)

        self.convert_button = ttk.Button(self.root, text="Convert", command=self.start_conversion)
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')

        self.input_label = ttk.Label(self.root, text="Input Directory:")
        self.output_label = ttk.Label(self.root, text="Output Directory:")
        self.type_label = ttk.Label(self.root, text="Convert to:")

        self.radio_schematic = ttk.Radiobutton(self.root, text=".schematic", variable=self.conversion_type, value='schematic')
        self.radio_schem = ttk.Radiobutton(self.root, text=".schem", variable=self.conversion_type, value='schem')

    def layout_widgets(self):
        """Organizza i widget nell'interfaccia grafica."""
        self.input_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_entry.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.browse_input_button.grid(row=1, column=1)

        self.output_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_entry.grid(row=3, column=0, sticky=(tk.W, tk.E))
        self.browse_output_button.grid(row=3, column=1)

        self.type_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        self.radio_schematic.grid(row=5, column=0, sticky=tk.W)
        self.radio_schem.grid(row=6, column=0, sticky=tk.W)

        self.convert_button.grid(row=7, column=0, columnspan=2, pady=10)
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Configurazione delle colonne
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)

    def browse_input(self):
        """Apre un dialogo per selezionare la directory di input."""
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir.set(directory)

    def browse_output(self):
        """Apre un dialogo per selezionare la directory di output."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def start_conversion(self):
        """Avvia la conversione in un thread separato."""
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()

        if not input_dir or not output_dir:
            messagebox.showerror("Errore", "Seleziona entrambe le directory di input e output.")
            return

        self.progress.start()
        threading.Thread(target=self.convert_files, args=(input_dir, output_dir)).start()

    def convert_files(self, input_dir, output_dir):
        """Esegue la conversione dei file."""
        file_pattern = '*.schem' if self.conversion_type.get() == 'schematic' else '*.schematic'
        files_to_convert = glob.glob(os.path.join(input_dir, file_pattern))
        total_files = len(files_to_convert)

        if total_files == 0:
            messagebox.showinfo("Nessun File", "Nessun file trovato da convertire.")
            self.progress.stop()
            return

        for index, input_file in enumerate(files_to_convert):
            file_name = os.path.basename(input_file)
            output_file = os.path.join(output_dir, file_name.replace('.schem', '.schematic') if self.conversion_type.get() == 'schematic' else file_name.replace('.schematic', '.schem'))

            try:
                if self.conversion_type.get() == 'schematic':
                    self.converter.convert_schem_to_schematic(input_file, output_file)
                else:
                    self.converter.convert_schematic_to_schem(input_file, output_file)
            except Exception as e:
                messagebox.showerror("Errore", str(e))
                break

            # Aggiorna la barra di progresso
            self.update_progress(index + 1, total_files)

        self.progress.stop()
        messagebox.showinfo("Successo", "Conversione completata con successo!")

    def update_progress(self, current, total):
        """Aggiorna la barra di progresso."""
        progress_percentage = (current / total) * 100
        self.progress['value'] = progress_percentage
        self.root.update_idletasks()

def main():
    """Funzione principale per avviare l'applicazione."""
    root = tk.Tk()
    app = MinecraftConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
