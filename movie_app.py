from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import re
import sys
import threading
import webbrowser
import random
from project import search
import cowsay


# ------------------------UI Elements that need there value stored for other functions-------------
"""
Holds users query string
# Only updated by 'set_query_string_function'
"""
query_string = ""

"""
Holds which checked button is checked
# Only updated by 'check_button_function'
"""
checked_button_value = ""

"""
Holds search limit value from combobox
# Only upadted by 'search_limit_function'
"""
search_limit_choice = "Top 3 Search"

"""
Holds progress bar reference to update it later
# Assigned reference in 'create_middle_frame' function after creating progress_bar
# Only updated by 'search_thread' and 'abort_button_function'
"""
progress_bar_reference = None
progress_bar_label_reference = None

"""
Holds reference of scrollable_frame returned from 'create_bottom_frame' assigned in 'main' function
# during creation of root_window so that it is later populated with search results
# Only updated by 'populate_bottom_frame' function
"""
update_frame = None
# -------------------------------------------------------------------------------------------------


# --------------------------------------Thread control-----------------------------
"""
A mechanism to control search thread
# 0 search (search started by the user)
# 1 stop search (search is aborted by user)
# 2 stop search (because app is closed by user) set only by close_appliction() method
"""
thread_exit_flag = 0
# -------------------------------------------------------------------------------------------------


def main():
    global update_frame

    root_window = create_root_window()
    create_top_frame(root_window)
    create_middle_frame(root_window)
    update_frame = create_bottom_frame(root_window)

    root_window.bind("<Return>", search_button_function)
    root_window.protocol("WM_DELETE_WINDOW", lambda: close_application(root_window))
    root_window.mainloop()


def create_root_window():
    """
    Creates root_window, the main window where all the other Frames are added into.
    Set theme to root window
    Adds a logo_label to root_window
    returns root_window
    """

    root = Tk()
    root.configure(padx=5, pady=5)
    root.minsize(800, 600)
    root.title("Search Movies & Tv Shows")

    s = ttk.Style()
    s.theme_use("winnative")
    s.configure(root, font=("Arial", 15,"bold"))

    image = ImageTk.PhotoImage(Image.open("resources/logo.png"))
    logo_label = ttk.Label(root, image=image, padding=15, relief="raised")
    logo_label.image_names = image
    logo_label.pack(side="top", fill="both", pady=5)

    return root


def create_top_frame(root):
    """
    creates top_frame that holds search_entry(search field), search_limit combobox and search_button
    takes the root window as parameter to add top_frame in to it
    returns top_frame
    """
    s = ttk.Style()

    top_frame = ttk.Frame(root, padding="5 10", style="Custom.TFrame")
    top_frame.pack(side="top", fill="both", pady=3)
    top_frame.configure(borderwidth=2, relief="solid")
    top_frame.option_add("*TCombobox*Listbox.font", ("Arial", 13, "bold"))
    top_frame.option_add("*TCombobox*Listbox.selectForeground", "#37BDCB")

    query = StringVar()
    query.set("Enter movie title . . .")
    query.trace(
        "w", lambda name, index, mode, text=query: set_query_string_function(text)
    )

    s.configure("TEntry", bordercolor="#37BDCB")
    search_entry = ttk.Entry(
        top_frame, width=50, textvariable=query, font=("Arial", 13, "bold")
    )
    search_entry.focus()
    search_entry.select_range(0, END)
    search_entry.pack(side="left", fill="both", expand=True, padx=10)

    search_choice = StringVar()
    search_limit = ttk.Combobox(
        top_frame,
        values=("Top 3 Search", "Full search"),
        state="readonly",
        textvariable=search_choice,
        font=("Arial", 13, "bold"),
    )

    search_limit.pack(side="left", fill="both", padx=10)
    search_limit.current(0)
    search_limit.bind(
        "<<ComboboxSelected>>",
        lambda e: search_limit_combobox_function(search_choice.get()),
    )

    s.configure("Custom.TButton", background="#37BDCB")
    search_button = ttk.Button(
        top_frame,
        text="Search",
        width=30,
        padding="10 10",
        command=search_button_function,
        style="Custom.TButton",
    )
    search_button.pack(side="left", fill="both")

    return top_frame


