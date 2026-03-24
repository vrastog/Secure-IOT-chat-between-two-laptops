import socket
import os
import threading
import customtkinter as ctk
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Set overall theme
ctk.set_appearance_mode("dark")

class ServerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Secure IoT Chat - SERVER")
        self.geometry("500x650")
        self.configure(fg_color="#0b141a") # Deep WhatsApp background

        # --- UI SETUP (WhatsApp Style) ---
        self.chat_box = ctk.CTkTextbox(
            self, state="disabled", wrap="word", font=("Helvetica", 15), 
            fg_color="#111B21", text_color="#E9EDEF"
        )
        self.chat_box.pack(pady=10, padx=10, fill="both", expand=True)

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(0, 15), padx=15, fill="x", side="bottom")

        self.message_entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="Message", font=("Helvetica", 15), 
            height=45, corner_radius=25, fg_color="#2A3942", border_width=0, text_color="white"
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message_event)

        self.send_button = ctk.CTkButton(
            self.input_frame, text="➤", font=("Arial", 22), command=self.send_message, 
            width=45, height=45, corner_radius=25, fg_color="#00A884", hover_color="#029071", text_color="white"
        )
        self.send_button.pack(side="right")

        self.update_chat("[*] Server Booted. Waiting for client...\n\n")

        # --- NETWORK VARIABLES ---
        self.conn = None
        self.aesgcm = None

        # --- START BACKGROUND THREAD ---
        threading.Thread(target=self.backend_network_loop, daemon=True).start()

    def update_chat(self, text):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", text)
        self.chat_box.configure(state="disabled")
        self.chat_box.yview("end")

    def send_message_event(self, event):
        self.send_message()

    def send_message(self):
        msg = self.message_entry.get()
        if msg.strip() == "" or self.conn is None or self.aesgcm is None:
            return

        self.update_chat(f"You: {msg}\n")
        self.message_entry.delete(0, "end")

        try:
            nonce = os.urandom(12)
            ciphertext = self.aesgcm.encrypt(nonce, msg.encode('utf-8'), None)
            self.conn.sendall(nonce + ciphertext)
        except Exception as e:
            self.update_chat(f"[-] Connection Error.\n")

    def backend_network_loop(self):
        HOST = '0.0.0.0'
        PORT = 5555       

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        
        try:
            self.conn, addr = server_socket.accept()
            self.update_chat(f"[+] Connected by {addr}\n[*] Negotiating Encryption Keys...\n")

            # MODULE 2: ECDH KEY EXCHANGE
            server_private_key = ec.generate_private_key(ec.SECP256R1())
            server_public_key = server_private_key.public_key()
            server_pub_bytes = server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
            
            self.conn.sendall(server_pub_bytes)
            client_pub_bytes = self.conn.recv(1024)
            client_public_key = serialization.load_pem_public_key(client_pub_bytes)
            
            shared_secret = server_private_key.exchange(ec.ECDH(), client_public_key)
            self.aesgcm = AESGCM(shared_secret)
            self.update_chat(f"[+] E2EE Session Active! (Key: {shared_secret[:8].hex()}...)\n\n")

            # MODULE 3: RECEIVE AND DECRYPT LOOP
            while True:
                data = self.conn.recv(1024)
                if not data:
                    break 
                
                recv_nonce = data[:12]
                recv_ciphertext = data[12:]
                plaintext = self.aesgcm.decrypt(recv_nonce, recv_ciphertext, None)
                self.update_chat(f"Client: {plaintext.decode('utf-8')}\n")
                
        except Exception as e:
            self.update_chat(f"\n[-] Network disconnected.\n")
        finally:
            server_socket.close()

if __name__ == "__main__":
    app = ServerGUI()
    app.mainloop()