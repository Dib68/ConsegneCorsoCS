import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import requests
import os
import threading
import datetime
import cv2
from PIL import Image, ImageTk

# --- VARIABILI DI CONFIGURAZIONE GLOBALI ---
PORTE_DA_CONTROLLARE = [21, 22, 25, 53, 80, 110, 139, 143, 443, 445, 3306, 8080]
HEADER_EVASIONE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive"
}
FILE_LOG = "network_tool_log.txt"
VIDEO_PATH = "Video_D_Generato_su_Richiesta.mp4"

# --- PALETTE COLORI (Stile Digital Avengers) ---
BG_MAIN = "#FFFFFF"         # Bianco di sfondo
BG_PANEL = "#F0F2F5"        # Grigio chiarissimo per i pannelli
BLUE_ACCENT = "#007BFF"     # Blu scudo/fulmine
BLUE_HOVER = "#0056b3"      # Blu scuro per hover bottoni
TEXT_DARK = "#1A1A1A"       # Testo scuro
CONSOLE_BG = "#1E222A"      # Sfondo console (hacker style)
CONSOLE_FG = "#00D2FF"      # Testo console azzurro acceso


class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Avengers - Security Tool")
        self.root.geometry("850x650")
        self.root.configure(bg=BG_MAIN)
        
        self.sniffing = False
        self.current_frame = None
        
        # Variabili per gestire i widget delle singole viste
        self.text_area = None 
        self.entry_ip = None

        # Avvio dalla schermata di Login
        self.mostra_schermata_login()

    def cambia_schermata(self, nuovo_frame_func):
        """Distrugge la schermata attuale e carica la nuova"""
        if self.current_frame is not None:
            self.current_frame.destroy()
        
        # Ferma lo sniffer se l'utente cambia schermata mentre è attivo
        self.sniffing = False 
        
        self.current_frame = tk.Frame(self.root, bg=BG_MAIN)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        nuovo_frame_func(self.current_frame)

    # ==========================================
    # 1. SCHERMATA DI LOGIN (CORRETTA)
    # ==========================================
    def mostra_schermata_login(self):
        self.cambia_schermata(self.costruisci_login)

    def costruisci_login(self, frame):
        panel = tk.Frame(frame, bg=BG_PANEL, bd=2, relief=tk.GROOVE)
        panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=350)

        tk.Label(panel, text="AUTENTICAZIONE", font=("Arial", 18, "bold"), fg=BLUE_ACCENT, bg=BG_PANEL).pack(pady=(30, 20))

        tk.Label(panel, text="Username:", font=("Arial", 12), fg=TEXT_DARK, bg=BG_PANEL).pack()
        entry_user = tk.Entry(panel, font=("Arial", 14), justify="center")
        entry_user.insert(0, "admin") # Precompilato per comodità
        entry_user.pack(pady=5)

        tk.Label(panel, text="Password:", font=("Arial", 12), fg=TEXT_DARK, bg=BG_PANEL).pack(pady=(10,0))
        entry_pwd = tk.Entry(panel, font=("Arial", 14), justify="center", show="*")
        entry_pwd.insert(0, "avengers") # Precompilato per comodità
        entry_pwd.pack(pady=5)

        # La funzione di controllo è all'interno, così "vede" entry_user ed entry_pwd
        def esegui_login(event=None):
            user = entry_user.get()
            pwd = entry_pwd.get()
            
            # Controllo credenziali (corretto con le stringhe)
            if user == "admin" and pwd == "avengers":
                self.cambia_schermata(self.mostra_schermata_video)
            else:
                messagebox.showerror("Accesso Negato", "Credenziali errate. Riprova.")

        btn_login = tk.Button(panel, text="ACCEDI", font=("Arial", 12, "bold"), bg=BLUE_ACCENT, fg="white", 
                              activebackground=BLUE_HOVER, command=esegui_login)
        btn_login.pack(pady=30, fill=tk.X, padx=50)
        
        # Permette di premere "Invio" sulla tastiera per fare il login
        self.root.bind('<Return>', esegui_login)

    # ==========================================
    # 2. SCHERMATA VIDEO INTRODUTTIVO
    # ==========================================
    def mostra_schermata_video(self, frame):
        self.root.unbind('<Return>') # Rimuove il bind dell'invio dal login
        
        if not os.path.exists(VIDEO_PATH):
            print(f"[AVVISO] Video '{VIDEO_PATH}' non trovato. Salto al menu.")
            self.cambia_schermata(self.mostra_menu_principale)
            return

        lbl_video = tk.Label(frame, bg="black")
        lbl_video.pack(fill=tk.BOTH, expand=True)
        
        cap = cv2.VideoCapture(VIDEO_PATH)

        def aggiorna_frame():
            ret, cv_frame = cap.read()
            if ret:
                # Converte l'immagine per Tkinter
                cv_frame = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv_frame)
                
                # Ridimensiona mantenendo le proporzioni
                win_width, win_height = self.root.winfo_width(), self.root.winfo_height()
                if win_width > 10 and win_height > 10:
                    img.thumbnail((win_width, win_height), Image.Resampling.LANCZOS)
                
                imgtk = ImageTk.PhotoImage(image=img)
                lbl_video.imgtk = imgtk
                lbl_video.configure(image=imgtk)
                lbl_video.after(30, aggiorna_frame) # ~30 fps
            else:
                cap.release()
                self.cambia_schermata(self.mostra_menu_principale)

        aggiorna_frame()

    # ==========================================
    # 3. MENU PRINCIPALE ISOLATO
    # ==========================================
    def mostra_menu_principale(self, frame=None):
        if frame is None:
            self.cambia_schermata(self.mostra_menu_principale)
            return

        lbl_titolo = tk.Label(frame, text="DIGITAL AVENGERS", font=("Arial", 28, "bold"), fg=BLUE_ACCENT, bg=BG_MAIN)
        lbl_titolo.pack(pady=(50, 10))
        tk.Label(frame, text="Seleziona il modulo operativo:", font=("Arial", 14), fg=TEXT_DARK, bg=BG_MAIN).pack(pady=(0, 40))

        frame_bottoni = tk.Frame(frame, bg=BG_MAIN)
        frame_bottoni.pack()

        btn_style = {"font": ("Arial", 14, "bold"), "bg": BG_PANEL, "fg": BLUE_ACCENT, "width": 20, "pady": 15, "bd": 2, "relief": tk.RIDGE}

        tk.Button(frame_bottoni, text="Scansione PORTE", command=lambda: self.mostra_tool("PORTE"), **btn_style).pack(pady=10)
        tk.Button(frame_bottoni, text="Verifica Verbi HTTP", command=lambda: self.mostra_tool("HTTP"), **btn_style).pack(pady=10)
        tk.Button(frame_bottoni, text="Sniffing SOCKET", command=lambda: self.mostra_tool("SOCKET"), **btn_style).pack(pady=10)
        
        tk.Button(frame, text="ESCI DAL SISTEMA", font=("Arial", 12, "bold"), bg="#d9534f", fg="white", 
                  width=20, pady=10, command=self.root.quit).pack(side=tk.BOTTOM, pady=40)

    # ==========================================
    # 4. SCHERMATE DEI SINGOLI TOOL
    # ==========================================
    def mostra_tool(self, tipo_tool):
        self.cambia_schermata(lambda frame: self.costruisci_interfaccia_tool(frame, tipo_tool))

    def costruisci_interfaccia_tool(self, frame, tipo_tool):
        # Header del Tool
        header = tk.Frame(frame, bg=BLUE_ACCENT, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Button(header, text="← Torna al Menu", font=("Arial", 12, "bold"), bg=BG_MAIN, fg=BLUE_ACCENT, 
                  command=self.mostra_menu_principale).pack(side=tk.LEFT, padx=20)
        
        tk.Label(header, text=f"MODULO: {tipo_tool}", font=("Arial", 18, "bold"), fg="white", bg=BLUE_ACCENT).pack(side=tk.RIGHT, padx=20)

        # Controlli (Input IP e Bottone Avvio)
        controlli = tk.Frame(frame, bg=BG_PANEL, pady=15)
        controlli.pack(fill=tk.X)

        testo_ip = "IP Locale (es. 192.168.x.x):" if tipo_tool == "SOCKET" else "IP Target (es. 192.168.50.101):"
        ip_default = "192.168.60.100" if tipo_tool == "SOCKET" else "192.168.50.101"

        tk.Label(controlli, text=testo_ip, font=("Arial", 12, "bold"), bg=BG_PANEL, fg=TEXT_DARK).pack(side=tk.LEFT, padx=20)
        
        self.entry_ip = tk.Entry(controlli, font=("Arial", 14), width=15, justify="center")
        self.entry_ip.insert(0, ip_default)
        self.entry_ip.pack(side=tk.LEFT, padx=10)

        cmd = None
        if tipo_tool == "PORTE": cmd = self.avvia_porte
        elif tipo_tool == "HTTP": cmd = self.avvia_http
        elif tipo_tool == "SOCKET": cmd = self.avvia_socket

        tk.Button(controlli, text="AVVIA OPERAZIONE", font=("Arial", 12, "bold"), bg=BLUE_ACCENT, fg="white", 
                  activebackground=BLUE_HOVER, command=cmd).pack(side=tk.LEFT, padx=20)

        # Area Log Console
        self.text_area = scrolledtext.ScrolledText(frame, font=("Consolas", 11), bg=CONSOLE_BG, fg=CONSOLE_FG, bd=0)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.log_message(f"--- Modulo {tipo_tool} Inizializzato ---\nPronto all'esecuzione.")

    def log_message(self, message):
        """Scrive nel log in modo sicuro e salva su file"""
        # Controlla se la text_area esiste ancora (l'utente potrebbe essere tornato al menu)
        if self.text_area and self.text_area.winfo_exists():
            self.text_area.insert(tk.END, message + "\n")
            self.text_area.see(tk.END) 
        
        try:
            with open(FILE_LOG, "a", encoding="utf-8") as f:
                orario = datetime.datetime.now().strftime("%H:%M:%S")
                f.write(f"[{orario}] {message}\n")
        except: pass

    # ==========================================
    # LOGICA DI RETE DEI TOOL
    # ==========================================
    def avvia_porte(self):
        target_ip = self.entry_ip.get().strip()
        if not target_ip: return self.log_message("[ERRORE] Inserisci un IP valido.")
        
        def task():
            self.log_message(f"\n[*] Avvio scansione PORTE su {target_ip}...")
            for porta in PORTE_DA_CONTROLLARE:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                try:
                    res = sock.connect_ex((target_ip, porta))
                    stato = "APERTA" if res == 0 else "CHIUSA/FILTRATA"
                    self.log_message(f"  -> Porta {porta}: {stato}")
                except Exception as e:
                    self.log_message(f"  -> Porta {porta}: ERRORE ({e})")
                finally:
                    sock.close()
            self.log_message("[*] Scansione Porte Completata.")
            
        threading.Thread(target=task, daemon=True).start()

    def avvia_http(self):
        target_ip = self.entry_ip.get().strip()
        if not target_ip: return self.log_message("[ERRORE] Inserisci un IP valido.")

        def task():
            target_url = f"http://{target_ip}"
            verbi = {"GET": requests.get, "POST": requests.post, "PUT": requests.put, "DELETE": requests.delete}
            self.log_message(f"\n[*] Avvio verifica VERBI HTTP su {target_url}...")
            
            for metodo, req_func in verbi.items():
                try:
                    if metodo in ["POST", "PUT"]:
                        risp = req_func(target_url, data={"test": "dati"}, headers=HEADER_EVASIONE, timeout=5)
                    else:
                        risp = req_func(target_url, headers=HEADER_EVASIONE, timeout=5)
                    
                    abilitato = risp.status_code < 400
                    self.log_message(f"  -> [{metodo}] Esito: {abilitato} (Codice: {risp.status_code})")
                except Exception as e:
                    self.log_message(f"  -> [{metodo}] Esito: False (Errore/Timeout)")
            self.log_message("[*] Verifica HTTP Completata.")
            
        threading.Thread(target=task, daemon=True).start()

    def avvia_socket(self):
        local_ip = self.entry_ip.get().strip()
        if not local_ip: return self.log_message("[ERRORE] Inserisci un IP Locale valido.")

        if self.sniffing:
            self.sniffing = False
            self.log_message("[*] Sniffer interrotto.")
            return

        def task():
            self.sniffing = True
            self.log_message(f"\n[*] Avvio SNIFFER SOCKET su {local_ip}...")
            proto = socket.IPPROTO_IP if os.name == 'nt' else socket.IPPROTO_ICMP 
            try:
                sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto)
                sniffer.bind((local_ip, 0))
                sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                if os.name == 'nt': sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
                
                sniffer.settimeout(1.0)
                self.log_message("[*] In ascolto... (Premi 'Avvia Operazione' di nuovo per fermare o torna al menu)")

                while self.sniffing:
                    try:
                        pacchetto, addr = sniffer.recvfrom(65565)
                        self.log_message(f"  [>] Pacchetto da: {addr[0]} | Byte: {len(pacchetto)}")
                    except socket.timeout: continue

            except PermissionError:
                self.log_message("[ERRORE CRITICO] Permessi insufficienti. Avvia l'eseguibile con 'sudo'.")
            except Exception as e:
                self.log_message(f"[ERRORE] {e}")
            finally:
                if os.name == 'nt' and 'sniffer' in locals() and not isinstance(sniffer, Exception):
                    try: sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
                    except: pass
                self.sniffing = False
                self.log_message("[*] Sniffer Terminati in modo sicuro.")

        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()