def create_middle_frame(root):
    """
    Creates middle_frame
    middle_frame holds movie and tv checkbuttons (used to either select movie or tv show to search),
    abort_button (aborts on-going search) and progress_bar (displays status of search)
    """
    s = ttk.Style()

    global progress_bar_reference
    global progress_bar_label_reference

    middle_frame = ttk.Frame(root, padding="10 12")
    middle_frame.pack(side="top", fill="both", pady=5)
    middle_frame.configure(borderwidth=2, relief="solid")

    movies_checked = StringVar()
    tv_checked = StringVar()
    movie_check_button = ttk.Checkbutton(middle_frame, style="Custom.TCheckbutton")
    tv_check_button = ttk.Checkbutton(middle_frame, style="Custom.TCheckbutton")

    s.configure(
        "TCheckbutton",
        indicatorcolor="#37BDCB",
        background="#37BDCB",
        foreground="black",
        font=("Arial", 15, "bold"),
    )

    movie_check_button.configure(
        text="Movies",
        variable=movies_checked,
        command=lambda: check_buttons_function(movies_checked, tv_check_button),
        onvalue="movies",
        offvalue="not_movie",
    )
    movie_check_button.pack(side="left", padx=10)

    tv_check_button.configure(
        text="Tv shows",
        variable=tv_checked,
        command=lambda: check_buttons_function(tv_checked, movie_check_button),
        onvalue="tv",
        offvalue="not_tv",
    )
    tv_check_button.pack(side="left")

    movies_checked.set("movies")
    check_buttons_function(
        movies_checked, tv_check_button
    )  # Select "Movies" choice by default.

    s.configure("Custom.TButton", font=("Arial", 15, "bold"), background="#37BDCB")
    abort_button = ttk.Button(
        middle_frame,
        text="Abort Search",
        width=20,
        padding="10 10",
        command=lambda: abort_button_function(),
        style="Custom.TButton",
    )
    abort_button.pack(side="right")

    progress_bar = ttk.Progressbar(
        middle_frame, orient="horizontal", length=100, mode="determinate", maximum=100
    )
    progress_bar.pack(anchor="center", side="left", padx=7)
    progress_bar_reference = progress_bar

    progress_bar_label = ttk.Label(middle_frame, font=("Helvetica", 10))
    progress_bar_label.pack(anchor="center", side="left")
    progress_bar_label_reference = progress_bar_label

    return middle_frame


def create_bottom_frame(root):
    """
    Creates bottom_frame
    Bottom_frame Holds (Canvas,Scrollbar_x and Scrollbar_y)
    Canvas holds ("scrollable_frame")
    returns Scrollable_frame
    """
    bottom_frame = ttk.Frame(root)
    bottom_frame.pack(side="bottom", fill="both", expand=True)
    
    scrollbar_x = ttk.Scrollbar(bottom_frame, orient="horizontal")
    scrollbar_x.pack(side="bottom", fill="x", padx=2)

    scrollbar_y = ttk.Scrollbar(bottom_frame, orient="vertical")
    scrollbar_y.pack(side="right", fill="y", pady=2)

    canvas = Canvas(bottom_frame)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar_y.configure(command=canvas.yview)
    scrollbar_x.configure(command=canvas.xview)

    scrollable_frame = ttk.Frame(canvas, padding=5)
    scrollable_frame.configure(borderwidth=2, relief="solid")
    scrollable_frame.pack(padx=5, pady=10, fill="both", expand=True)
    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.bind(
        "<Configure>", lambda e: canvas.itemconfigure(canvas_window, width=e.width)
    )
    # ------------------------------------------------------------------------------

    return scrollable_frame


