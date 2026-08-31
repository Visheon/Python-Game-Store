# ============================================
# REVIEWS DISPLAY
# ============================================
#
# Shows all reviews for a game with average rating.

import ipywidgets as widgets
from IPython.display import clear_output, display

from helpers import get_game_reviews, create_star_display


def show_reviews_on_close(btn, cancel_callback):
  clear_output(wait=True)
  cancel_callback()


def show_reviews(game, return_to_callback, cancel_callback):
  reviews = get_game_reviews(game["GameID"])

  title = widgets.HTML(
    value=f"<h3 style='margin: 0 0 10px 0;'>Reviews for {game['Name']}</h3>"
  )

  # Show average rating at top
  avg_rating = game.get('Rating')
  if avg_rating:
    avg_display = widgets.HTML(
    value=f"<div style='text-align: center; margin: 10px 0;'>"
          f"<span style='color: #FFA500; font-size: 20px;'>{'★' * int(round(avg_rating))}{'☆' * (5 - int(round(avg_rating)))}</span><br>"
          f"<span style='font-size: 16px;'>Average: {avg_rating:.1f}/5.0 ({len(reviews)} reviews)</span>"
          f"</div>"
    )
  else:
    avg_display = widgets.Label(value="No reviews yet")

  close_btn = widgets.Button(
    description="Close",
    button_style='primary',
    layout=widgets.Layout(width='150px', margin='10px 0')
  )

  close_btn.on_click(lambda btn: show_reviews_on_close(btn, cancel_callback))

  # Build review cards
  if not reviews:
    review_widgets = [widgets.Label(
      value="No reviews yet.",
      layout=widgets.Layout(margin='20px 0')
  )]
  else:
    review_widgets = []
    for review in reviews:
      stars = create_star_display(review["Rating"], None)
      comment = widgets.Label(
        value=review["Comment"],
        layout=widgets.Layout(margin='5px 0 0 0')
      )

      review_card = widgets.VBox(
        [stars, comment],
        layout=widgets.Layout(
          border='1px solid #ccc',
          padding='10px',
          margin='5px 0',
          width='100%',
          background_color='#f9f9f9'
        )
      )
      review_widgets.append(review_card)

  # Scrollable container for reviews
  reviews_container = widgets.VBox(
    review_widgets,
    layout=widgets.Layout(
      max_height='400px',
      overflow_y='auto',
      width='100%',
      padding='10px'
    )
  )

  popup = widgets.VBox(
    [title, avg_display, close_btn, reviews_container],
    layout=widgets.Layout(
      width='500px',
      max_height='600px',
      padding='20px',
      border='2px solid gray',
      margin='20px auto',
      align_items='center'
    )
  )

  clear_output(wait=True)
  display(popup)
