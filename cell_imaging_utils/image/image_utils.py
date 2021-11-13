import aicsimageio
import numpy as np
import logging
import typing
import tifffile
from aicsimageio import AICSImage, aics_image
from multipledispatch import dispatch


log = logging.getLogger(__name__)

"""
ImageUtils
------------------
Class that contains some static methods to help handle images
Channel= 'C'
MosaicTile= 'M'
Samples= 'S'
SpatialX= 'X'
SpatialY= 'Y'
SpatialZ= 'Z'
Time= 'T'

Two main functions params are
image - AICSImage ("STCZYX")
image_ndarray - np.ndarray ("CZYX")
"""


class ImageUtils:

    @staticmethod
    def imread(image: typing.Union[np.ndarray, str]) -> AICSImage:
        with AICSImage(image) as img:
            img.size_z
            return img

    @staticmethod
    def imsave(image_ndarray: np.ndarray, path: str):
        tifffile.imsave(path, image_ndarray, image_ndarray.shape)

    @staticmethod
    @dispatch(AICSImage, int)
    def get_channel(image: AICSImage, channel_index: int) -> np.ndarray:
        return image.get_image_data("CZYX")[channel_index:channel_index+1, :, :, :]

    @staticmethod
    @dispatch(np.ndarray, int)
    def get_channel(image_ndarray: np.ndarray, channel_index: int) -> np.ndarray:
        return image_ndarray[channel_index:channel_index+1, :, :, :]

    @staticmethod
    def add_channel(image_ndarray: np.ndarray, channel) -> np.ndarray:
        new_image_ndarray = np.append(image_ndarray, channel, axis=0)
        return new_image_ndarray

    @staticmethod
    def image_to_ndarray(image):
        return image.get_image_data("CZYX")

    @staticmethod
    def get_channel_names(image):
        return image.get_channel_names()

    """
    Normalize all values between 0 to max_value
    """
    @staticmethod
    def normalize(image_ndarray,max_value=255,dtype=np.uint8) -> np.ndarray:
        temp_image = image_ndarray-np.min(image_ndarray)
        return (((temp_image)/np.max(temp_image))*max_value).astype(dtype)
    
    """
    to_shape changes the image shape according to the shape recieved
    """
    @staticmethod
    def to_shape(image_ndarray, shape, rescale_z=None, min_shape=None)  -> np.ndarray:
        c_, z_, y_, x_ = np.maximum(shape,min_shape)
        c, z, y, x = image_ndarray.shape
        y_pad = (y_-y)
        x_pad = (x_-x)
        z_pad = (z_-z)
        c_pad = (c_-c)
        if (rescale_z is not None):
            scaled_a = image_ndarray[:,::rescale_z,:,:]
            z_pad = (z_ - scaled_a.shape[1])
        else:
            scaled_a = image_ndarray
        if (c_pad >= 0):        
            scaled_a = np.pad(scaled_a,((c_pad//2, c_pad//2 + c_pad%2),(0,0),(0,0),(0,0)),mode = 'constant')
        else:
            scaled_a = scaled_a[abs(c_pad//2):scaled_a.shape[0]+(c_pad//2 + c_pad%2),:,:,:]
            
        if (z_pad >= 0):        
            scaled_a = np.pad(scaled_a,((0,0),(z_pad//2, z_pad//2 + z_pad%2),(0,0),(0,0)),mode = 'constant')
        else:
            scaled_a = scaled_a[:,abs(z_pad//2):scaled_a.shape[1]+(z_pad//2 + z_pad%2),:,:]
            
        if (y_pad >= 0):        
            scaled_a = np.pad(scaled_a,((0,0),(0,0),(y_pad//2, y_pad//2 + y_pad%2),(0,0)),mode = 'constant')
        else:
            scaled_a = scaled_a[:,:,abs(y_pad//2):scaled_a.shape[2]+(y_pad//2 + y_pad%2),:]
            
        if (x_pad >= 0):        
            scaled_a = np.pad(scaled_a,((0,0),(0,0),(0,0),(x_pad//2, x_pad//2 + x_pad%2)),mode = 'constant')
        else:
            scaled_a = scaled_a[:,:,:,abs(x_pad//2):scaled_a.shape[3]+(x_pad//2 + x_pad%2)]                        
        return scaled_a
    
    # @staticmethod
    # def clean_by_slice(image_ndarray:np.ndarray, leave_percentage:float)->np.ndarray:
    #     sum_values
    
    """
    mask_image gets image and mask_template it masks the image according to the template and duplicate it accordingly
    """
    @staticmethod
    def mask_image(image_ndarray,mask_template_ndarray) -> np.ndarray:
        mask_ndarray = mask_template_ndarray
        for i in range(int(image_ndarray.shape[0])-1):
            mask_ndarray = ImageUtils.add_channel(mask_ndarray,mask_template_ndarray)
        return np.where(mask_ndarray==1.0,image_ndarray,np.zeros(image_ndarray.shape))
