import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import re  # Import regex module for splitting
##script logic by me. GUI and clean up by claude + gemini
## this script intended to create combinations of light and heavy chains from NGS data and assemble them into a .yaml file to be used as input sequence in boltz-2

class ProteinSequenceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Protein Sequence YAML Generator")
        self.root.geometry("1000x800")

        # Data storage
        self.heavy_chains = []
        self.light_chains = []

        self.setup_gui()

    def setup_gui(self):
        """Setup the main GUI interface"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title_label = ttk.Label(main_frame, text="Protein Sequence YAML Generator", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.antigen_tab = ttk.Frame(notebook)
        notebook.add(self.antigen_tab, text="Antigen Sequence")
        self.setup_antigen_tab()

        self.heavy_tab = ttk.Frame(notebook)
        notebook.add(self.heavy_tab, text="Heavy Chains")
        self.setup_heavy_tab()

        self.light_tab = ttk.Frame(notebook)
        notebook.add(self.light_tab, text="Light Chains")
        self.setup_light_tab()

        self.generate_tab = ttk.Frame(notebook)
        notebook.add(self.generate_tab, text="Generate YAML Files")
        self.setup_generate_tab()

    def setup_antigen_tab(self):
        """Setup the antigen sequence input tab"""
        frame = ttk.LabelFrame(self.antigen_tab, text="Antigen Sequence", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Enter the antigen amino acid sequence:").pack(anchor=tk.W, pady=(0, 5))
        self.antigen_text = scrolledtext.ScrolledText(frame, height=10, wrap=tk.WORD)
        self.antigen_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Clear", command=self.clear_antigen).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Load from File", command=self.load_antigen_file).pack(side=tk.LEFT)

    def setup_heavy_tab(self):
        """Setup the heavy chains input tab with a table-like paste area."""
        frame = ttk.LabelFrame(self.heavy_tab, text="Heavy Chain Sequences", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Input section for pasting multiple sequences
        paste_frame = ttk.LabelFrame(frame, text="Paste Heavy Chains (Name<space/tab>Sequence)", padding=10)
        paste_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(paste_frame,
                  text="Paste multiple sequences below. Each line should contain a unique name, a space or tab, and the sequence.",
                  wraplength=800).pack(anchor=tk.W, pady=(0, 5))

        self.heavy_paste_box = scrolledtext.ScrolledText(paste_frame, height=10, width=60)
        self.heavy_paste_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        paste_button_frame = ttk.Frame(paste_frame)
        paste_button_frame.pack(fill=tk.X)

        ttk.Button(paste_button_frame, text="Add Pasted Sequences", command=self.process_pasted_heavy_chains).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(paste_button_frame, text="Clear Paste Box",
                   command=lambda: self.heavy_paste_box.delete(1.0, tk.END)).pack(side=tk.LEFT)

        # List section to display added chains
        list_frame = ttk.LabelFrame(frame, text="Added Heavy Chains List", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('Name', 'Sequence Preview')
        self.heavy_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.heavy_tree.heading('Name', text='Name/Tag')
        self.heavy_tree.heading('Sequence Preview', text='Sequence Preview')
        self.heavy_tree.column('Name', width=150)
        self.heavy_tree.column('Sequence Preview', width=400)

        scrollbar_heavy = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.heavy_tree.yview)
        self.heavy_tree.configure(yscrollcommand=scrollbar_heavy.set)
        self.heavy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_heavy.pack(side=tk.RIGHT, fill=tk.Y)

        heavy_btn_frame = ttk.Frame(list_frame)
        heavy_btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(heavy_btn_frame, text="Remove Selected", command=self.remove_heavy_chain).pack(side=tk.LEFT,
                                                                                                  padx=(0, 5))
        ttk.Button(heavy_btn_frame, text="Clear All", command=self.clear_all_heavy).pack(side=tk.LEFT)

    def setup_light_tab(self):
        """Setup the light chains input tab with a table-like paste area."""
        frame = ttk.LabelFrame(self.light_tab, text="Light Chain Sequences", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Input section for pasting multiple sequences
        paste_frame = ttk.LabelFrame(frame, text="Paste Light Chains (Name<space/tab>Sequence)", padding=10)
        paste_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(paste_frame,
                  text="Paste multiple sequences below. Each line should contain a unique name, a space or tab, and the sequence.",
                  wraplength=800).pack(anchor=tk.W, pady=(0, 5))

        self.light_paste_box = scrolledtext.ScrolledText(paste_frame, height=10, width=60)
        self.light_paste_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        paste_button_frame = ttk.Frame(paste_frame)
        paste_button_frame.pack(fill=tk.X)

        ttk.Button(paste_button_frame, text="Add Pasted Sequences", command=self.process_pasted_light_chains).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(paste_button_frame, text="Clear Paste Box",
                   command=lambda: self.light_paste_box.delete(1.0, tk.END)).pack(side=tk.LEFT)

        # List section to display added chains
        list_frame = ttk.LabelFrame(frame, text="Added Light Chains List", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('Name', 'Sequence Preview')
        self.light_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.light_tree.heading('Name', text='Name/Tag')
        self.light_tree.heading('Sequence Preview', text='Sequence Preview')
        self.light_tree.column('Name', width=150)
        self.light_tree.column('Sequence Preview', width=400)

        scrollbar_light = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.light_tree.yview)
        self.light_tree.configure(yscrollcommand=scrollbar_light.set)
        self.light_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_light.pack(side=tk.RIGHT, fill=tk.Y)

        light_btn_frame = ttk.Frame(list_frame)
        light_btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(light_btn_frame, text="Remove Selected", command=self.remove_light_chain).pack(side=tk.LEFT,
                                                                                                  padx=(0, 5))
        ttk.Button(light_btn_frame, text="Clear All", command=self.clear_all_light).pack(side=tk.LEFT)

    def setup_generate_tab(self):
        """Setup the generate files tab"""
        frame = ttk.LabelFrame(self.generate_tab, text="Generate YAML Files", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        summary_frame = ttk.LabelFrame(frame, text="Summary", padding=10)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        self.summary_label = ttk.Label(summary_frame, text="Please add sequences in other tabs first.")
        self.summary_label.pack(anchor=tk.W)

        dir_frame = ttk.Frame(frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        self.output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.LEFT)

        generate_frame = ttk.Frame(frame)
        generate_frame.pack(fill=tk.X, pady=(10, 0))
        self.generate_btn = ttk.Button(generate_frame, text="Generate YAML Files", command=self.generate_yaml_files,
                                       state=tk.DISABLED)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(generate_frame, text="Update Summary", command=self.update_summary).pack(side=tk.LEFT)

        self.progress_frame = ttk.Frame(frame)
        self.progress_frame.pack(fill=tk.X, pady=(20, 0))
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(anchor=tk.W)

        self.output_text = scrolledtext.ScrolledText(frame, height=15, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    # --- NEW: Methods for processing pasted sequences ---

    def parse_and_add_sequences(self, paste_box, chain_list, tree_view, chain_type_str):
        """Generic function to parse pasted text and add sequences."""
        text_content = paste_box.get(1.0, tk.END).strip()
        if not text_content:
            messagebox.showinfo("Info", f"The paste box for {chain_type_str} chains is empty.")
            return

        lines = text_content.split('\n')
        added_count, skipped_count, duplicate_count = 0, 0, 0
        error_lines = []
        existing_names = {chain['name'] for chain in chain_list}

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Split on the first block of whitespace (handles spaces and tabs)
            parts = re.split(r'\s+', line, 1)

            if len(parts) != 2:
                skipped_count += 1
                error_lines.append(f"Line {i + 1}: Incorrect format.")
                continue

            name, sequence = parts[0].strip(), parts[1].strip().upper()

            if not name or not sequence:
                skipped_count += 1
                error_lines.append(f"Line {i + 1}: Name or sequence is empty after parsing.")
                continue

            if name in existing_names:
                duplicate_count += 1
                continue

            chain_list.append({'name': name, 'sequence': sequence})
            existing_names.add(name)

            preview = sequence[:50] + "..." if len(sequence) > 50 else sequence
            tree_view.insert('', tk.END, values=(name, preview))
            added_count += 1

        paste_box.delete(1.0, tk.END)
        self.update_summary()

        summary_msg = f"Processing complete for {chain_type_str} chains.\n\n"
        summary_msg += f"Successfully added: {added_count}\n"
        if duplicate_count > 0:
            summary_msg += f"Skipped (duplicate names): {duplicate_count}\n"
        if skipped_count > 0:
            summary_msg += f"Skipped (invalid format): {skipped_count}\n"
            summary_msg += "\nDetails of first 5 invalid lines:\n" + "\n".join(error_lines[:5])
        messagebox.showinfo("Processing Report", summary_msg)

    def process_pasted_heavy_chains(self):
        """Wrapper function to process pasted heavy chains."""
        self.parse_and_add_sequences(self.heavy_paste_box, self.heavy_chains, self.heavy_tree, "Heavy")

    def process_pasted_light_chains(self):
        """Wrapper function to process pasted light chains."""
        self.parse_and_add_sequences(self.light_paste_box, self.light_chains, self.light_tree, "Light")

    # --- Existing Event Handlers (modified or kept as is) ---

    def clear_antigen(self):
        self.antigen_text.delete(1.0, tk.END)

    def load_antigen_file(self):
        filename = filedialog.askopenfilename(title="Select antigen sequence file",
                                              filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.antigen_text.delete(1.0, tk.END)
                    self.antigen_text.insert(1.0, f.read())
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {str(e)}")

    def remove_heavy_chain(self):
        selected_items = self.heavy_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a heavy chain to remove.")
            return

        names_to_remove = {self.heavy_tree.item(item)['values'][0] for item in selected_items}

        # Remove from backend list
        self.heavy_chains = [chain for chain in self.heavy_chains if chain['name'] not in names_to_remove]

        # Remove from treeview
        for item in selected_items:
            self.heavy_tree.delete(item)

        self.update_summary()

    def clear_all_heavy(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all heavy chains?"):
            self.heavy_chains.clear()
            for item in self.heavy_tree.get_children():
                self.heavy_tree.delete(item)
            self.update_summary()

    def remove_light_chain(self):
        selected_items = self.light_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a light chain to remove.")
            return

        names_to_remove = {self.light_tree.item(item)['values'][0] for item in selected_items}

        self.light_chains = [chain for chain in self.light_chains if chain['name'] not in names_to_remove]

        for item in selected_items:
            self.light_tree.delete(item)

        self.update_summary()

    def clear_all_light(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all light chains?"):
            self.light_chains.clear()
            for item in self.light_tree.get_children():
                self.light_tree.delete(item)
            self.update_summary()

    def browse_output_dir(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)

    def update_summary(self):
        antigen = self.antigen_text.get(1.0, tk.END).strip()
        heavy_count = len(self.heavy_chains)
        light_count = len(self.light_chains)

        summary_text = f"Antigen sequence: {'Present' if antigen else 'Missing'}\n"
        summary_text += f"Heavy chains: {heavy_count}\n"
        summary_text += f"Light chains: {light_count}\n"

        if antigen and heavy_count > 0 and light_count > 0:
            total_combinations = self.calculate_combinations(heavy_count, light_count)
            summary_text += f"Total YAML files to be generated: {total_combinations}"
            self.generate_btn.config(state=tk.NORMAL)
        else:
            summary_text += "Status: Missing required data"
            self.generate_btn.config(state=tk.DISABLED)
        self.summary_label.config(text=summary_text)

    def calculate_combinations(self, heavy_count, light_count):
        # This is a complex, specific logic from the original script.
        # It's kept as is.
        if heavy_count == 0 or light_count == 0:
            return 0
        if heavy_count == 1:
            return min(5, light_count)

        total = 0
        # First two heavy chains
        total += min(5, light_count)  # First heavy
        total += min(5, light_count)  # Second heavy

        # Middle heavy chains (from 3rd to 3rd from last)
        if heavy_count > 4:
            total += (heavy_count - 4) * 5  # Each gets 5 light chains

        # Last two heavy chains
        if heavy_count > 2:  # 2nd to last heavy
            total += min(5, light_count)
        if heavy_count > 3:  # last heavy
            total += min(5, light_count)

        # The calculation might overestimate if light_count is small for middle chains.
        # A more precise count could be implemented, but we follow the original implied logic.
        return total

    def generate_yaml_files(self):
        antigen_seq = self.antigen_text.get(1.0, tk.END).strip()
        if not antigen_seq or not self.heavy_chains or not self.light_chains:
            messagebox.showerror("Error", "Please provide antigen sequence and at least one heavy and light chain.")
            return

        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {str(e)}")
                return

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        try:
            self.generate_combinations_gui(antigen_seq, output_dir)
            messagebox.showinfo("Success", f"YAML files generated successfully in {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating files: {str(e)}")
        self.output_text.config(state=tk.DISABLED)

    def create_yaml_file_gui(self, filepath, antigen_seq, heavy_seq, light_seq):
        with open(filepath, 'w') as f_out:
            f_out.write("sequences:\n")
            f_out.write(f"  - protein:\n      id: A\n      sequence: {antigen_seq}\n")
            f_out.write(f"  - protein:\n      id: B\n      sequence: {heavy_seq}\n")
            f_out.write(f"  - protein:\n      id: C\n      sequence: {light_seq}\n")

    def log_output(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.root.update()

    def generate_combinations_gui(self, antigen_seq, output_dir):
        """Generate YAML files for different combinations - Original Logic"""
        heavy = [chain['sequence'] for chain in self.heavy_chains]
        heavy_tag = [chain['name'] for chain in self.heavy_chains]
        light = [chain['sequence'] for chain in self.light_chains]
        light_tag = [chain['name'] for chain in self.light_chains]

        self.log_output(f"Generating YAML files...")
        self.log_output(f"Heavy chains: {len(heavy)}, Light chains: {len(light)}")
        files_generated = 0

        # This entire block follows the specific combination logic from the original script
        if not heavy or not light: return

        # First heavy chain with first 5 light chains
        for j in range(min(5, len(light))):
            filename = f"{heavy_tag[0]}_{light_tag[j]}.yaml"
            filepath = os.path.join(output_dir, filename)
            self.create_yaml_file_gui(filepath, antigen_seq, heavy[0], light[j])
            self.log_output(f"Generated: {heavy_tag[0]} + {light_tag[j]}")
            files_generated += 1
        self.log_output("---")

        # Second heavy chain with first 5 light chains
        if len(heavy) > 1:
            for j in range(min(5, len(light))):
                filename = f"{heavy_tag[1]}_{light_tag[j]}.yaml"
                filepath = os.path.join(output_dir, filename)
                self.create_yaml_file_gui(filepath, antigen_seq, heavy[1], light[j])
                self.log_output(f"Generated: {heavy_tag[1]} + {light_tag[j]}")
                files_generated += 1
            self.log_output("---")

        # Middle heavy chains (3rd to 3rd-from-last)
        if len(heavy) > 4:
            for i in range(2, len(heavy) - 2):
                for j in range(5):
                    light_idx = i + j - 2
                    if light_idx >= len(light): continue
                    filename = f"{heavy_tag[i]}_{light_tag[light_idx]}.yaml"
                    filepath = os.path.join(output_dir, filename)
                    self.create_yaml_file_gui(filepath, antigen_seq, heavy[i], light[light_idx])
                    self.log_output(f"Generated: {heavy_tag[i]} + {light_tag[light_idx]}")
                    files_generated += 1
                self.log_output("---")

        # Second to last heavy chain (if it exists and is not one of the first two)
        if len(heavy) > 2:
            for j in reversed(range(min(5, len(light)))):
                light_idx = len(light) - 1 - j
                filename = f"{heavy_tag[-2]}_{light_tag[light_idx]}.yaml"
                filepath = os.path.join(output_dir, filename)
                self.create_yaml_file_gui(filepath, antigen_seq, heavy[-2], light[light_idx])
                self.log_output(f"Generated: {heavy_tag[-2]} + {light_tag[light_idx]}")
                files_generated += 1
            self.log_output("---")

        # Last heavy chain (if it's different from the others already processed)
        if len(heavy) > 1 and len(heavy) not in [2, 3, 4]:  # Avoid reprocessing
            for j in reversed(range(min(5, len(light)))):
                light_idx = len(light) - 1 - j
                filename = f"{heavy_tag[-1]}_{light_tag[light_idx]}.yaml"
                filepath = os.path.join(output_dir, filename)
                self.create_yaml_file_gui(filepath, antigen_seq, heavy[-1], light[light_idx])
                self.log_output(f"Generated: {heavy_tag[-1]} + {light_tag[light_idx]}")
                files_generated += 1
            self.log_output("---")

        self.log_output(f"Completed! Generated {files_generated} YAML files.")


def main():
    root = tk.Tk()
    app = ProteinSequenceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
