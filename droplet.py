import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import skimage.feature

def edges_image(img, sigma=3, low_threshold=0.9, high_threshold=0.95):
    gray_img = img[:,:,0]
    return skimage.feature.canny(
        gray_img,
        sigma=sigma,
        low_threshold=low_threshold,
        high_threshold=high_threshold,
        use_quantiles=True)


def add_padding(img, width, height):
    img_height = len(img)
    img_width = len(img[0])
    padding_height = (height - img_height) / 2
    padding_width = (width - img_width) / 2
    start_top = int(padding_height)
    end_top = int(img_height + padding_height)
    start_left = int(padding_width)
    end_left = int(img_width + padding_width)
    if len(img.shape) == 2:
        resized = np.empty([height, width])
        resized[start_top:end_top, start_left:end_left] = img
    elif len(img.shape) == 3:
        resized = np.empty([height, width, 3])
        resized[start_top:end_top, start_left:end_left, :] = img
    return resized


def remove_padding(img, width, height):
    img_height = len(img)
    img_width = len(img[0])
    padding_height = (img_height - height) / 2
    padding_width = (img_width - width) / 2
    start_top = int(padding_height)
    end_top = int(height + padding_height)
    start_left = int(padding_width)
    end_left = int(width + padding_width)
    if len(img.shape) == 2:
        resized = img[start_top:end_top, start_left:end_left]
    elif len(img.shape) == 3:
        resized = img[start_top:end_top, start_left:end_left, :]
    return resized


def draw_circles(img, cy, cx, radii, color=(220, 20, 20)):
    for center_y, center_x, radius in zip(cy, cx, radii):
        circy, circx = skimage.draw.circle_perimeter(center_y, center_x, radius)
        img[circy, circx] = color


def find_circles(img, possible_radii=np.arange(150, 400, 10)):
    hough_res = skimage.transform.hough_circle(img, possible_radii)
    accums, cx, cy, radii = skimage.transform.hough_circle_peaks(
        hough_res, possible_radii, total_num_peaks=2)
    return cx, cy, radii


def find_circles_in_image(img_dir, img_file):
    img = plt.imread(os.path.join(img_dir, img_file))
    resized = add_padding(img, 2000, 1100)
    resized_edges = add_padding(edges_image(img), 2000, 1100)

    cx, cy, radii = find_circles(resized_edges)
    resized_edges = skimage.color.gray2rgb(resized_edges)
    draw_circles(resized, cy, cx, radii)
    draw_circles(resized_edges, cy, cx, radii)

    dpi = 96
    width = len(img[0]) / dpi
    height = len(img) / dpi
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(width, height), dpi=dpi)
    ax.imshow(remove_padding(resized, len(img[0]), len(img)), cmap=plt.cm.gray)
    processed_dir = os.path.join(os.path.dirname(img_dir), 'processed')
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    fig.savefig(os.path.join(processed_dir, img_file), bbox_inches='tight')
    return cx, cy, radii
