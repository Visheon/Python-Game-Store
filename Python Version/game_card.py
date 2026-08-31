# ============================================
# GAME CARD DISPLAY
# ============================================
#
# Creates the visual card for each game with image, info, rating, and
# action buttons.

import ipywidgets as widgets

from helpers import get_cached_image, get_image_format, create_star_display


def create_game_card(game, rent_callback, return_callback, reviews_callback):

  image = get_cached_image(game["Image"])
  img_format = get_image_format(game, image)

  # Load game image or show a placeholder if there is no image
  try:
    img_widget = widgets.Image(
      value=image,
      format=img_format,
      layout=widgets.Layout(max_width="280px",
                            max_height="200px",
                            min_height="200px",
                            width="100%",
                            height="auto",
                            object_fit="contain"))
  except:
    img_widget = widgets.Label(value="No Image")

  # Main action button (RENT or RETURN)
  rent_button = widgets.Button(
    description="RENT" if game["Available"] else "RETURN",
    layout=widgets.Layout(width="120px", height="40px")
  )

  if game["Available"]:
    rent_button.style.button_color = "#0da602"
    rent_button.on_click(lambda x: rent_callback(game))
  else:
    rent_button.style.button_color = "darkgray"
    rent_button.on_click(lambda x: return_callback(game))

  # Reviews button
  reviews_button = widgets.Button(
    description="📝 Reviews",
    layout=widgets.Layout(width="120px", height="35px"),
    button_style='info'
  )
  reviews_button.on_click(lambda x: reviews_callback(game))

  # Basic game info
  title = widgets.Label(value=game['Name'])
  players = widgets.Label(value=f"Players: {game['NoPlayers']}")
  genre = widgets.Label(value=f"Genre: {game['Genre']}")

  # Build status section (available vs rented)
  if game['Available']:
    border_color = "green"
    rating_widget = create_star_display(game['Rating'], None)
    status = widgets.HTML(
      value="<span style='color: green; font-weight: bold;'>AVAILABLE</span>",
    )
    card_children = [title, img_widget, players, genre, rating_widget, status, rent_button, reviews_button]
  else:
    border_color = "red"
    # Show who rented it if that info exists
    if "RentalInfo" in game:
      rental = game["RentalInfo"]
      status = widgets.HTML(
        value=f"<div style='text-align: center;'>"
        f"<span style='color: red; font-weight: bold;'>RENTED</span><br>"
        f"Rented by: {rental['CustomerID']}<br>",
      )
    else:
      status = widgets.HTML(
        value="<span style='color: red; font-weight: bold;'>RENTED</span>",
      )
    card_children = [title, img_widget, players, genre, status, rent_button, reviews_button]

  # Assemble card with colored border
  card = widgets.VBox(
    card_children,
    layout=widgets.Layout(
      border=f"2px solid {border_color}",
      padding="4px",
      margin="6px",
      width="280px",
      max_width="400px",
      min_width="200px",
      min_height="500px",
      align_items="center",
      grid_gap="2px"
    )
  )

  return card
