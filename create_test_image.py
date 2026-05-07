from PIL import Image, ImageDraw

# Create a simple medical-like test image (500x500 pixels)
img = Image.new('RGB', (500, 500), color='white')
draw = ImageDraw.Draw(img)

# Draw some content 
draw.rectangle([50, 50, 450, 450], outline='black', width=3)
draw.text((180, 100), 'TEST IMAGE', fill='black')
draw.ellipse([150, 200, 350, 350], outline='blue', width=2)
draw.text((150, 380), 'Medical Scan Demo', fill='blue')

# Save it
img.save('test_image.png')
print('Test image created: test_image.png')
