# ============================================
# GAME RENTAL
# ============================================
#
# Handles the rental process with customer validation and checks the
# subscription limit.

import csv
import os
import time
from datetime import datetime

import ipywidgets as widgets
from IPython.display import clear_output, display

from helpers import getCustomer, getLimit, get_user_rent_count


def rent_game_on_confirm(btn, user_input, message_label, return_to_callback, game):
  username = user_input.value.strip()
  customer = getCustomer(username)

  # Validate customer exists
  if customer == None:
    message_label.value = "❌ Invalid Username"
    return
  if customer == -1:
    message_label.value = "❌ Subscription has expired"
    return

  # Check if user has hit their rental limit
  limit = getLimit(customer)
  current_rented = get_user_rent_count(username)

  if current_rented >= limit:
    message_label.value = f"❌ You have reached your rental limit ({limit}). Please return a game first."
    return

  # Create rental record
  rental_entry = {
    "GameID": game["GameID"],
    "RentalDate": datetime.now().strftime("%Y-%m-%d"),
    "ReturnDate": "",  # Empty until returned
    "CustomerID": username
  }

  # Append to rental file
  file_exists = os.path.exists("Rental.txt")
  with open("Rental.txt", "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["GameID", "RentalDate", "ReturnDate", "CustomerID"])
    if not file_exists:
      writer.writeheader()
    writer.writerow(rental_entry)

  message_label.value = "✔ Game rented successfully!"
  time.sleep(2)
  clear_output(wait=True)
  return_to_callback()


def rent_game_on_cancel(btn, cancel_callback):
  clear_output(wait=True)
  cancel_callback()


def rent_game(game, return_to_callback, cancel_callback):
  user_input = widgets.Text(description="Customer ID:")
  message_label = widgets.Label(value="")
  confirm_button = widgets.Button(description="Confirm", button_style="success")
  cancel_button = widgets.Button(description="Cancel", button_style="danger")

  confirm_button.on_click(lambda btn: rent_game_on_confirm(btn, user_input, message_label, return_to_callback, game))
  cancel_button.on_click(lambda btn: rent_game_on_cancel(btn, cancel_callback))

  prompt_label = widgets.Label(value="Enter Customer ID to rent this game:")
  popup = widgets.VBox(
    [prompt_label, user_input, message_label, widgets.HBox([confirm_button, cancel_button])],
    layout=widgets.Layout(align_items='center', padding='10px')
  )

  clear_output(wait=True)
  display(popup)
