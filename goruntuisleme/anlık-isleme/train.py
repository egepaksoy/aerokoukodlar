import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os

# Veri seti yolu
DATASET_PATH = "captured_images"

# Eğitim parametreleri
IMG_SIZE = (224, 224)  # MobileNetV2'nin beklediği giriş boyutu
BATCH_SIZE = 16
EPOCHS = 10
LEARNING_RATE = 0.0001

# Eğitim ve doğrulama verilerinin hazırlanması
datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    validation_split=0.2,  # Verilerin %20'sini doğrulama için ayır
)

train_generator = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="training",
)

val_generator = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="validation",
)

# MobileNetV2 modeli
temp_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))

# Son katmanların eklenmesi
x = temp_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)
predictions = Dense(train_generator.num_classes, activation="softmax")(x)

model = Model(inputs=temp_model.input, outputs=predictions)

# Pretrained katmanları dondurma
for layer in temp_model.layers:
    layer.trainable = False

# Model derleme
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# Model eğitimi
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    validation_steps=val_generator.samples // BATCH_SIZE,
)

# Modelin kaydedilmesi
os.makedirs("models", exist_ok=True)
model.save("./models/mobilenet_trained_model.h5")
print("Model başarıyla kaydedildi!")
