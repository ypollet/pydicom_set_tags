from tifffile import imread, TiffFile

image_stack = TiffFile('/home/psadmin/Leica-1.tiff')

print(len(image_stack.pages))
for i in range(len(image_stack.pages)):
    page = image_stack.pages[i]
    print(page.shape)
