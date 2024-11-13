# import required libraries
import cv2, time
import numpy as np
import pickle
starttime = time.time()


# taken from https://stackoverflow.com/questions/40895785/using-opencv-to-overlay-transparent-image-onto-another-image
def overlay_transparent(background, overlay, x, y):
    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
            ],
            axis = 2,
        )

    mask = overlay[..., 3:] / 255.0
    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay

    return background

# taken from https://stackoverflow.com/questions/43892506/opencv-python-rotate-image-without-cropping-sides
def rotate_image(mat, angle):
    """
    Rotates an image (angle in degrees) and expands image to avoid cropping
    """

    height, width = mat.shape[:2] # image shape has 3 dimensions
    image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0,0]) 
    abs_sin = abs(rotation_mat[0,1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat, bound_w, bound_h


def get_all_slices(attrs, num_slices, num_angles, viewing_angle, scale): # todo pull these params from attrs anyway
    cacheout = []
    starttime = time.time()
    print("rotating", attrs['path'])
    # load the input image
    img = cv2.imread(attrs['path'], cv2.IMREAD_UNCHANGED)
    img[..., :3] = img[..., 2::-1] # rbga to rgba conversion

    #img = cv2.resize(img, None, fx=scale, fy=scale, interpolation = cv2.INTER_NEAREST)
    slices = np.split(img, num_slices)
    if 'reverse' not in attrs or not attrs['reverse']:
        slices = slices[::-1] # todo handle reverse efficiently
    all_slices = {}
    for angle in range(num_angles):
        all_slices[angle*viewing_angle] = []
    for angle in range(num_angles-1, -1, -1):
        draw_onto = None
        for slice_num in range(len(slices)):
            rotated_image, width, height = rotate_image(slices[slice_num], 90 +  angle * viewing_angle) # todo is this 90 constant correct
            if draw_onto is None:
                draw_onto = rotated_image.copy()
                draw_onto.resize(height + attrs['num_layers'] # * attrs['scale'] # we removed scale
                , width, 4) # resize image to make room for stack
            else:
                x_offset = 0
                y_offset = slice_num
                overlay_transparent(draw_onto, rotated_image, x_offset, y_offset)
            all_slices[angle * viewing_angle].append(rotated_image)
        cacheout.append(draw_onto)
        #cv2.imwrite("cache/%d-%s" % (angle, attrs['path'].split("/")[-1]), draw_onto) # debug loop (write out)
    pickle.dump(cacheout, open("cache/%s" % (attrs['path'].split("/")[-1]), 'wb'))
    print("done rotatating at", time.time() - starttime)
    return all_slices

if False:
    # dead code for reference / image show
    # rotate the image by 180 degree clockwise
    img_cw_180 = cv2.rotate(img, cv2.ROTATE_180)

    # display the rotated image
    cv2.imshow("Image rotated by 180 degree", img_cw_180)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
