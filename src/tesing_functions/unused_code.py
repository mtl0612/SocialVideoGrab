with open(f'{title}.png', 'wb') as image_file:
    image_file.write(response.meta['screenshot'])
with open(f'{title}.html', 'w') as f:
    f.write(page_source)

