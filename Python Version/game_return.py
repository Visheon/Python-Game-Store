# ============================================
# GAME RETURN
# ============================================
#
# Handles returns with mandatory feedback collection (star rating + comments).

import csv
import time
from datetime import datetime

import ipywidgets as widgets
from IPython.display import clear_output, display

import feedbackManager as fmDS


def return_game_on_star_click(btn, rating, selected_rating, star_buttons):
  selected_rating[0] = rating
  # Fill stars up to selected rating
  for i, star_btn in enumerate(star_buttons):
    if i < rating:
      star_btn.button_style = 'warning'
    else:
      star_btn.button_style = ''


def return_game_create_star_button(rating, selected_rating, star_buttons):
  btn = widgets.Button(
    description='★',
    layout=widgets.Layout(width='50px', height='50px'),
    style={'font_size': '24px'}
  )
  btn.on_click(lambda btn: return_game_on_star_click(btn, rating, selected_rating, star_buttons))
  return btn


def return_game_on_submit(btn, selected_rating, comment_input, message_label, game, return_to_callback):
  # Validate feedback before processing return
  if selected_rating[0] == 0:
    message_label.value = "❌ Please select a rating"
    return

  comment_text = comment_input.value.strip()
  if not comment_text:
    comment_text = "No comments given."

  # Save feedback
  fmDS.add_feedback(
    game['GameID'],
    selected_rating[0],
    comment_text,
    'Game_Feedback.txt'
  )

  # Update rental record with return date
  updated_rows = []
  with open("Rental.txt", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
      if row["GameID"] == game["GameID"] and row["ReturnDate"] == "":
        row["ReturnDate"] = datetime.now().strftime("%Y-%m-%d")
      updated_rows.append(row)

  # Write back all rentals
  with open("Rental.txt", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["GameID", "RentalDate", "ReturnDate", "CustomerID"])
    writer.writeheader()
    writer.writerows(updated_rows)

  game["Available"] = True

  clear_output(wait=True)
  success_label = widgets.Label(value="✔ Game returned and feedback submitted successfully!")
  display(success_label)
  time.sleep(2)
  return_to_callback()


def return_game_on_cancel(btn, cancel_callback):
  clear_output(wait=True)
  cancel_callback()


def return_game(game, return_to_callback, cancel_callback):
  if game["Available"]:
    return

  star_buttons = []
  selected_rating = [0]  # Use list to maintain reference in nested function

  # Create star buttons
  for i in range(1, 6):
    star_buttons.append(return_game_create_star_button(i, selected_rating, star_buttons))

  stars_container = widgets.HBox(
    star_buttons,
    layout=widgets.Layout(justify_content='center', margin='10px 0')
  )

  # Comment input
  comment_label = widgets.Label(
    value='Comments:',
    layout=widgets.Layout(width='400px', margin='10px 0 5px 0')
  )
  comment_input = widgets.Textarea(
    placeholder='Share your experience with this game...',
    layout=widgets.Layout(width='400px', height='100px')
  )

  submit_button = widgets.Button(
    description="Submit Feedback",
    button_style="success",
    layout=widgets.Layout(width='150px')
  )
  cancel_button = widgets.Button(
    description="Cancel",
    button_style="danger",
    layout=widgets.Layout(width='150px')
  )

  message_label = widgets.Label(value="")

  submit_button.on_click(lambda btn: return_game_on_submit(btn, selected_rating, comment_input, message_label, game, return_to_callback))
  cancel_button.on_click(lambda btn: return_game_on_cancel(btn, cancel_callback))

  title_label = widgets.Label(
    value=f"Return Game: {game['Name']}",
    layout=widgets.Layout(margin='0 0 10px 0')
  )
  rating_label = widgets.Label(
    value="Rate your experience (click stars):",
    layout=widgets.Layout(margin='10px 0 5px 0')
  )

  popup = widgets.VBox(
    [
      title_label,
      rating_label,
      stars_container,
      comment_label,
      comment_input,
      message_label,
      widgets.HBox(
        [submit_button, cancel_button],
          layout=widgets.Layout(justify_content='center', margin='10px 0')
      )
    ],
      layout=widgets.Layout(
        align_items='center',
        padding='20px',
        border='2px solid gray',
        width='500px',
        margin='50px auto'
      )
  )

  clear_output(wait=True)
  display(popup)
