from modules.image_detector import predict_food

image_path = "sample_data/plate1.jpg"  # put your test image here
try:
    result = predict_food(image_path)
    print(result)
except FileNotFoundError as e:
    print(e)
