import requests

url = 'http://localhost/transfer'
multiple_files = [
('images', ('apple.jpg', open('./public/images/apple.jpg', 'rb'), 'image/jpg')),
('images', ('bananas.jpg', open('./public/images/bananas.jpg', 'rb'), 'image/jpg'))]
print(multiple_files)
r = requests.post(url, files=multiple_files)
print(r.text)
