import os
import piexif
from PIL import Image

def forge_exif_data(image_path):
    try:
        os.chmod(image_path, 0o777) # 更改文件权限
        with Image.open(image_path) as img:
            # 删除img.info中的所有元数据
            keys_to_remove = list(img.info.keys())
            for key in keys_to_remove:
                del img.info[key]#删除元数据字典中的值
            # 这是伪造的元数据，请自己找这方面的参数，这是个苹果13的，可以换成别的手机.
            fake_exif_data = {
                "Make": "Apple",
                "Model": "iPhone 13 Pro Max",
                "Software": "iOS 15",
                "ExposureTime": (1,50), # 1/50s
                "FNumber": (28,10), # f/2.8
                "ISOSpeedRatings": 100,
                "Latitude": ((31, 1), (13, 1), (49, 100)), # 上海的纬度
                "Longitude": ((121, 1), (28, 1), (25, 100)), # 上海的经度
            }
            # 将伪造的Exif数据写入图片
            exif_bytes = piexif.dump(fake_exif_data)
            piexif.insert(exif_bytes, image_path)
    except Exception as e:
        print(f"处理 {image_path} 时出现了错误: {str(e)}")
# 示例：批量修改目录下的所有JPEG文件
image_directory = "images"
for filename in os.listdir(image_directory):
    if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
        image_path = os.path.join(image_directory, filename)
        # 删除元数据并伪造Exif数据，然后覆盖原文件
        forge_exif_data(image_path)
