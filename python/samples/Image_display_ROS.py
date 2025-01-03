import socket
import tkinter as tk
from PIL import Image, ImageTk
import threading
import rospy
from std_msgs.msg import String
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

def emotion_callback(data):
    """Callback function to update the global emotion variable based on the received message."""
    global emotion
    rospy.loginfo(f"Received emotion: {data.data}")
    if data.data in image_list:
        emotion = data.data
    else:
        rospy.logwarn(f"Emotion '{data.data}' not found in image_list. Keeping current emotion.")


def update_image(window,label,):
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
     # Initialize ROS node
    rospy.init_node('emotion_listener', anonymous=True)

    # Subscribe to the 'emotion' topic
    rospy.Subscriber("emotion", String, emotion_callback)

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


if __name__ == '__main__':
    try:
        image_loop()
    except rospy.ROSInterruptException:
        pass
