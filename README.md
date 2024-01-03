# Movie Search App

## Video Demo: 

[![Movie app Demo](https://i.ytimg.com/vi/oioRrSSrhww/maxresdefault.jpg)](https://youtu.be/oioRrSSrhww)


## Overview

The Movie Search App is a Python-based application that serves as an interactive platform for users to explore and gather detailed information about movies and TV shows. This README provides insights into the structure, functionalities, and design choices made within the project.

## Files and Functionality

### `movie_app.py`

This module is the heart of the application, housing the Graphical User Interface (GUI) and orchestrating user interactions. The main functionalities include:

- **Search Interface:** Users can input a movie or TV show title for search, initiating a dynamic process to fetch details.
- **Filter Options:** The application allows users to specify their search by choosing between movies and TV shows.
- **Search Limit:** Users can choose between displaying only the top 3 search results or opting for a comprehensive full search.
- **Asynchronous Search:** To ensure a smooth user experience, asynchronous searches are implemented using threading, preventing the GUI from freezing during lengthy searches.
- **Dynamic UI Updates:** The GUI dynamically updates to display search results, presenting posters and relevant information in an aesthetically pleasing manner.
- **Abort Search:** In case a user wishes to interrupt an ongoing search, the application provides an option to abort.

### `project.py`

This support module encapsulates crucial functionalities utilized by `movie_app.py`:

- **Image Handling:** The `get_poster_image` function fetches poster images for movies and TV shows, ensuring a visually appealing representation.
- **Genres Retrieval:** The `get_genres` function retrieves genres based on the title ID and type (movie or TV show), enhancing the categorization of content.
- **Runtime Calculation:** The `compute_runtime` function calculates runtime based on the type of content (movie or TV show), providing users with an estimate of the time commitment.
- **Credits Retrieval:** The `get_credits` function gathers information about the cast, adding depth to the user's understanding of the content.
- **Watch Providers Retrieval:** The `get_watch_providers` function fetches links to watch providers for movies and TV shows, facilitating easy access to streaming options.
- **Search Function:** The `search` function serves as the engine behind the search process, yielding details about each found title.

## Design Choices

- **Threading:** The application's use of threading ensures a responsive user interface. This design choice prevents freezes during searches, contributing to a more seamless user experience.
- **Error Handling:** Robust error handling mechanisms have been implemented for network requests and image processing. This enhances the user experience by gracefully handling failures and communicating issues effectively.
- **Dynamic UI:** The GUI is meticulously designed to dynamically update in real-time as search results are retrieved. This feature not only provides users with prompt feedback but also enhances the overall intuitiveness of the application.

## How to Run

1. Ensure you have Python installed.
2. Install required dependencies using `pip install -r requirements.txt`.
3. Run the application using `python movie_app.py`.


## License

This project is licensed under the MIT License.
