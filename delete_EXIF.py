#已经删除了Pillow库中img.info字典的元数据并伪造了Exif数据。
#可以使用exiftool或类似的库来删除其他潜在的隐私信息。这里没有写。
#一定一定要测试一下我这边测试基本都删除了。
#pip install pillow
#pip install piexif
# -*- coding: utf-8 -*-
import os
import piexif
from PIL import Image

def forge_exif_data(image_path):
    try:
        os.chmod(image_path, 0o777) # 更改文件权限
        with Image.open(image_path) as img:
            # 删除img.info中的所有元数据
            if "icc_profile" in img.info:
                del img.info["icc_profile"]# 删除ICC Profile
            if "photoshop_metadata" in img.info:
                del img.info["photoshop_metadata"]# 删除IPTC信息
            if "xmp_metadata" in img.info:
                del img.info["xmp_metadata"]# 删除XMP信息
            keys_to_remove = list(img.info.keys())
            for key in keys_to_remove:
                print(f"正在删除 {key} 元数据...")
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
            print(f"已成功向 {image_path} 写入伪造的 Exif 数据。")
            piexif.insert(exif_bytes, image_path)
    except Exception as e:
        print(f"处理 {image_path} 时出现了错误: {str(e)}")
# 示例：批量修改目录下的所有JPEG文件
image_directory = r"C:\\Users\Administrator\Documents\测试区域\image"#这里填写真实的文件路径，这是我的测试的部分，你换成python3的，格式部分这是尝试了，自己研究不解释了。
for filename in os.listdir(image_directory):
    if filename.lower().endswith(('.jpg', '.jpeg', '.bmp', '.gif', '.png')):#图片格式很多，需要的自己添加进去。
        image_path = os.path.join(image_directory, filename)
        print(f"正在处理 {image_path}...")
        # 删除元数据并伪造Exif数据，然后覆盖原文件
        forge_exif_data(image_path)