def populate_bottom_frame(scrollable_frame, result):
    """
    populates bottom_frames's Scrollable_frame with movie_frames
    Each movie_frame holds poster image(poster_label), movie_description_frame and movie_watch_description_frame
    Movie_description_frame holds movie_title(label), movie_gener(label), movie_overview
    returns populated scrollable_frame
    """
    s = ttk.Style()

    if result["value"] == "empty" or result["value"] == "connection_timedout":
        s.configure("SearchFailed.TLabel", foreground="#CF2A27")
        result_frame = ttk.Frame(scrollable_frame, padding=5)
        result_frame.pack(anchor="center", pady=10)

        result_label = ttk.Label(result_frame, style="SearchFailed.TLabel")
        result_label.pack(fill="both", expand=True)

        cowsay_method = random.choice(
            ["cow", "beavis", "cheese", "dragon", "fox", "ghostbusters", "kitty"]
        )
        if result["value"] == "empty":
            result_label["text"] = cowsay.get_output_string(
                cowsay_method, "Nothing Found!"
            )
            return scrollable_frame
        else:
            result_label["text"] = cowsay.get_output_string(
                cowsay_method, "Connection timed out!"
            )
            return scrollable_frame

    if result["value"] == "found":
        movie_frame = ttk.Frame(scrollable_frame, padding=5)
        movie_frame.configure(borderwidth=1, relief="raised")
        movie_frame.pack(fill="both", padx=5, pady=10)
        s.configure(movie_frame, font=("Helvetica", 10))
        # -----------------------Poster Image----------------------------------------------
        
        poster_image = ImageTk.PhotoImage(result["poster_image"])
        poster_label = ttk.Label(
            movie_frame,
            image=poster_image,
        )
        poster_label.configure(borderwidth=1, relief="raised")
        poster_label.image_names = poster_image
        poster_label.pack(anchor="n", side="left", fill="y")

        # ---------------------Title, Geners, Runtime, Release Date, Popularity and Casts--------------------------------
        movie_watch_description_frame = ttk.Frame(movie_frame, padding=3)
        movie_watch_description_frame.configure(borderwidth=1, relief="raised")
        movie_watch_description_frame.pack(anchor="nw", side="left", padx=5, fill="y")
        movie_watch_description_frame.bind(
            "<Configure>",
            lambda e: movie_watch_description_frame.configure(
                height=poster_label.winfo_screenheight()
            ),
        )

        movie_title = ttk.Label(
            movie_watch_description_frame, text=f'Title: {result["title"]}'
        )
        movie_title.pack(anchor="w", side="top", pady=5)

        if type(result["genres"]) is list:
            genres = "".join(genre + "," for genre in result["genres"]).rstrip(",")
        else:
            genres = result["genres"]

        movie_geners = ttk.Label(
            movie_watch_description_frame, text=f"Genres: {genres}"
        )
        movie_geners.pack(anchor="w", side="top", pady=5)

        movie_runtime = ttk.Label(
            movie_watch_description_frame, text=f'Runtime: {result["runtime"]}'
        )
        movie_runtime.pack(anchor="w", side="top", pady=5)

        movie_release_date = ttk.Label(
            movie_watch_description_frame,
            text=f'Release Date: {result["release_date"]}',
        )
        movie_release_date.pack(anchor="w", side="top", pady=5)

        movie_popularity = ttk.Label(
            movie_watch_description_frame,
            text=f'Popularity: {result["popularity"]}',
        )
        movie_popularity.pack(anchor="w", side="top", pady=5)

        if type(result["casts"]) is list:
            casts = "".join(" " + cast + ",\n" for cast in result["casts"]).rstrip(",")
        else:
            casts = result["casts"]

        movie_casts = ttk.Label(
            movie_watch_description_frame,
            text=f"Casts: \n{casts}",
            justify="left",
        )
        movie_casts.pack(anchor="w", side="top", pady=5)
        movie_casts.bind(
            "<Configure>", lambda e: movie_casts.configure(wraplength=e.width)
        )

        # --------------------Overview and watch providers-------------------------
        movie_description_frame = ttk.Frame(movie_frame, padding=3)
        movie_description_frame.configure(borderwidth=1, relief="raised")
        movie_description_frame.pack(side="left", fill="both", expand=True, padx=5)

        movie_overview = ttk.Label(
            movie_description_frame,
            text=f'Movie Overview: {result["overview"]}',
            justify="left",
        )
        movie_overview.pack(anchor="w", side="top", fill="both")
        movie_overview.bind(
            "<Configure>", lambda e: movie_overview.configure(wraplength=e.width)
        )

        s.configure("Blue.TLabel", foreground="#0078D7")
        movie_stream_providers = ttk.Label(
            movie_description_frame,
            text=f'Watch Providers: {result["providers"]}',
            justify="left",
            style="Blue.TLabel",
        )

        movie_stream_providers.pack(anchor="sw", side="bottom", fill="both", pady=3)

        movie_stream_providers.bind(
            "<Button-1>",
            lambda e: extract_watch_providers_link(movie_stream_providers["text"]),
        )

        movie_stream_providers.bind(
            "<Configure>",
            lambda e: movie_stream_providers.configure(wraplength=e.width),
        )

    return scrollable_frame


def set_query_string_function(query):
    global query_string
    query_string = query.get()


def check_buttons_function(*args):
    global checked_button_value

    if args[0].get() == "movies":
        args[1].state(["!selected"])
        checked_button_value = "movies"
    elif args[0].get() == "tv":
        args[1].state(["!selected"])
        checked_button_value = "tv"
    elif args[0].get() == "not_movie":
        args[1].state(["selected"])
        checked_button_value = "tv"
    else:
        args[1].state(["selected"])
        checked_button_value = "movies"


