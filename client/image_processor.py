from PIL import Image

class ImageProcessor:
    def __init__(self):
        pass
    
    def crop_around_point(self, image, center_x, center_y, crop_size=100):
        width, height = image.size
        
        left = max(0, center_x - crop_size)
        top = max(0, center_y - crop_size)
        right = min(width, center_x + crop_size)
        bottom = min(height, center_y + crop_size)
        
        cropped_image = image.crop((left, top, right, bottom))
        return cropped_image
    
    def resize_image(self, image, new_size):
        return image.resize(new_size, Image.Resampling.LANCZOS) 