from PIL import Image  # 导入Pillow库中的Image模块，用于图片处理
import os  # 导入os模块，用于操作文件和目录

def compress_image(infile, outfile, quality=85):
    """
    压缩图片函数
    :param infile: 输入文件名（包含路径）
    :param outfile: 输出文件名（包含路径）
    :param quality: 图片压缩质量
    :return: 如果成功压缩并保存图片，则返回True，否则返回False
    """
    try:
        with Image.open(infile) as im:  # 使用with语句打开输入图片
            # 删除图片的EXIF数据
            data = list(im.getdata())
            cleaned_exif = im.info.get('exif')
            if cleaned_exif:
                del im.info['exif']
            
            # 以JPEG格式保存压缩后的图片，并指定压缩质量和启用优化选项
            im.save(outfile, "JPEG", quality=quality, optimize=True)
            return True
    except:
        return False

def process_directory(directory_path, quality=85, allowed_extensions=['jpg', 'jpeg', 'png']):
    """
    处理目录下的所有图片函数
    :param directory_path: 目录路径
    :param quality: 图片压缩质量
    :param allowed_extensions: 允许的文件扩展名列表
    """
    # 创建一个新的目录用于保存压缩后的图片
    compressed_dir = os.path.join(directory_path, 'compressed')
    os.makedirs(compressed_dir, exist_ok=True)
    
    # 遍历目录下的所有文件，仅处理允许的文件扩展名
    for file_name in os.listdir(directory_path):
        # 获取文件扩展名并转换为小写字母
        extension = os.path.splitext(file_name)[-1].lower()[1:]
        
        if extension in allowed_extensions:
            image_path = os.path.join(directory_path, file_name)  # 构造输入图片的完整路径
            compressed_path = os.path.join(compressed_dir, file_name)  # 构造压缩后图片的完整路径
            compress_image(image_path, compressed_path, quality)  # 调用压缩图片函数进行压缩
            
            # 计算原始图片和压缩后图片的大小并打印
            origin_size = os.path.getsize(image_path)
            compressed_size = os.path.getsize(compressed_path)
            
            print("原始文件 {} 大小为：{}KB".format(file_name, round(origin_size/1024, 2)))
            print("压缩后文件 {} 大小为：{}KB".format(file_name, round(compressed_size/1024, 2)))
        
if __name__ == '__main__':
    process_directory("./images", quality=85, allowed_extensions=['jpg', 'jpeg', 'png'])  # 在主程序中调用process_directory函数对目录下所有图片进行压缩
