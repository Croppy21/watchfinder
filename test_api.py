import requests
from config import TMDB_READ_ACCESS_TOKEN

BASE_URL = "https://api.themoviedb.org/3"


def search_movie(query):
    url = f"{BASE_URL}/search/movie"

    headers = {
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
        "accept": "application/json"
    }

    params = {
        "query": query
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"

    headers = {
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    return response.json()


def print_providers(provider_data):
    au = provider_data.get("results", {}).get("AU")

    print("\n📺 Streaming in Australia")

    if not au:
        print("No streaming information available.")
        return

    labels = {
        "flatrate": "Subscription",
        "rent": "Rent",
        "buy": "Buy"
    }

    for category in ["flatrate", "rent", "buy"]:
        if category in au:
            print(f"\n{labels[category]}:")

            for provider in au[category]:
                print(f" • {provider['provider_name']}")


def main():
    query = input("Enter movie name: ")

    data = search_movie(query)

    results = data.get("results", [])

    if not results:
        print("No results found.")
        return

    # Pick the best match
    movie = results[0]

    title = movie.get("title")
    year = movie.get("release_date", "")[:4]
    rating = movie.get("vote_average")
    overview = movie.get("overview")

    print("\n🎬 BEST MATCH FOUND\n")
    print(f"Title: {title}")
    print(f"Year: {year}")
    print(f"Rating: {rating}")
    print(f"\nOverview:\n{overview}")

    # Get streaming providers
    providers = get_watch_providers(movie["id"])

    # Display them
    print_providers(providers)


if __name__ == "__main__":
    main()