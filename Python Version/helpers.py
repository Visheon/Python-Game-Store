# ============================================
# HELPER FUNCTIONS
# ============================================
#
# Shared utilities used across the rest of the game rental system:
# customer validation, game loading, ratings, rental tracking, and
# image fetching/caching.

import csv
import os
from datetime import datetime, timedelta

import ipywidgets as widgets
import requests

import feedbackManager as fmDS
import subscriptionManager as smDS

# =================
# Global Variables
# =================

IMAGE_CACHE = {}


def getCustomer(username):
  today = datetime.today().strftime('%Y-%m-%d')
  # Look up customer in subscription file
  with open("Subscription_Info.txt", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
      if row["CustomerID"] == username:
        if row["EndDate"] < today:
          return -1
        return row
    return None


def getLimit(customer):
  # Returns rental limit based on subscription tier
  if customer["SubscriptionType"] == 'Basic':
    return smDS.BASIC_LIMIT
  else:
    return smDS.PREMIUM_LIMIT


def get_user_rent_count(username):
  # Count active rentals for a user (no return date)
  count = 0
  if not os.path.exists("Rental.txt"):
    return count
  with open("Rental.txt", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
      if row["CustomerID"] == username and row['ReturnDate'] == "":
        count += 1
  return count


def get_game_rent_count(game_id):
  # Total times a game has been rented
  count = 0
  if not os.path.exists("Rental.txt"):
    return count
  with open("Rental.txt", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      if row["GameID"] == game_id:
        count += 1
  return count


def get_average_rating(game_id):
  # Calculate average star rating from feedback
  if not os.path.exists("Game_Feedback.txt"):
    return None
  ratings = []
  with open("Game_Feedback.txt", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      if row["GameID"] == game_id:
        ratings.append(int(row["Rating"]))
  if not ratings:
    return None
  return sum(ratings) / len(ratings)


def get_game_reviews(game_id):
  # Pull all reviews for a specific game
  all_feedback = fmDS.load_feedback('Game_Feedback.txt')
  reviews = []
  for feedback in all_feedback:
    if feedback["GameID"] == game_id:
      reviews.append({
        "Rating": int(feedback["Rating"]),
        "Comment": feedback["Comments"]
    })
  return reviews


def load_games(filename, game_type):
  # Load games from CSV and attach rating/rental data
  games = []
  with open(filename, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      games.append({
        "GameID": row["GameID"],
        "Name": row["Name"],
        "Image": row["Image"],
        "NoPlayers": row["NoPlayers"],
        "Genre": row["Genre"],
        "PurchaseDate": row["PurchaseDate"],
        "Type": game_type,
        "Available": True,
        "Rating": get_average_rating(row["GameID"]),
        "RentalCount": get_game_rent_count(row["GameID"])
      })
  return games


def load_rentals():
  # Get all currently active rentals (no return date set)
  rentals = {}
  if os.path.exists("Rental.txt"):
    with open("Rental.txt", 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
        if row["ReturnDate"] == "":
          rentals[row["GameID"]] = row
  return rentals


def create_star_display(rating, string):
  # Creates star rating widget (★★★½☆ format)
  if rating == None:
    return widgets.Label(value="No ratings yet", layout=widgets.Layout(height='25px'))

  # Round to nearest half star
  rounded_rating = round(rating * 2) / 2
  full_stars = int(rounded_rating)
  half_star = (rounded_rating % 1) != 0
  empty_stars = 5 - full_stars - (1 if half_star else 0)

  star_str = "★" * full_stars
  if half_star:
    star_str += "½"
  star_str += "☆" * empty_stars

  if string == None:

    display_text = f"{star_str} {rating:.1f}"

    return widgets.HTML(
      value=f"<div style='color: #FFA500; font-size: 16px;'>{display_text}</div>",
      layout=widgets.Layout(height="25px")
    )
  else:
    return star_str

def get_cached_image(image_url):
  # Fetches an image from github and "caches" it

  if image_url in IMAGE_CACHE:
    return  IMAGE_CACHE[image_url]

  try:
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()
    image = response.content
    IMAGE_CACHE[image_url] = image
    return image

  except Exception as e:
    print(f"Error fetching image from URL: {image_url}")
    print(e)
    return None

def get_image_format(game, image):
  if image:
  # Detect format from URL or default to common formats
    image_url = game["Image"].lower()
    if '.png' in image_url:
      img_format = 'png'
      return img_format
    elif '.jpg' in image_url or '.jpeg' in image_url:
      img_format = 'jpeg'
      return img_format
    elif '.gif' in image_url:
      img_format = 'gif'
      return img_format
    elif '.avif' in image_url:
      img_format = 'avif'
      return img_format
    else:
      img_format = 'png'
      return img_format

def get_game_rent_count_by_period(game_id, days=None):
  # Finds the number of times a game has been rented based on a period
  count = 0
  if not os.path.exists("Rental.txt"):
    return count

  # Calculate cutoff date if days specified
  cutoff_date = None
  if days is not None:
    cutoff_date = (datetime.today() - timedelta(days=days)).strftime('%Y-%m-%d')

  with open("Rental.txt", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      if row["GameID"] == game_id:
        # If there is a time filter, check the rental date
        if cutoff_date and row["RentalDate"] < cutoff_date:
          continue
        count += 1
    return count
