import io
import numpy as np
from PIL import Image, ImageFilter


def image_bytes_to_sketch_bytes(input_bytes: bytes) -> bytes:
    """
    Converts an input image (as bytes) to a sketch art style image (as bytes).
    Uses only Pillow + numpy (no scipy/matplotlib needed).
    """
    img = Image.open(io.BytesIO(input_bytes)).convert('RGB')

    # Convert to grayscale
    gray = img.convert('L')

    # Invert
    inverted = Image.eval(gray, lambda px: 255 - px)

    # Gaussian blur the inverted image (radius ~5 approximates scipy sigma=5)
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=5))

    # Color dodge blend: gray / (255 - blurred) * 256
    gray_np = np.array(gray, dtype=np.float32)
    blurred_np = np.array(blurred, dtype=np.float32)
    inverted_blurred = 255.0 - blurred_np

    # Dodge: divide gray by inverted-blurred, scale back
    epsilon = 1e-5
    sketch = gray_np / (inverted_blurred / 255.0 + epsilon) * 255.0
    sketch = np.clip(sketch, 0, 255).astype(np.uint8)

    # Edge enhancement via PIL FIND_EDGES kernel
    sketch_img = Image.fromarray(sketch, mode='L')
    edges = sketch_img.filter(ImageFilter.FIND_EDGES)
    edges_np = np.array(edges, dtype=np.float32)

    # Combine sketch with inverted edges for bold outlines
    final = 0.7 * sketch.astype(np.float32) + 0.3 * (255.0 - edges_np)
    final = np.clip(final, 0, 255).astype(np.uint8)

    out_img = Image.fromarray(final, mode='L')

    buf = io.BytesIO()
    out_img.save(buf, format='PNG')
    return buf.getvalue()
