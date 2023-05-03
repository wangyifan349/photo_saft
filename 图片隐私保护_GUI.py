#!/usr/bin/python3
#pip install piexif
#pip install pyexif
#pip install pillow
import os,random,time,piexif,threading
from PIL import Image
from tkinter import Tk, filedialog, Label, Button, StringVar, Entry, Frame
from tkinter import messagebox
from datetime import datetime, timedelta
print("本程序可以擦除照片有关相机参数、GPS、曝光、白平均等信息，保护用户隐私。")
print("同时写入一定的GPS、苹果手机信息以混淆")
def forge_exif_data(image_path):
    try:
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
##########################################################
            # 原始的 GPS 数据
            # 新的 GPS 数据（山东省青岛胶州青岛工学院）
            #latitude = ((36, 1), (16, 1), (1618, 100))
            #longitude = ((120, 1), (0, 1), (5965, 100))
            # 新的 GPS 数据（山东烟台大学）,随便选择一个。
            latitude = ((37, 1), (25, 1), (15, 1))
            longitude = ((121, 1), (26, 1), (55, 1))
            # 生成随机偏移量
            latitude_offset = random.uniform(-0.0001, 0.0001)
            longitude_offset = random.uniform(-0.0001, 0.0001)

            # 应用偏移量到原始经纬度
            lat_seconds = int(latitude[2][0] * 100 + latitude[2][1])
            lon_seconds = int(longitude[2][0] * 100 + longitude[2][1])
            lat_seconds_new = lat_seconds + int(latitude_offset * 10000)
            lon_seconds_new = lon_seconds + int(longitude_offset * 10000)
            latitude_new = ((latitude[0][0], latitude[0][1]), (latitude[1][0], latitude[1][1]), (lat_seconds_new // 100, lat_seconds_new % 100))
            longitude_new = ((longitude[0][0], longitude[0][1]), (longitude[1][0], longitude[1][1]), (lon_seconds_new // 100, lon_seconds_new % 100))

#这里面是伪造GPS信息的。
###################################
            altitude = random.randint(5, 100)  # 随机生成高度，单位为米

            # 随机生成高度，单位为米
            # 随机生成时间，向前回退 1-50 天，时分秒随机生成
            days = random.randint(1, 50)
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            seconds = random.randint(0, 59)
            delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
            timestamp = datetime.now() - delta
            print(timestamp)#它的构造函数可以接受四个可选参数：days、hours、minutes 和 seconds，用于表示时间间隔的天、小时、分钟和秒数。
            # 将时间转换为字符串格式
            date_string = timestamp.strftime("%Y:%m:%d %H:%M:%S")

# 创建 GPS 信息字典
            gps_ifd = {
                piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),  # GPS 版本信息
                piexif.GPSIFD.GPSLatitudeRef: "N",  # 纬度参考（N表示北纬，S表示南纬）
                piexif.GPSIFD.GPSLongitudeRef: "E",  # 经度参考（E表示东经，W表示西经）
                piexif.GPSIFD.GPSLatitude: latitude_new,
                piexif.GPSIFD.GPSLongitude: longitude_new,
                piexif.GPSIFD.GPSDateStamp: date_string,  # GPS 日期时间戳
                piexif.GPSIFD.GPSAltitudeRef: 1,  # GPS 海拔高度参考（1 表示海平面以上）
                piexif.GPSIFD.GPSAltitude: (altitude, 1)  # GPS 海拔高度
            }
            ZeroTH={
        piexif.ImageIFD.Make: "Apple",  # 相机制造商
        piexif.ImageIFD.Model: "iPhone 13 Pro Max",  # 相机型号
        piexif.ImageIFD.Software: "iOS 15",  # 软件版本
        piexif.ImageIFD.Orientation: 1,  # 图像方向（1表示正常方向）
        piexif.ImageIFD.Software: "IOS 15",#用于记录图像处理软件的名称和版本信息，如果图像是由 Apple 设备生成的，则通常会将此字段设置为 "iOS xxx" 或 "macOS xxx"，其中 "xxx" 是操作系统的版本号。例如，如果图像是由运行 iOS 15 的 iPhone 13 Pro Max 拍摄的，则 piexif.ImageIFD.Software 可以设置为 "iOS 15"。
        
        }
            exif_info= {
        piexif.ExifIFD.ExposureTime: (1, 50),  # 曝光时间 1/50s
        piexif.ExifIFD.FNumber: (28, 10),  # F值 f/2.8
        piexif.ExifIFD.ISOSpeedRatings: 100,  # ISO速度
        piexif.ExifIFD.ExposureBiasValue: (0, 3),  # 曝光补偿 0 EV
        piexif.ExifIFD.MaxApertureValue: (28, 10),  # 最大光圈 f/2.8
        piexif.ExifIFD.FNumber: (15, 10), # 光圈值ƒ/1.5 （分数表示）
        #
        #长焦：ƒ/2.8 光圈
        #广角：ƒ/1.5 光圈
        #超广角：ƒ/1.8 光圈和 120° 视角
        #
        piexif.ExifIFD.ExifVersion: b"0231",  # Exif版本 2.31
        piexif.ExifIFD.DigitalZoomRatio: (1, 1),  # 数字缩放 1x
        piexif.ExifIFD.WhiteBalance: 1,  # 自动白平衡
        piexif.ExifIFD.BodySerialNumber: "cafw36caerMsasl5n9431",  # 相机序列号
        piexif.ExifIFD.Flash: 16,  # 闪光灯未触发
        piexif.ExifIFD.FocalLength: (28, 1),  # 焦距 28mm
        piexif.ExifIFD.LensMake: "Foxconn Technology Group",  # 镜头制造商
        piexif.ExifIFD.LensModel: "iPhone 13 Pro Max lens",  # 镜头型号，改一下
        piexif.ExifIFD.Contrast: 0,  # 对比度设置（0表示正常）
        piexif.ExifIFD.Saturation: 0,  # 饱和度设置（0表示正常）
        piexif.ExifIFD.Sharpness: 0,  # 锐度设置（0表示正常）
        piexif.ExifIFD.ExposureProgram: 2,  # 曝光程序（2表示正常程序）
        piexif.ExifIFD.ExposureMode: 0,  # 曝光模式（0表示自动曝光，1表示手动曝光）
        piexif.ExifIFD.SceneCaptureType: 0,  # 场景拍摄类型（0表示标准，1表示风景，2表示人像，3表示夜景等）
        }
            fake_exif_data = {
                "0th":ZeroTH,
                "Exif":exif_info ,
                "GPS": gps_ifd
                }
            # 将伪造的Exif数据写入图片
            print("开始写入伪造数据")
            exif_bytes = piexif.dump(fake_exif_data)
            print(f"已成功向 {image_path} 写入伪造的 Exif 数据。")
            img.save(image_path, "jpeg", exif=exif_bytes)
            #piexif.insert(exif_bytes, image_path)
    except Exception as e:
        print(f"处理 {image_path} 时出现了错误: {str(e)}")
def is_directory_exist(path):
    if os.path.isdir(path):
        return True
    else:
        return False
# 此函数允许用户从本机中浏览和选择一个目录
def browse_directory():
    # 在此函数中使用全局变量'image_directory'
    global image_directory 
    # 打开一个对话框，让用户选择一个目录，并将其路径存储在'image_directory'中
    image_directory = filedialog.askdirectory()
    # 更新标签(widget)的文本为所选目录的路径
    directory_label.config(text=image_directory)
    # 删除条目(widget)中当前存在的任何文本
    directory_entry.delete(0, 'end')
    # 将所选目录的路径插入到条目(widget)中
    directory_entry.insert(0, image_directory)

def process_images_recursively(directory):
    for root, _, files in os.walk(directory):
        for filename in files:
            if os.path.splitext(filename)[1].lower() in ('.webp', '.jpg', '.jpeg', '.bmp', '.gif', '.png', '.PNG', '.WEBP', '.JPG', '.JPEG', '.BMP', '.GIF'):
                image_path = os.path.join(root, filename)
                print(f"正在处理 {image_path}...")
                forge_exif_data(image_path)
def process_images_thread():
    # 使用线程处理图像，以防止GUI阻塞
    process_thread = threading.Thread(target=process_images)
    process_thread.start()
    
def process_images():
    if is_directory_exist(image_directory):
        process_images_recursively(image_directory)
        status_label.config(text="处理完成")
        messagebox.showinfo("感谢使用", "已经清除了图片中的隐私信息，同时写入了一定的伪造信息")
    else:
        status_label.config(text="路径无法识别，有任何问题，请联系开发者。")
# 创建GUI窗口
root = Tk()
root.title("Exif数据伪造工具")
root.geometry("400x200")
# 获取当前用户的用户名
user_name = os.getlogin()
# 获取图片目录的路径
image_directory = os.path.join("C:\\", "Users", user_name, "Pictures")
print(image_directory)
#image_directory = ""  # 在这里添加初始值

# 添加目录选择和显示组件
directory_label = Label(root, text="请选择图片文件夹：", wraplength=350)
directory_label.pack(pady=10)

browse_button = Button(root, text="浏览", command=browse_directory)
browse_button.pack()

directory_entry = Entry(root, width=50)
directory_entry.pack(pady=5)

# 添加开始处理按钮
process_button = Button(root, text="开始处理", command=process_images_thread)
process_button.pack(pady=10)

# 添加状态标签
status_label = Label(root, text="")
status_label.pack(pady=5)

# 运行GUI主循环
root.mainloop()
