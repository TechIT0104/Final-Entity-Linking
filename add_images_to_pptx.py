import os
from pptx import Presentation
from pptx.util import Inches

pptx_path = r"C:\Users\Dhruv\OneDrive\Desktop\Final Entity Linking\Board_Review_Presentation.pptx"
img_dir = r"C:\Users\Dhruv\OneDrive\Desktop\Final Entity Linking\images"

prs = Presentation(pptx_path)

# Dictionary defining which image goes on which slide and where 
# (Slide index is 0-based)
image_placements = [
    # Slide 8 (index 7): Implementation Details -> MHEL Architecture
    (7, "mhel_llamo_arch.png", Inches(4.8), Inches(2.5), Inches(4.7), None),
    
    # Slide 16 (index 15): Results & Observations -> MEWSLI F1 Results
    (15, "mewsli9_f1.png", Inches(4.8), Inches(2.2), Inches(4.7), None),
    
    # Slide 3 (index 2): Entity Linking Foundation -> BLINK benchmark
    (2, "blink_benchmark_bar.png", Inches(0.5), Inches(5.0), None, Inches(2.2)),
    
    # Slide 4 (index 3): Motivation & Overview -> MVD Recall Curve
    (3, "mvd_recall_curve.png", Inches(5.0), Inches(3.8), Inches(4.5), None)
]

for slide_idx, img_name, left, top, width, height in image_placements:
    try:
        img_path = os.path.join(img_dir, img_name)
        if os.path.exists(img_path):
            slide = prs.slides[slide_idx]
            if width and not height:
                slide.shapes.add_picture(img_path, left, top, width=width)
            elif height and not width:
                slide.shapes.add_picture(img_path, left, top, height=height)
            else:
                slide.shapes.add_picture(img_path, left, top, width=width, height=height)
            print(f"Added {img_name} to Slide {slide_idx+1}")
        else:
            print(f"Image not found: {img_path}")
    except Exception as e:
        print(f"Failed to add {img_name} to Slide {slide_idx+1}: {e}")

prs.save(pptx_path)
print("Images embedded and PPTX saved successfully!")
