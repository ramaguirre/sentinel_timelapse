def load_image(image_path):
    """Load an image from the specified path."""
    from PIL import Image
    return Image.open(image_path)

def save_image(image, save_path):
    """Save the image to the specified path."""
    image.save(save_path)

def calculate_duration(start_time, end_time):
    """Calculate the duration between two time points."""
    return end_time - start_time