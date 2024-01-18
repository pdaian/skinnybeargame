# import required libraries
import cv2, time
import numpy as np
starttime = time.time()

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
    return rotated_mat


def get_all_slices(path, num_slices, num_angles, viewing_angle):
    starttime = time.time()
    print("rotating", path)
    # load the input image
    img = cv2.imread(path)
    slices = np.split(img, num_slices)
    all_slices = {}
    for angle in range(num_angles):
        all_slices[angle*viewing_angle] = []
    for angle in range(num_angles ):
        for slice_num in range(len(slices)):
            rotated_image = rotate_image(slices[slice_num], angle * viewing_angle)
            all_slices[angle * viewing_angle].append(rotated_image)
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
