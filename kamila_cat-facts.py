import requests
import random

def main():
	random.seed()
	numberOfBreeds = 100
	startOfRand = 1

	url = "https://catfact.ninja/breeds?limit=" + str(numberOfBreeds)
	response = requests.get(url)
	if response.status_code == 200:
		data = response.json()
		mainCat = random.randint(startOfRand, numberOfBreeds - 1)
		dummyCat1 = -1
		dummyCat2 = -1
		dummyCat3 = -1

		while True:
			if dummyCat1 == -1:
				dummyCat1 = random.randint(startOfRand, numberOfBreeds - 1)
				if data["data"][dummyCat1]["country"] != " " and data["data"][mainCat]["breed"] == data["data"][dummyCat1]["breed"]:
					dummyCat1 = -1
			elif dummyCat2 == -1:
				dummyCat2 = random.randint(startOfRand, numberOfBreeds - 1)
				if data["data"][dummyCat2]["country"] != " " and data["data"][mainCat]["breed"] == data["data"][dummyCat2]["breed"] or dummyCat1 == dummyCat2:
					dummyCat2 = -1
			elif dummyCat3 == -1:
				dummyCat3 = random.randint(startOfRand, numberOfBreeds - 1)
				if data["data"][dummyCat3]["country"] != " " and data["data"][mainCat]["breed"] == data["data"][dummyCat3]["breed"] or dummyCat1 == dummyCat3 or dummyCat2 == dummyCat3:
					dummyCat3 = -1
			else:
				break

		print ("What country does the following cat breed come from: " + data["data"][mainCat]["breed"])
		randStart = random.randint(0, 3)
		correctAnswer = -1

		for i in range(4):
			if randStart == 0:
				correctAnswer = i + 1
				print(str(i + 1) + ". " + data["data"][mainCat]["country"])
			elif randStart == 1:
				print(str(i + 1) + ". " + data["data"][dummyCat1]["country"])
			elif randStart == 2:
				print(str(i + 1) + ". " + data["data"][dummyCat2]["country"])
			elif randStart == 3:
				print(str(i + 1) + ". " + data["data"][dummyCat3]["country"])
			randStart += 1
			if randStart > 3:
				randStart = 0

		answer = input("Enter the number of your answer: ")
		if answer == str(correctAnswer):
			print("Correct!")
		else:
			print("Incorrect! The correct answer was " + str(correctAnswer) + ".")
	else:
		print("Failed to retrieve cat breeds")

if __name__ == "__main__":
	main()