from modules.text_parser import extract_food_items

text_1 = "I had 2 rotis with dal and salad"
text_2 = "One bowl of rice and grilled chicken"
text_3 = "Egg and paneer"

print(extract_food_items(text_1))
print(extract_food_items(text_2))
print(extract_food_items(text_3))
