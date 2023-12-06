import sys
from io import BytesIO
from PIL import Image
import requests
import re
#https://api.themoviedb.org/3/movie/87502?api_key=328653fefa8f0be59141eda744355727 (id: flight)
#https://api.themoviedb.org/3/tv/1402?api_key=328653fefa8f0be59141eda744355727 (id: the walking dead)
# this query gives genres by name and also run time. no need to get genre lists and find genre!
#get flag i.e (movie/tv), in result["genres"], find result[name].
#plus write method to get "run time" for movie and "episode run time" for tv shows.


"""
Global variable holding title_details i.e title query from search() method returns title id
further details about the title can be searched using the returned title id
Only used and updated by: get_geners() and compute_runtime() methods
"""
title_details = None


def main():
    sys.exit("#A python moduel written specifically for movie_app.py to handle search function of the application.#")


def get_poster_image(poster_path):
    if poster_path == None:
        image = Image.open("resources/noImage.jpg")
        image = image.resize((200, 320))
        return image

    url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    url += "?api_key=328653fefa8f0be59141eda744355727"

    try:
        response = requests.get(url,timeout=50)
    except:
        image = Image.open("resources/noImage.jpg")
        image = image.resize((200, 320))
        return image

    if response.status_code == 200:
        try:
            image = Image.open(BytesIO(response.content))
            image = image.resize((200,320))
            return image
        except:
            image = Image.open("resources/noImage.jpg")
            image = image.resize((200, 320))
            return image
    else:
        image = Image.open("resources/noImage.jpg")
        image = image.resize((200, 320))
        return image



def get_genres(flag, title_id):
    global title_details
    
    if title_id == None:
        return "No title_id is provided!"
    
    url = ""

    if flag == "movies":
        url = f"https://api.themoviedb.org/3/movie/{title_id}"
        url += "?api_key=328653fefa8f0be59141eda744355727"
    elif flag == "tv":
       url = f"https://api.themoviedb.org/3/tv/{title_id}"
       url += "?api_key=328653fefa8f0be59141eda744355727"
    else:
        sys.exit(":( Invalid flag for get_genres!")

    try:
        response = requests.get(url,timeout=50)
    except:
        return ":( Unable to fetch geners!, Connection timed out."

    genres = []
    if response.status_code == 200:
        response = response.json()
        title_details = response   
        for genre in response["genres"]:
              genres.append(genre["name"])  

        return genres
    else:
        return ":( Unable to fetch poviders link!, invalid response code received."
    

def compute_runtime(flag):
    global title_details
    
    if title_details == None:
        return ":( Unable to get runtime!"

    if flag == "movies": 
        runtime = title_details["runtime"]   
        title_details = None
        hours = int(runtime) // 60
        if (runtime - (hours * 60)) != 0:
            minutes = runtime - (hours * 60)
            if hours > 0:
                return f"{hours}hr {minutes}mins"
            else:
                return f"{minutes}mins"
        else:
            if hours > 0:
                return f"{hours}hr"
            else:
                return "Unknown"
    else:
        runtime = title_details["episode_run_time"]
        title_details = None
        runtime = str(runtime).lstrip("[").rstrip("]")
        if runtime == "":
            return ":( Episodes runtime not found!"
        else:
         return f"{runtime} mins"


def get_credits(flag, title_id):
    if title_id == None:
        return ":( No title_id is provided!"

    url = ""
    if flag == "movies":
        url = f"https://api.themoviedb.org/3/movie/{title_id}/credits"
        url += "?api_key=328653fefa8f0be59141eda744355727"
    elif flag == "tv":
        url = f"https://api.themoviedb.org/3/tv/{title_id}/credits"
        url += "?api_key=328653fefa8f0be59141eda744355727"
    else:
        sys.exit("Invalid flag for get_credits")

    try:
        response = requests.get(url,timeout=50)
    except:
        return ":( Unable to fetch credits!, Connection timed out."

    if response.status_code == 200:
        response = response.json()
        casts = []
        number_of_actors = 0
        for cast in response["cast"]:
            casts.append(cast["name"])
            number_of_actors += 1
            if number_of_actors == 4:
                break
        
        return casts
    else:
        return ":( Unable to fetch credits!, invalid response code received."



def get_watch_providers(flag, title_id):
    if title_id == None:
        return "No title_id is provided!"

    url = ""
    if flag == "movies":
        url = f"https://api.themoviedb.org/3/movie/{title_id}/watch/providers"
        url += "?api_key=328653fefa8f0be59141eda744355727"
    elif flag == "tv":
        url = f"https://api.themoviedb.org/3/tv/{title_id}/watch/providers"
        url += "?api_key=328653fefa8f0be59141eda744355727"
    else:
        sys.exit(":( Invalid flag for get_watch_providers!")

    try:
        response = requests.get(url,timeout=50)
    except:
        return ":( Unable to fetch poviders link!, Connection timed out."
    
    watch_link = ""
    if response.status_code == 200:
        response = response.json()
        results_dict = response["results"]
        
        for result in results_dict:
            new_dict = results_dict[f"{result}"]
            watch_link = new_dict["link"]
        
        if watch_link != "":
            match = re.search("(https://.+/watch)", watch_link)
            watch_link = match.group()
            return watch_link
        else:
            return "No watch providers found!"  
    else:
        return ":( Unable to fetch poviders link!, invalid response code received."


def search(flag, query):

    query = query.strip()
    query = query.replace(" ", "%20")
    url = ""

    if flag == "movies":
        url = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=false&language=en-US&page=1"
        url += "&api_key=328653fefa8f0be59141eda744355727"
    else:
        url = f"https://api.themoviedb.org/3/search/tv?query={query}&include_adult=false&language=en-US&page=1"
        url += "&api_key=328653fefa8f0be59141eda744355727"
   
   
    try:
        response = requests.get(url,timeout=50)
    except:
        atrributes = {"value":"connection_timedout"}
        yield atrributes
        return
    
    if response.status_code == 200:
        response = response.json()
        movie_attributes = {}
    
        if len(response["results"]) == 0:
            movie_attributes["value"] = "empty"
            yield movie_attributes
            return
        
        for result in response["results"]:

            movie_attributes["value"] = "found"
            
            if flag == "movies":
                movie_attributes["title"] = result["title"]
                movie_attributes["release_date"] = result["release_date"]
            else:
                movie_attributes["title"] = result["name"]
                movie_attributes["release_date"] = result["first_air_date"]
            
            movie_attributes["popularity"] = result["popularity"]
            movie_attributes["overview"] = result["overview"]
            movie_attributes["poster_image"] = get_poster_image(result["poster_path"])
            movie_attributes["providers"] = get_watch_providers(flag, result["id"])
            movie_attributes["genres"] = get_genres(flag, result["id"])
            movie_attributes["runtime"] = compute_runtime(flag)
            movie_attributes["casts"] = get_credits(flag, result["id"])
           
            yield movie_attributes
    

if __name__ == "__main__":
    main()