# ============================================
# DASHBOARD
# ============================================
#
# Main menu with tabs for video games, board games, and bookings.
# Handles game state and navigation.

import ipywidgets as widgets
from IPython.display import clear_output, display

from helpers import load_games, load_rentals
from game_card import create_game_card
from rental import rent_game
from game_return import return_game
from reviews import show_reviews
from bookings import create_bookings_view, book_session
from search import search_ui
from analytics import analytics_ui


def dashboard_redisplay(main_container):
  # Quick redisplay without reload
  clear_output(wait=True)
  display(main_container)


def dashboard_make_grid(games, main_container):
  # Create grid of game cards
  cards = [create_game_card(
    g,
    lambda game: rent_game(
      game,
      dashboard,
      lambda: dashboard_redisplay(main_container)
    ),
    lambda game: return_game(
      game,
      dashboard,
      lambda: dashboard_redisplay(main_container)
    ),
    lambda game: show_reviews(
      game,
      dashboard,
      lambda: dashboard_redisplay(main_container)
    )
  ) for g in games]

  grid = widgets.GridBox(
    cards,
    layout=widgets.Layout(
      grid_template_columns="repeat(3, 0fr)",
      justify_content="center",
      justify_items="center",
      align_items="flex-start",
      grid_gap="5px",
      width="100%"
    )
  )
  return grid


def dashboard_refresh_cards(
  board_games,
  video_games,
  rentals,
  video_box,
  board_box,
  bookings_box,
  search_box,
  main_container
):
  # Reload game data and rebuild cards
  board_games[:] = load_games("Board_Game_Info.txt", "board")
  video_games[:] = load_games("Video_Game_Info.txt", "video")

  rentals.clear()
  rentals.update(load_rentals())

  for game in board_games + video_games:
    if game["GameID"] in rentals:
      game["Available"] = False
      game["RentalInfo"] = rentals[game["GameID"]]

  video_box.children = [dashboard_make_grid(video_games, main_container)]
  board_box.children = [dashboard_make_grid(board_games, main_container)]
  bookings_box.children = [create_bookings_view(
    lambda: book_session(
      dashboard,
      lambda: dashboard_redisplay(main_container)
    ),
    dashboard
  )]
  search_box.children = [search_ui(dashboard)]


def dashboard_update_buttons(
  current_tab,
  video_btn,
  board_btn,
  bookings_btn,
  search_btn,
  content_area,
  video_box,
  board_box,
  bookings_box,
  search_box
):
  # Highlight active tab and show its content
  if current_tab[0] == 0:
    video_btn.button_style = 'success'
    board_btn.button_style = ''
    bookings_btn.button_style = ''
    search_btn.button_style = ''
    content_area.children = video_box.children
  elif current_tab[0] == 1:
    video_btn.button_style = ''
    board_btn.button_style = 'success'
    bookings_btn.button_style = ''
    search_btn.button_style = ''
    content_area.children = board_box.children
  elif current_tab[0] == 2:
    video_btn.button_style = ''
    board_btn.button_style = ''
    bookings_btn.button_style = 'success'
    search_btn.button_style = ''
    content_area.children = bookings_box.children
  else:
    video_btn.button_style = ''
    board_btn.button_style = ''
    bookings_btn.button_style = ''
    search_btn.button_style = 'success'
    content_area.children = search_box.children


def dashboard_on_video_click(
  btn,
  current_tab,
  video_btn,
  board_btn,
  bookings_btn,
  search_btn,
  content_area,
  video_box,
  board_box,
  bookings_box,
  search_box
):
  current_tab[0] = 0
  dashboard_update_buttons(
    current_tab,
    video_btn,
    board_btn,
    bookings_btn,
    search_btn,
    content_area,
    video_box,
    board_box,
    bookings_box,
    search_box
  )


def dashboard_on_board_click(
  btn,
  current_tab,
  video_btn,
  board_btn,
  bookings_btn,
  search_btn,
  content_area,
  video_box,
  board_box,
  bookings_box,
  search_box
):
  current_tab[0] = 1
  dashboard_update_buttons(
    current_tab,
    video_btn,
    board_btn,
    bookings_btn,
    search_btn,
    content_area,
    video_box,
    board_box,
    bookings_box,
    search_box
  )


def dashboard_on_bookings_click(
  btn,
  current_tab,
  video_btn,
  board_btn,
  bookings_btn,
  search_btn,
  content_area,
  video_box,
  board_box,
  bookings_box,
  search_box
):
  current_tab[0] = 2
  dashboard_update_buttons(
    current_tab,
    video_btn,
    board_btn,
    bookings_btn,
    search_btn,
    content_area,
    video_box,
    board_box,
    bookings_box,
    search_box
  )


