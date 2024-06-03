import os
from PIL import Image, ImageDraw
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


def generate_image(index, row, base_image, output_dir, img_size):
    img = base_image.copy()
    draw = ImageDraw.Draw(img)

    x = row['norm_lon'] * img_size[0]
    y = img_size[1] - row['norm_lat'] * img_size[1]
    draw.ellipse([x-5, y-5, x+5, y+5], fill="orange")

    img.save(os.path.join(output_dir, f'frame_{index+1:04d}.png'))


def create_images(points_df, output_dir, img_size):
    os.makedirs(output_dir, exist_ok=True)

    route_image = Image.new('RGBA', img_size, (0, 0, 0, 0))
    route_draw = ImageDraw.Draw(route_image)

    scaled_lons = points_df['norm_lon'] * img_size[0]
    scaled_lats = img_size[1] - points_df['norm_lat'] * img_size[1]

    for i in range(1, len(points_df)):
        route_draw.line(
            [
                (scaled_lons.iloc[i-1], scaled_lats.iloc[i-1]),
                (scaled_lons.iloc[i], scaled_lats.iloc[i])
            ],
            fill="white",
            width=3
        )

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(generate_image, index, row,
                            route_image, output_dir, img_size)
            for index, row in points_df.iterrows()
        ]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating images"):
            future.result()

    print(f'Images saved in directory: {output_dir}')
