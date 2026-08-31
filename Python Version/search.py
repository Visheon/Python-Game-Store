# ============================================
# SEARCH
# ============================================
#
# Real-time search across all games by title, genre, or platform (for
# video games).

import ipywidgets as widgets

from helpers import load_games, load_rentals
from game_card import create_game_card
from rental import rent_game
from game_return import return_game
from reviews import show_reviews


def search_filter_games(search_term, all_games):
  # Return all games if search is empty
  if not search_term.strip():
    return all_games

  search_term = search_term.lower()
  filtered = []

  for game in all_games:
    # Match title
    if search_term in game['Name'].lower():
      filtered.append(game)
      continue

    # Match genre
    if search_term in game['Genre'].lower():
      filtered.append(game)
      continue

    # Match platform (video games only, stored in NoPlayers field)
    if game['Type'] == 'video' and 'NoPlayers' in game:
      if search_term in game['NoPlayers'].lower():
        filtered.append(game)

  return filtered


def search_update_results(change, search_input, results_container, all_games, main_menu_callback):
  # Called whenever search input changes
  search_term = search_input.value
  filtered_games = search_filter_games(search_term, all_games)

  if not filtered_games:
    results_container.children = [
      widgets.Label(
        value=f"No games found for '{search_term}'",
        layout=widgets.Layout(margin='50px auto')
      )
    ]
  else:
    # Create game cards with callbacks
    cards = [create_game_card(
      g,
      lambda game: rent_game(game, lambda: search_ui(main_menu_callback), lambda: search_ui(main_menu_callback)),
      lambda game: return_game(game, lambda: search_ui(main_menu_callback), lambda: search_ui(main_menu_callback)),
      lambda game: show_reviews(game, lambda: search_ui(main_menu_callback), lambda: search_ui(main_menu_callback))
    ) for g in filtered_games]

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
    results_container.children = [grid]


def search_ui(main_menu_callback):

  # Load all games (board + video)
  board_games = load_games("Board_Game_Info.txt", "board")
  video_games = load_games("Video_Game_Info.txt", "video")
  all_games = board_games + video_games

  # Mark rented games and attach rental info
  rentals = load_rentals()

  for game in all_games:
    if game["GameID"] in rentals:
      game["Available"] = False
      game["RentalInfo"] = rentals[game["GameID"]]

  # Search input
  search_input = widgets.Text(
    placeholder='Search by title, genre, or platform (e.g., Xbox, PlayStation, Nintendo)...',
    layout=widgets.Layout(width='90%', height='50px'),
    style={'description_width': 'initial'}
  )

  # Container for results
  results_container = widgets.VBox(
    layout=widgets.Layout(
      min_height='600px',
      border='2px solid gray',
      padding='20px'
    )
  )

  # Real-time search as user types
  search_input.observe(lambda change: search_update_results(change, search_input, results_container, all_games, main_menu_callback), names='value')

  # Show all games initially
  search_update_results(None, search_input, results_container, all_games, main_menu_callback)

  return widgets.VBox([search_input, results_container])
