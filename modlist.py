import requests
import json
import os
import tkinter as tk
from tkinter import messagebox
import getpass
import subprocess
import threading

# URL de la liste de mods
url = "https://raw.githubusercontent.com/PtitBeescuit/modlist/refs/heads/main/modlist.json"

# URL du fichier de version hébergé sur GitHub
version_url = "https://raw.githubusercontent.com/PtitBeescuit/modlist/refs/tags/v2.0/updater.json"

# Chemin du fichier de stockage des versions locales
username = getpass.getuser()
mods_folder = f"C:\\Users\\{username}\\AppData\\Roaming\\.minecraft\\mods"
local_versions_file = f"C:\\Users\\{username}\\AppData\\Roaming\\.minecraft\\mods_versions.json"

# Charger et sauvegarder les versions locales
def load_local_versions():
    if os.path.exists(local_versions_file):
        with open(local_versions_file, "r") as file:
            return json.load(file)
    return {}

def save_local_versions(local_versions):
    with open(local_versions_file, "w") as file:
        json.dump(local_versions, file, indent=4)

# Supprimer les anciennes versions
def delete_old_version(mod, log_text):
    for file in os.listdir(mods_folder):
        if file.startswith(mod['name']) and file.endswith(".jar"):
            file_version = file[len(mod['name'])+1:-4]
            if file_version != mod['version']:
                old_mod_path = os.path.join(mods_folder, file)
                log_text.insert(tk.END, f"Ancienne version trouvée et supprimée : {old_mod_path}\n")
                os.remove(old_mod_path)
                log_text.yview(tk.END)

# Télécharger les mods
def download_mod(mod, log_text):
    delete_old_version(mod, log_text)
    response = requests.get(mod["url"])
    if response.status_code == 200:
        os.makedirs(mods_folder, exist_ok=True)
        mod_path = os.path.join(mods_folder, f"{mod['name']}-{mod['version']}.jar")
        with open(mod_path, "wb") as file:
            file.write(response.content)
        log_text.insert(tk.END, f"Mod téléchargé : {mod['name']} (version {mod['version']})\n")
        log_text.yview(tk.END)
    else:
        log_text.insert(tk.END, f"Échec du téléchargement pour {mod['name']} (version {mod['version']})\n")
        log_text.yview(tk.END)

# Vérifier et mettre à jour les mods
def check_and_update_mods(log_text, update_window):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            mods = response.json()
        else:
            messagebox.showerror("Erreur", f"Erreur de récupération des données : Statut {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Une erreur de connexion s'est produite : {e}")
        return

    local_versions = load_local_versions()
    mods_updated = False

    update_window.show_window()
    log_text.insert(tk.END, "Étape 1: Vérification des versions...\n")
    log_text.yview(tk.END)

    for mod in mods:
        local_version = local_versions.get(mod["name"])
        if local_version != mod["version"]:
            log_text.insert(tk.END, f"Étape 2: Téléchargement de {mod['name']}...\n")
            log_text.yview(tk.END)
            download_mod(mod, log_text)
            local_versions[mod["name"]] = mod["version"]
            mods_updated = True

    save_local_versions(local_versions)
    if mods_updated:
        log_text.insert(tk.END, "Étape 3: Mise à jour terminée.\nLes mods ont été mis à jour avec succès.\n")
    else:
        log_text.insert(tk.END, "Étape 3: Tous les mods sont déjà à jour.\n")
    log_text.yview(tk.END)
    update_window.enable_ok_button()

# Lancer Minecraft via le Xbox Launcher
def play_minecraft():
    try:
        subprocess.Popen(['explorer.exe', 'shell:appsFolder\\Microsoft.4297127D64EC6_8wekyb3d8bbwe!Minecraft'])
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lancer Minecraft : {e}")

# Supprimer les mods et le fichier des versions locales
def clear_mods_folder():
    if messagebox.askyesno("Confirmation", "Voulez-vous supprimer tous les mods et le fichier mods_versions.json ?"):
        try:
            if os.path.exists(mods_folder):
                for file in os.listdir(mods_folder):
                    os.remove(os.path.join(mods_folder, file))
            if os.path.exists(local_versions_file):
                os.remove(local_versions_file)
            messagebox.showinfo("Succès", "Tous les mods et le fichier mods_versions.json ont été supprimés.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")

# Fonction pour vérifier si une mise à jour est disponible
def check_for_updates():
    try:
        # Récupérer les informations de version depuis GitHub
        response = requests.get(version_url)
        if response.status_code == 200:
            version_info = response.json()
            latest_version = version_info["version"]
            download_url = version_info["download_url"]

            # Lire la version actuelle du programme
            current_version = "2.0.0"  # Remplacer par la version actuelle de votre programme

            if latest_version > current_version:
                # Si une mise à jour est disponible, proposer de la télécharger
                if messagebox.askyesno("Mise à jour disponible", f"Une nouvelle version ({latest_version}) est disponible.\nSouhaitez-vous la télécharger ?"):
                    download_update(download_url)
            else:
                messagebox.showinfo("Pas de mise à jour", "Votre programme est à jour.")
        else:
            messagebox.showerror("Erreur", f"Erreur de récupération de la version : Statut {response.status_code}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite lors de la connexion : {e}")

# Fonction pour télécharger et remplacer l'exécutable
def download_update(download_url):
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            exe_path = os.path.join(os.getcwd(), "your_program.exe")  # Chemin de votre programme actuel
            with open(exe_path, "wb") as file:
                file.write(response.content)
            messagebox.showinfo("Mise à jour", "Le programme a été mis à jour avec succès.")
        else:
            messagebox.showerror("Erreur", "Échec du téléchargement de la mise à jour.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite lors du téléchargement de la mise à jour : {e}")

# Fenêtre de mise à jour des mods
class UpdateWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Mise à jour des Mods Minecraft")
        self.window.geometry("400x300")
        self.window.minsize(400, 300)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        self.text = tk.Text(self.window, height=15, width=50)
        self.text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.ok_button = tk.Button(self.window, text="OK", command=self.hide_window, state="disabled")
        self.ok_button.grid(row=1, column=0, pady=5)
        self.window.withdraw()

    def show_window(self):
        self.window.deiconify()
        self.ok_button.config(state="disabled")

    def enable_ok_button(self):
        self.ok_button.config(state="normal")

    def hide_window(self):
        self.window.withdraw()

# Interface principale
def create_interface():
    root = tk.Tk()
    root.title("Gestionnaire de Mods Minecraft")
    
    tk.Label(root, text="Cliquez pour vérifier les mises à jour des mods.").pack(pady=10)

    tk.Button(root, text="Vérifier et Mettre à Jour", command=lambda: start_update_thread(update_window)).pack(pady=10)
    tk.Button(root, text="Vérifier les mises à jour du programme", command=check_for_updates).pack(pady=10)  # Nouveau bouton pour les mises à jour du programme
    tk.Button(root, text="Lancer Minecraft (Xbox Launcher)", command=play_minecraft).pack(pady=10)
    tk.Button(root, text="Supprimer tous les mods", command=clear_mods_folder).pack(pady=10)
    tk.Button(root, text="Quitter", command=root.quit).pack(pady=10)

    update_window = UpdateWindow(root)
    root.mainloop()

# Lancer le processus de mise à jour dans un thread
def start_update_thread(update_window):
    threading.Thread(target=check_and_update_mods, args=(update_window.text, update_window)).start()

# Lancer l'interface graphique
create_interface()
