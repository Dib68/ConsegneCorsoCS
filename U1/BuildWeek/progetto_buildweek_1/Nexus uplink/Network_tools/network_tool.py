import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import socket
import requests
import os
import threading
import datetime
import cv2
import base64
import codecs
import stepic
import urllib.parse
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- CONFIGURAZIONE GLOBALE ---
PORTE_DA_CONTROLLARE = [21, 22, 25, 53, 80, 110, 139, 143, 443, 445, 3306, 8080]
HEADER_EVASIONE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}
FILE_LOG = "network_tool_log.txt"
VIDEO_PATH = "Video_D_Generato_su_Richiesta.mp4"
VIDEO_SPEED = 15

# --- PALETTE COLORI ---
BG_MAIN = "#0D1117"
BG_PANEL = "#161B22"
BLUE_ACCENT = "#58A6FF"
BLUE_HOVER = "#1F6FEB"
TEXT_DARK = "#C9D1D9"
TEXT_MUTED = "#8B949E"
CONSOLE_BG = "#010409"
CONSOLE_FG = "#3FB950"

class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Avengers - Ultimate Security Tool v4.0")
        self.root.geometry("900x750")
        self.root.configure(bg=BG_MAIN)
        
        self.sniffing = False
        self.current_frame = None
        self.text_area = None 
        self.entry_ip = None
        self.drop_target = None

        self.mostra_schermata_login()

    def cambia_schermata(self, nuovo_frame_func):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.sniffing = False 
        self.current_frame = tk.Frame(self.root, bg=BG_MAIN)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        nuovo_frame_func(self.current_frame)

    def setup_placeholder(self, entry, test_placeholder, is_password=False):
        entry.insert(0, test_placeholder)
        entry.config(fg=TEXT_MUTED)
        
        def on_focus_in(event):
            if entry.get() == test_placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=TEXT_DARK)
                if is_password:
                    entry.config(show="*")
                    
        def on_focus_out(event):
            if entry.get() == "":
                if is_password:
                    entry.config(show="")
                entry.insert(0, test_placeholder)
                entry.config(fg=TEXT_MUTED)
                
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def mostra_schermata_login(self):
        self.cambia_schermata(self.costruisci_login)

    def costruisci_login(self, frame):
        panel = tk.Frame(frame, bg=BG_PANEL, bd=1, relief=tk.SOLID, highlightbackground=BLUE_ACCENT, highlightthickness=1)
        panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=350)
        tk.Label(panel, text="SISTEMA CRIPTATO", font=("Consolas", 18, "bold"), fg=BLUE_ACCENT, bg=BG_PANEL).pack(pady=(30, 20))
        
        e_user = tk.Entry(panel, font=("Consolas", 14), justify="center", bg=CONSOLE_BG, fg=TEXT_DARK, insertbackground=TEXT_DARK)
        self.setup_placeholder(e_user, "Inserisci Username")
        e_user.pack(pady=10, ipady=5, padx=40, fill=tk.X)

        e_pwd = tk.Entry(panel, font=("Consolas", 14), justify="center", bg=CONSOLE_BG, fg=TEXT_DARK, insertbackground=TEXT_DARK)
        self.setup_placeholder(e_pwd, "Inserisci Password", is_password=True)
        e_pwd.pack(pady=10, ipady=5, padx=40, fill=tk.X)

        def login(event=None):
            if e_user.get() == "admin" and e_pwd.get() == "avengers":
                self.cambia_schermata(self.mostra_schermata_video)
            else:
                messagebox.showerror("Accesso Negato", "Credenziali errate.")

        tk.Button(panel, text="ACCEDI", font=("Consolas", 12, "bold"), bg=BLUE_ACCENT, fg="#ffffff", command=login, relief=tk.FLAT).pack(pady=30, fill=tk.X, padx=40, ipady=5)
        self.root.bind('<Return>', login)

    def mostra_schermata_video(self, frame):
        self.root.unbind('<Return>')
        if not os.path.exists(VIDEO_PATH):
            self.mostra_menu_principale()
            return

        lbl_v = tk.Label(frame, bg="black")
        lbl_v.pack(fill=tk.BOTH, expand=True)
        cap = cv2.VideoCapture(VIDEO_PATH)

        def stream():
            ret, f = cap.read()
            if ret:
                f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(f)
                img.thumbnail((self.root.winfo_width(), self.root.winfo_height()), Image.Resampling.LANCZOS)
                itk = ImageTk.PhotoImage(image=img)
                lbl_v.itk = itk
                lbl_v.config(image=itk)
                lbl_v.after(VIDEO_SPEED, stream)
            else:
                cap.release()
                self.mostra_menu_principale()
        stream()

    def mostra_menu_principale(self, frame=None):
        if frame is None:
            self.cambia_schermata(self.mostra_menu_principale)
            return
        
        tk.Label(frame, text="DIGITAL AVENGERS", font=("Consolas", 28, "bold"), fg=BLUE_ACCENT, bg=BG_MAIN).pack(pady=(40, 10))
        tk.Label(frame, text="Seleziona modulo operativo:", font=("Consolas", 12), fg=TEXT_DARK, bg=BG_MAIN).pack(pady=(0, 30))
        
        btns = [
            ("Scansione PORTE", "PORTE"), 
            ("Verifica Verbi HTTP", "HTTP"), 
            ("Sniffing SOCKET (ICMP)", "SOCKET"), 
            ("Decodifica Testo (TXT)", "DECODER"),
            ("Steganografia Avanzata", "STEGANO")
        ]
        
        for t, m in btns:
            tk.Button(frame, text=t, font=("Consolas", 12, "bold"), bg=BG_PANEL, fg=BLUE_ACCENT, width=35, pady=12, relief=tk.FLAT,
                      activebackground=BLUE_HOVER, activeforeground="white", cursor="hand2",
                      command=lambda x=m: self.mostra_tool(x)).pack(pady=8)
        
        tk.Button(frame, text="ESCI DAL SISTEMA", bg="#da3633", fg="white", font=("Consolas", 12, "bold"), width=20, pady=10, relief=tk.FLAT, cursor="hand2", command=self.root.quit).pack(side=tk.BOTTOM, pady=40)

    def mostra_tool(self, tipo):
        self.cambia_schermata(lambda f: self.costruisci_interfaccia_tool(f, tipo))

    def costruisci_interfaccia_tool(self, frame, tipo):
        header = tk.Frame(frame, bg=BG_PANEL, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Button(header, text="← Torna al Menu", font=("Consolas", 10), bg=BG_MAIN, fg=TEXT_DARK, relief=tk.FLAT, command=self.mostra_menu_principale).pack(side=tk.LEFT, padx=20)
        tk.Label(header, text=f"MODULO: {tipo}", font=("Consolas", 16, "bold"), fg=BLUE_ACCENT, bg=BG_PANEL).pack(side=tk.RIGHT, padx=20)

        ctrl = tk.Frame(frame, bg=BG_MAIN, pady=15)
        ctrl.pack(fill=tk.X, padx=20)

        if tipo == "STEGANO":
            self.drop_target = tk.Label(ctrl, text="\n[ TRASCINA QUI LA FOTO (JPG/PNG) PER ESTRARRE I DATI ]\n", font=("Consolas", 12, "bold"), bg=CONSOLE_BG, fg=BLUE_ACCENT, bd=2, relief=tk.GROOVE, height=5)
            self.drop_target.pack(pady=10, fill=tk.X)
            self.drop_target.drop_target_register(DND_FILES)
            self.drop_target.dnd_bind('<<Drop>>', self.processa_drop_stegano)

        elif tipo == "DECODER":
            self.drop_target = tk.Label(ctrl, text="\n[ TRASCINA QUI IL FILE .TXT DA DECODIFICARE ]\n", font=("Consolas", 12, "bold"), bg=CONSOLE_BG, fg=BLUE_ACCENT, bd=2, relief=tk.GROOVE, height=5)
            self.drop_target.pack(pady=10, fill=tk.X)
            self.drop_target.drop_target_register(DND_FILES)
            self.drop_target.dnd_bind('<<Drop>>', self.processa_drop_testo)

        else:
            self.entry_ip = tk.Entry(ctrl, font=("Consolas", 12), bg=CONSOLE_BG, fg=TEXT_DARK, insertbackground=TEXT_DARK, width=25)
            placeholder_text = "IP Target (es. 192.168.1.1)" if tipo != "SOCKET" else "Il tuo IP (es. 192.168.x.x)"
            self.setup_placeholder(self.entry_ip, placeholder_text)
            self.entry_ip.pack(side=tk.LEFT, padx=5, ipady=5)
            cmd_func = {"PORTE": self.avvia_porte, "HTTP": self.avvia_http, "SOCKET": self.avvia_socket}[tipo]
            tk.Button(ctrl, text="▶ AVVIA OPERAZIONE", font=("Consolas", 10, "bold"), bg=BLUE_ACCENT, fg="white", relief=tk.FLAT, command=cmd_func).pack(side=tk.LEFT, padx=10, ipady=3)

        self.text_area = scrolledtext.ScrolledText(frame, font=("Consolas", 10), bg=CONSOLE_BG, fg=CONSOLE_FG, bd=1, relief=tk.SOLID)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.log_message("Sistema in attesa di input...")

    def log_message(self, msg):
        if self.text_area and self.text_area.winfo_exists():
            self.text_area.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
            self.text_area.see(tk.END)

    def avvia_porte(self):
        t = self.entry_ip.get().strip()
        if not t or "es." in t:
            self.log_message("ERRORE: Inserisci un IP target valido.")
            return
        def task():
            self.log_message(f"Avvio scansione porte su {t}...")
            for p in PORTE_DA_CONTROLLARE:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                res = s.connect_ex((t, p))
                self.log_message(f" > Porta {p}: {'APERTA' if res == 0 else 'CHIUSA'}")
                s.close()
            self.log_message("Scansione completata.")
        threading.Thread(target=task, daemon=True).start()

    def avvia_http(self):
        t = self.entry_ip.get().strip()
        if not t or "es." in t:
            self.log_message("ERRORE: Inserisci un IP target valido.")
            return
        def task():
            self.log_message(f"Test Verbi HTTP su http://{t} ...")
            for m in ["GET", "POST", "PUT", "DELETE"]:
                try:
                    r = requests.request(m, f"http://{t}", headers=HEADER_EVASIONE, timeout=3)
                    self.log_message(f" > [{m}] Status Code: {r.status_code}")
                except:
                    self.log_message(f" > [{m}] Connessione fallita/Timeout")
            self.log_message("Analisi HTTP terminata.")
        threading.Thread(target=task, daemon=True).start()

    def avvia_socket(self):
        if self.sniffing: 
            self.sniffing = False
            return
        ip = self.entry_ip.get().strip()
        if not ip or "es." in ip:
            self.log_message("ERRORE: Inserisci la tua interfaccia IP locale.")
            return
        def task():
            self.sniffing = True
            self.log_message(f"Avvio Sniffer ICMP (Ping) su {ip}...")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                s.bind((ip, 0))
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                s.settimeout(1.0)
                while self.sniffing:
                    try:
                        d, a = s.recvfrom(65535)
                        self.log_message(f" [!] PING ICMP rilevato da: {a[0]} | Dimensione payload: {len(d)} byte")
                    except socket.timeout:
                        continue
            except PermissionError:
                self.log_message("ERRORE CRITICO: I Raw Sockets richiedono permessi di amministratore (usa 'sudo' su Kali Linux).")
            finally:
                self.sniffing = False
                self.log_message("Sniffer disattivato.")
        threading.Thread(target=task, daemon=True).start()

    def processa_drop_stegano(self, event):
        raw_path = event.data.strip('{}')
        if raw_path.startswith("file://"):
            raw_path = urllib.parse.unquote(raw_path[7:])
            
        self.log_message(f"Avviata estrazione steganografica sull'immagine: {os.path.basename(raw_path)}")
        try:
            img = Image.open(raw_path).convert("RGB")
            hidden = stepic.decode(img)
            
            if hidden:
                self.log_message("Dati nascosti rilevati! Preparazione per il salvataggio...")
                
                save_path = filedialog.asksaveasfilename(
                    title="Seleziona dove salvare il file estratto",
                    defaultextension=".txt",
                    filetypes=[("File di testo", "*.txt"), ("Tutti i file", "*.*")]
                )
                
                if not save_path:
                    self.log_message("Salvataggio annullato dall'utente.")
                    return

                if isinstance(hidden, str):
                    dati_da_salvare = hidden.encode()
                else:
                    dati_da_salvare = hidden

                with open(save_path, "wb") as f:
                    f.write(dati_da_salvare)
                
                # RIMOZIONE LUCCHETTO forzata
                try:
                    os.chmod(save_path, 0o777)
                except Exception:
                    pass
                    
                self.log_message(f"Completato! File smistato e salvato in: {save_path}")
                messagebox.showinfo("Rilevamento Positivo", f"Dati estratti e salvati in:\n{save_path}")
            else:
                self.log_message("Negativo. Nessun dato nascosto rilevato nell'immagine.")
                
        except Exception as e:
            self.log_message(f"Errore durante l'elaborazione dell'immagine: {str(e)}")

    def processa_drop_testo(self, event):
        # Pulizia del percorso su Kali
        raw_path = event.data.strip('{}')
        if raw_path.startswith("file://"):
            raw_path = urllib.parse.unquote(raw_path[7:])

        path = raw_path

        self.log_message(f"\n--- Analisi decodifica file: {os.path.basename(path)} ---")
        try:
            # error="ignore" permette di scavalcare i byte spazzatura generati dall'estrazione
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                
            if not content:
                self.log_message("Il file risulta vuoto o non contiene testo decifrabile.")
                return

            self.log_message(f"Anteprima testo estratto: {content[:50]}...")

            decodifiche_trovate = []

            # 1. ROT13 Forzato Manulamente (Anticrash)
            try:
                alfabeto_min = 'abcdefghijklmnopqrstuvwxyz'
                alfabeto_mai = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                rot13_trans = str.maketrans(alfabeto_mai + alfabeto_min, 
                                            alfabeto_mai[13:] + alfabeto_mai[:13] + 
                                            alfabeto_min[13:] + alfabeto_min[:13])
                
                dec_rot13 = content.translate(rot13_trans)
                if dec_rot13 != content:
                    decodifiche_trovate.append(("ROT13", dec_rot13))
            except Exception as e: 
                pass

            # 2. Base64 Sicuro
            try:
                padded = content + '=' * (-len(content) % 4)
                dec_b64 = base64.b64decode(padded).decode('utf-8')
                decodifiche_trovate.append(("Base64", dec_b64))
            except: pass

            # 3. Esadecimale (Hex)
            try:
                clean_hex = "".join(c for c in content if c in '0123456789abcdefABCDEF')
                if len(clean_hex) % 2 == 0 and len(clean_hex) > 0:
                    dec_hex = bytes.fromhex(clean_hex).decode('utf-8')
                    decodifiche_trovate.append(("Esadecimale", dec_hex))
            except: pass

            # 4. Binario
            try:
                clean_bin = "".join(c for c in content if c in '01')
                if len(clean_bin) >= 8 and len(clean_bin) % 8 == 0:
                    n = int(clean_bin, 2)
                    dec_bin = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8')
                    decodifiche_trovate.append(("Binario", dec_bin))
            except: pass

            # 5. Stringa Invertita
            if len(content) > 1:
                decodifiche_trovate.append(("Testo Invertito", content[::-1]))

            if decodifiche_trovate:
                self.log_message("--- RISULTATI DECIFRAZIONE ---")
                for nome_metodo, testo_decodificato in decodifiche_trovate:
                    self.log_message(f"\n[Metodo: {nome_metodo}]")
                    self.log_message(f"> {testo_decodificato}")
                self.log_message("\n------------------------------")
            else:
                self.log_message("Impossibile riconoscere una codifica nota. Il testo è già in chiaro o criptato.")
                
        except PermissionError:
            self.log_message("ERRORE PERMESSI (LUCCHETTO): Avvia il tool con privilegi 'sudo' o modifica i permessi del file.")
        except Exception as e:
            self.log_message(f"Errore durante l'apertura del file: {str(e)}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = NetworkApp(root)
    root.mainloop()
