import requests
print(requests.get("https://www.automobile.tn/fr/occasions").text[:1000])
