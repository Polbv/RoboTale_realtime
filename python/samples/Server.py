import socket
import tkinter as tk
from PIL import Image, ImageTk
import threading

image_list={}
image_list["question"]="input/Questions.jpeg"
image_list["exclamation"]="input/surprise.jpeg"
image_list["joy"]="input/joy.jpeg"
image_list["love"]="input/love.png"
image_list["surprise"]="input/surprise.jpeg"
image_list["fear"]="input/fear.jpeg"
image_list["sadness"]="input/sadness.jpg"
# Create the main window
current_image_path = "input/joy.jpeg"
emotion="joy"


def update_image(window, label):
    """Continuously checks for updates to the global image path and updates the displayed image."""
    global current_image_path
    global image_list
    global emotion
    
    current_image_path = image_list[emotion]
        #print(sentence_dict[str(text_chunk_index)]["sentence_emotion"])
    # Load and display the updated image
    img = Image.open(current_image_path)
    #img = img.resize((400, 300), Image.ANTIALIAS)  # Resize for display
    tk_img = ImageTk.PhotoImage(img)
    label.config(image=tk_img)
    label.image = tk_img  # Keep a reference to avoid garbage collection

    # Call this function again after 500ms
    window.after(50, update_image, window, label)

def image_loop():
    """Main function to set up the window and start the update loop."""
    global current_image_path

    # Create the main window
    window = tk.Tk()
    window.title("Real-Time Image Viewer")

    # Create a label to display the image
    img = Image.open(current_image_path)
    #img = img.resize((400, 300), Image.ANTIALIAS)
    tk_img = ImageTk.PhotoImage(img)
    label = tk.Label(window, image=tk_img)
    label.pack()
   
    # Start the update loop
    update_image(window, label)

    # Run the application
    window.mainloop()

#




def socket_setup():
        #Create a socket
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to an IP and port
    HOST = '0.0.0.0'  # Listen on all available interfaces
    PORT = 12345      # Use a port not in use
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen(5)  # Allow up to 5 connections
    print(f"Server listening on {HOST}:{PORT}")
    
def socket_recieve():
         global server_socket,emotion
         emoption="joy"
         while True:
            # Accept an incoming connection
            client_socket, client_address = server_socket.accept()
            print(f"Connection established with {client_address}")
            while True:
                try:
                    # Receive data from the client
                    message = client_socket.recv(1024).decode('utf-8')
                    emotion=message 
                    if message != last_message: 
                        print(f"Received: {message}")
                        last_message = message

                    # Send a response back
                    client_socket.send("Message received!".encode('utf-8'))

                except KeyboardInterrupt:
                    # Close the connection
                    client_socket.close()
                    print("\nServer shutting down.")
                    server_socket.close()
                    exit()
def main():
    socket_setup()

    thread = threading.Thread(target=socket_recieve)
    thread.start()
    image_loop()
main()
