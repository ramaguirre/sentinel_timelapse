class Timelapse:
    def __init__(self):
        self.is_running = False

    def start(self):
        self.is_running = True
        print("Timelapse started.")

    def stop(self):
        self.is_running = False
        print("Timelapse stopped.")

    def process_frame(self, frame):
        if not self.is_running:
            print("Timelapse is not running. Please start it first.")
            return
        # Process the frame (placeholder for actual processing logic)
        print(f"Processing frame: {frame}")