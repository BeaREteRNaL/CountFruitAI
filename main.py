import os
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# 設定圖片尺寸
target_size = (256, 256)

# 資料集路徑
dataset_dir = 'D:/CountFruitAI/train/apple'

# 圖片預處理函數
def preprocess_image (image_path, target_size):
    img = Image.open(image_path).convert('L')  # 轉換為灰階
    img = ImageOps.pad(img, target_size, color='black')  # 填充短邊
    img = img.resize(target_size, Image.ANTIALIAS)  # 縮放
    return np.array(img)

# 建立自定義ImageDataGenerator
class CustomImageDataGenerator (ImageDataGenerator):
    def _get_batches_of_transformed_samples(self, index_array):
        batch_x = np.zeros((len(index_array), *self.target_size, 1))
        for i, j in enumerate(index_array):
            img = preprocess_image(self.filepaths[j], self.target_size)
            batch_x[i] = np.expand_dims(img, axis=-1)
        return batch_x, self._get_batches_of_transformed_samples_y(index_array)

    # 使用ImageDataGenerator進行數據增強和批處理
    train_datagen = CustomImageDataGenerator (
        rescale=1.0 / 255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        validation_split=0.2  # 分出20%作為驗證集
    )

    train_generator = train_datagen.flow_from_directory(
        dataset_dir,
        target_size=target_size,
        batch_size=32,
        class_mode='binary',
        color_mode='grayscale',
        subset='training'
    )

    validation_generator = train_datagen.flow_from_directory(
        dataset_dir,
        target_size=target_size,
        batch_size=32,
        class_mode='binary',
        color_mode='grayscale',
        subset='validation'
    )

    # 建立CNN模型
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 1)),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(1, activation='sigmoid')  # 二分類輸出層
    ])