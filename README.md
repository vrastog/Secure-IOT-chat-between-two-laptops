# Secure-IOT-chat-between-two-laptops

A lightweight, fully functional End-to-End Encrypted (E2EE) messaging application built in Python. Designed to simulate secure communication between resource-constrained IoT edge nodes, this project implements military-grade cryptographic protocols over local TCP/IP sockets, entirely wrapped in a modern, asynchronous graphical user interface.

### Key Features
* **End-to-End Encryption:** Utilizes **AES-GCM** to ensure absolute message confidentiality and cryptographic integrity (tamper-proofing) for every payload.
* **Dynamic Key Exchange:** Implements **Elliptic Curve Diffie-Hellman (ECDH)** to securely negotiate shared session keys over unsecure networks without ever transmitting the secret.
* **Asynchronous Networking:** Leverages Python's `threading` module to handle continuous, real-time socket listening in the background without freezing the UI.
* **Modern GUI:** Features a sleek, responsive, WhatsApp-inspired dark mode interface built with `customtkinter`.

### Tech Stack
* **Language:** Python 3
* **Networking:** `socket` (TCP/IP)
* **Cryptography:** `cryptography` (Hazmat primitives)
* **Frontend:** `customtkinter`


### How to Run Locally

1. Clone the repository to your local machine.
2. Install the required dependencies:
   `pip install cryptography customtkinter`
3. Run the Server script on the first machine (or terminal):
   `python server_gui.py`
4. Update the `HOST` variable in `client_gui.py` to match the Server's local IP address.
5. Run the Client script on the second machine (or a separate terminal):
   `python client_gui.py`
