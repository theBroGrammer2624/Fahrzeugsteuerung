import tkinter as tk
import picamera2
import threading
from PIL import Image, ImageTk

class CameraApp:
    def __init__(self, master, **kwargs):
        self.master = master
        self.master.title("Pi Camera Viewer")

        self.camera = picamera2.Picamera2()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 30

        self.video_frame = tk.Label(master)
        self.video_frame.pack()

        self.quit_button = tk.Button(master, text="Quit", command=self.quit)
        self.quit_button.pack()

        self.update_video()

    def update_video(self):
        frame = self.capture_frame()
        if frame is not None:
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.video_frame.config(image=photo)
            self.video_frame.image = photo

        self.master.after(10, self.update_video)

    def capture_frame(self):
        try:
            image = Image.new("RGB", (self.camera.resolution[0], self.camera.resolution[1]))
            self.camera.raw_capture(image, format="rgb")
            return image
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None

    def quit(self):
        self.camera.close()
        self.master.destroy()

def main():
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