def search_limit_combobox_function(*args):
    global search_limit_choice
    search_limit_choice = args[0]


def extract_watch_providers_link(link):
    """
    Get text variable from movie_stream_providers ttk label , extract link and open it on webbrowser
    this method is a bind method method called for each movie_stream_providers ttk label up on being clicked
    each movie/tv search result has movie_stream_providers label that displays a link the provides with streaming options
    """
    match = re.search("(https://.+/watch)", link)
    if match != None:
        watch_link = match.group()
        webbrowser.open(watch_link)
    return


def abort_button_function(*args):
    global thread_exit_flag

    # Signal to the thread to exit(if there is a search thread going!).
    if threading.active_count() == 2:
        thread_exit_flag = 1
        progress_bar_status(-1, "stop")

    for widget in update_frame.winfo_children():
        widget.destroy()

    return


def progress_bar_status(update, flag):
    s = ttk.Style()
    s.configure("SearchCompleted.TLabel", foreground="#0078D7")

    if flag == "start":
        progress_bar_reference.start(interval=2100000)  # 35 minutes interval
        progress_bar_reference["value"] = 0
        progress_bar_label_reference.configure(style="")
        progress_bar_label_reference[
            "text"
        ] = f'Progress: {progress_bar_reference["value"]}%'
        return
    elif flag == "stop":
        # Stop any ongoing progress_bar function
        if update == 0 and flag == "stop":
            progress_bar_reference.stop()
            return

        # flage = 1 sent to thread to stop, waiting for thread to exit.
        if update == -1 and flag == "stop":
            progress_bar_reference.stop()
            progress_bar_label_reference["text"] = "Aborting...please wait!"
            return

        # Search aborted(thread found flag and exited)!!
        if update == -2 and flag == "stop":
            progress_bar_label_reference["text"] = "Aborted!"
            return

        # update bar to 100 and stop.
        if update == 100 and flag == "stop":
            progress_bar_reference["value"] = 100
            progress_bar_label_reference.configure(style="SearchCompleted.TLabel")
            progress_bar_label_reference["text"] = f"Search Completed!"
    else:
        progress_bar_reference["value"] += update
        progress_bar_label_reference[
            "text"
        ] = f'Progress: {progress_bar_reference["value"]}%'
        return


def search_button_function(*args):
    
    # Remove previous results from upadate_frame
    for widget in update_frame.winfo_children():
        widget.destroy()

    # Only a single thread additional to the main thread at a time.
    if threading.active_count() == 1:
        thread = threading.Thread(target=lambda: search_thread())
        thread.start()
        return


def search_thread():
    global thread_exit_flag

    progress_bar_status(0, "stop")
    progress_bar_status(0, "start")

    if search_limit_choice == "Top 3 Search":
        count = 0
        for result in search(checked_button_value, query_string):
            if thread_exit_flag == 0:  # search started
                if result["value"] == "found":
                    progress_bar_status(34, None)
                    populate_bottom_frame(update_frame, result)
                else:
                    progress_bar_status(100, "stop")
                    populate_bottom_frame(update_frame, result)
                    sys.exit()
                count += 1
                if count == 3:
                    progress_bar_status(
                        100, "stop"
                    )  # update progressbar value with 100
                    sys.exit()
            elif (
                thread_exit_flag == 1
            ):  # normal exit search is aborted by user.[search aborted]
                progress_bar_status(-2, "stop")  # set progress to Abotred status
                thread_exit_flag = 0  # reset exit_flag to zero
                sys.exit()
            else:  # special exit, App is closed by the user.
                sys.exit()

    if search_limit_choice == "Full search":
        for result in search(checked_button_value, query_string):
            if thread_exit_flag == 0:
                if result["value"] == "found":
                    progress_bar_status(5, None)
                    populate_bottom_frame(update_frame, result)
                else:
                    progress_bar_status(100, "stop")
                    populate_bottom_frame(update_frame, result)
                    sys.exit()
            elif thread_exit_flag == 1:
                progress_bar_status(-2, "stop")
                thread_exit_flag = 0
                sys.exit()
            else:
                sys.exit()

    progress_bar_status(100, "stop")
    sys.exit()


def close_application(root_window):
    global thread_exit_flag
    thread_exit_flag = 2  # Tells search thread to exit cause App is closed.
    root_window.destroy()


if __name__ == "__main__":
    main()
