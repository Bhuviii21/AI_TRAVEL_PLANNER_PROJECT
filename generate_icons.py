from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
import math

def create_icon(size, filename):
    """Create a PWA icon with the given size"""
    
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for i in range(size):
        for j in range(size):
            # Calculate distance from center
            x = (i - size/2) / size
            y = (j - size/2) / size
            dist = math.sqrt(x*x + y*y)
            
            # Create gradient color
            if dist < 0.5:
                # Center: lighter blue
                r = int(56 + (37 - 56) * (dist * 2))
                g = int(189 + (99 - 189) * (dist * 2))
                b = int(248 + (235 - 248) * (dist * 2))
            else:
                # Edge: darker blue
                r = int(37 + (56 - 37) * ((dist - 0.5) * 2))
                g = int(99 + (189 - 99) * ((dist - 0.5) * 2))
                b = int(235 + (248 - 235) * ((dist - 0.5) * 2))
            
            # Clamp color values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            draw.point((i, j), fill=(r, g, b, 255))
    
    # Draw rounded square overlay with transparency using RGB + alpha
    margin = size * 0.05
    radius = size * 0.15
    
    # Create a temporary overlay image
    overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Draw rounded rectangle with white fill and opacity
    overlay_draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill=(255, 255, 255, 20)  # RGBA with ~8% opacity (20/255)
    )
    
    # Composite the overlay onto the main image
    img = Image.alpha_composite(img, overlay)
    
    # Draw travel icon (airplane emoji)
    try:
        # Try to load a font
        font_size = int(size * 0.45)
        try:
            # Use Arial font if available
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw airplane symbol
        draw = ImageDraw.Draw(img)
        draw.text(
            (size/2 - font_size/4, size/2 - font_size/4),
            '✈',
            fill=(255, 255, 255, 255),
            font=font
        )
        
        # Draw "AI" text for larger icons
        if size >= 128:
            try:
                ai_font = ImageFont.truetype("arial.ttf", int(size * 0.1))
            except:
                ai_font = ImageFont.load_default()
            
            draw.text(
                (size/2 - size*0.05, size*0.85 - size*0.05),
                'AI',
                fill=(255, 255, 255, 179),  # ~70% opacity
                font=ai_font
            )
            
    except Exception as e:
        print(f"Warning: Could not draw text on icon: {e}")
        # Draw a simple circle as fallback
        draw = ImageDraw.Draw(img)
        draw.ellipse(
            [size*0.2, size*0.2, size*0.8, size*0.8],
            fill=(255, 255, 255, 77)  # ~30% opacity
        )
    
    # Convert to RGB for saving (some viewers don't support RGBA PNG)
    if size >= 192:  # For larger icons, keep transparency
        img.save(filename, 'PNG')
    else:  # For smaller icons, convert to RGB with white background
        rgb_img = Image.new('RGB', (size, size), (255, 255, 255))
        rgb_img.paste(img, (0, 0), img)
        rgb_img.save(filename, 'PNG')
    
    print(f"✓ Created {filename}")

# Main execution
if __name__ == '__main__':
    # Create icons directory
    os.makedirs('static/icons', exist_ok=True)
    
    # Generate icons of different sizes
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    print("🎨 Generating PWA icons...")
    print("=" * 50)
    
    for size in sizes:
        filename = f'static/icons/icon-{size}x{size}.png'
        create_icon(size, filename)
    
    print("=" * 50)
    print("✅ All icons generated successfully!")
    print(f"📁 Saved in: static/icons/")
    print("📱 Ready to use with your PWA manifest.json")