def dashboard_on_search_click(
  btn,
  current_tab,
  video_btn,
  board_btn,
  bookings_btn,
  search_btn,
  content_area,
  video_box,
  board_box,
  bookings_box,
  search_box
):
  current_tab[0] = 3
  dashboard_update_buttons(
    current_tab,
    video_btn,
    board_btn,
    bookings_btn,
    search_btn,
    content_area,
    video_box,
    board_box,
    bookings_box,
    search_box
  )


def dashboard():
  clear_output(wait=True)
  anchor = widgets.HTML("<div id='top-anchor'></div>")
  display(anchor)

  # Load games from CSV files
  board_games = load_games("Board_Game_Info.txt", "board")
  video_games = load_games("Video_Game_Info.txt", "video")

  # Mark rented games
  rentals = load_rentals()

  for game in board_games + video_games:
    if game["GameID"] in rentals:
      game["Available"] = False
      game["RentalInfo"] = rentals[game["GameID"]]

  # Tab content containers
  video_box = widgets.VBox()
  board_box = widgets.VBox()
  bookings_box = widgets.VBox()
  search_box = widgets.VBox()

  # Tab navigation
  current_tab = [0]  # 0=video, 1=board, 2=bookings, 3=search

  video_btn = widgets.Button(
    description="🎮 Video Games",
    layout=widgets.Layout(width='25%', height='50px'),
    style={'font_weight': 'bold'}
  )
  board_btn = widgets.Button(
    description="🎲 Board Games",
    layout=widgets.Layout(width='25%', height='50px'),
    style={'font_weight': 'bold'}
  )
  bookings_btn = widgets.Button(
    description="📋 Bookings",
    layout=widgets.Layout(width='25%', height='50px'),
    style={'font_weight': 'bold'}
  )
  search_btn = widgets.Button(
    description="🔍 Search",
    layout=widgets.Layout(width='25%', height='50px'),
    style={'font_weight' : 'bold'}
  )

  content_area = widgets.VBox(
    layout=widgets.Layout(
      min_height='600px',
      border='2px solid gray',
      padding='20px'
    )
  )

  button_bar = widgets.HBox(
    [video_btn, board_btn, bookings_btn, search_btn],
    layout=widgets.Layout(width='95%', margin='0 auto')
  )

  tabs_container = widgets.VBox(
    [button_bar, content_area],
    layout=widgets.Layout(width='95%', margin='20px auto')
  )

  # Header with search button
  header = widgets.HTML("<h2 style='color:#0b8517; margin:0'>PIXEL VAULT – HOME</h2>")

  analytics_button = widgets.Button(
    description="📊 Analytics",
    button_style='success',
    layout=widgets.Layout(width='150px', height='40px'),
    style={'font_weight': 'bold'}
  )

  analytics_button.on_click(lambda btn: analytics_ui(dashboard))

  header_frame = widgets.HBox(
    [header, analytics_button],
    layout=widgets.Layout(
      width='95%',
      margin='0 auto 20px auto',
      padding='15px 20px',
      border='2px solid #0b8517',
      justify_content='space-between',
      align_items='center'
    )
  )

  main_container = widgets.VBox(
    [header_frame, tabs_container],
    layout=widgets.Layout(
      width='90%',
      margin='0 auto',
      padding='20px'
    )
  )

  dashboard_refresh_cards(
    board_games,
    video_games,
    rentals,
    video_box,
    board_box,
    bookings_box,
    search_box,
    main_container
  )

  video_btn.on_click(
    lambda btn: dashboard_on_video_click(
      btn,
      current_tab,
      video_btn,
      board_btn,
      bookings_btn,
      search_btn,
      content_area,
      video_box,
      board_box,
      bookings_box,
      search_box
    )
  )
  board_btn.on_click(
    lambda btn: dashboard_on_board_click(
      btn,
      current_tab,
      video_btn,
      board_btn,
      bookings_btn,
      search_btn,
      content_area,
      video_box,
      board_box,
      bookings_box,
      search_box
    )
  )
  bookings_btn.on_click(
    lambda btn: dashboard_on_bookings_click(
      btn,
      current_tab,
      video_btn,
      board_btn,
      bookings_btn,
      search_btn,
      content_area,
      video_box,
      board_box,
      bookings_box,
      search_box
    )
  )
  search_btn.on_click(
    lambda btn: dashboard_on_search_click(
      btn,
      current_tab,
      video_btn,
      board_btn,
      bookings_btn,
      search_btn,
      content_area,
      video_box,
      board_box,
      bookings_box,
      search_box
    )
  )

  dashboard_update_buttons(
    current_tab,
    video_btn,
    board_btn,
    bookings_btn,
    search_btn,
    content_area,
    video_box,
    board_box,
    bookings_box,
    search_box
  )

  display(anchor)
  display(main_container)
