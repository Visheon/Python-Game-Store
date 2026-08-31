# ============================================
# BOOKINGS
# ============================================
#
# In-store gaming session bookings with capacity management (50 person
# limit per time slot).

import csv
import os
import time
from datetime import datetime, timedelta

import ipywidgets as widgets
from IPython.display import clear_output, display

from helpers import getCustomer


def book_session_check_capacity(date_str, time_slot):
  # Calculate current bookings for a time slot
  total_guests = 0
  if os.path.exists("Bookings.txt") and os.path.getsize("Bookings.txt") > 0:
    with open("Bookings.txt", 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
        if row["BookingDate"] == date_str and row["Time"] == time_slot:
          total_guests += int(row["NoGuests"])
  return total_guests


def bookings_get_capacity_for_date(date_str):
  # Get capacity information for all time slots on a specific date
  capacity_info = {
    "14:00-18:00 (2pm-6pm)": 0,
    "18:00-22:00 (6pm-10pm)": 0
  }

  if os.path.exists("Bookings.txt") and os.path.getsize("Bookings.txt") > 0:
    with open("Bookings.txt", 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
        if row["BookingDate"] == date_str and row["Time"] in capacity_info:
          capacity_info[row["Time"]] += int(row["NoGuests"])

  return capacity_info


def bookings_remove_expired():
  # Remove bookings that have passed their date
  if not os.path.exists("Bookings.txt") or os.path.getsize("Bookings.txt") == 0:
    return

  today = datetime.now().date()
  updated_rows = []

  with open("Bookings.txt", "r") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
      booking_date = datetime.strptime(row["BookingDate"], "%Y-%m-%d").date()
      # Keep only future bookings
      if booking_date >= today:
        updated_rows.append(row)

  # Write back only active bookings
  with open("Bookings.txt", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)


def book_session_on_confirm(btn, user_input, message, booking_date, time_dropdown, party_size, return_to_callback):
  username = user_input.value.strip()
  customer = getCustomer(username)

  if customer == None:
    message.value = "❌ Invalid User ID"
    return
  elif customer == -1:
    message.value = "❌ Subscription has expired"
    return

  if booking_date.value == None:
    message.value = "❌ Please select a date"
    return

  if party_size.value < 1 or party_size.value > 3:
      message.value = "❌ Party size must be between 1 and 3 guests"
      return

  # Check for duplicate bookings
  if os.path.exists("Bookings.txt"):
    with open("Bookings.txt", 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
        if row["UserId"] == username and booking_date.value == row["BookingDate"]:
          message.value = "❌ User already has an active booking. Please cancel it first."
          return

        if (row["BookingDate"] == booking_date.value and
          row["Time"] == time_dropdown.value):
          message.value = "❌ This time slot is already fully booked. Please choose another time."
          return

  # Check capacity limit (50 people per slot)
  current_capacity = book_session_check_capacity(booking_date.value, time_dropdown.value)

  if current_capacity + party_size.value > 50:
    message.value = f"❌ Not enough space! Only {50 - current_capacity} spots left for this time slot."
    return

  # Create booking
  booking_entry = {
    "UserId": username,
    "BookingDate": booking_date.value,
    "Time": time_dropdown.value,
    "NoGuests": str(party_size.value)
  }

  file_exists = os.path.exists("Bookings.txt") and os.path.getsize("Bookings.txt") > 0
  with open("Bookings.txt", "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["UserId", "BookingDate", "Time", "NoGuests"])
    if not file_exists:
      writer.writeheader()
    writer.writerow(booking_entry)

  message.value = "✔ Session booked successfully!"
  time.sleep(2)
  clear_output(wait=True)
  return_to_callback()


def book_session_on_cancel(btn, cancel_callback):
  clear_output(wait=True)
  cancel_callback()


def book_session(return_to_callback, cancel_callback):
  popup = widgets.VBox()
  user_input = widgets.Text(description="User ID:", style={'description_width': '100px'})

  # Generate next 30 days of dates
  today = datetime.now().date()
  date_options = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 31)]
  booking_date = widgets.Dropdown(
    options=date_options,
    description="Date:",
    style={'description_width': '100px'}
  )

  times = ["14:00-18:00 (2pm-6pm)", "18:00-22:00 (6pm-10pm)"]
  time_dropdown = widgets.Dropdown(
    options=times,
    description="Time:",
    style={'description_width': '100px'}
  )

  party_size = widgets.IntSlider(
    description="No. Guests:",
    value=1,
    min=1,
    max=3,
    step=1,
    style={'description_width': '100px'},
    layout=widgets.Layout(width='300px')
  )

  confirm_button = widgets.Button(description="Book Session", button_style="success")
  cancel_button = widgets.Button(description="Cancel", button_style="danger")
  message = widgets.Label(value="")

  confirm_button.on_click(lambda btn: book_session_on_confirm(btn, user_input, message, booking_date, time_dropdown, party_size, return_to_callback))
  cancel_button.on_click(lambda btn: book_session_on_cancel(btn, cancel_callback))

  title_label = widgets.Label(value="Book an In-Store Gaming Session")
  popup = widgets.VBox(
    [title_label, user_input, booking_date, time_dropdown, party_size, message,
      widgets.HBox([confirm_button, cancel_button], layout=widgets.Layout(justify_content='center'))],
      layout=widgets.Layout(align_items='center', padding='10px'))

  clear_output(wait=True)
  display(popup)


def bookings_cancel_booking(btn, user_id, booking_date, booking_time, return_to_callback):
  # Removes a specific booking from file based on UserId, Date, and Time
  updated_rows = []
  with open("Bookings.txt", "r") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
      # Keep all bookings except the one that matches all three criteria
      if not (r["UserId"] == user_id and r["BookingDate"] == booking_date and r["Time"] == booking_time):
        updated_rows.append(r)

  with open("Bookings.txt", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)

  return_to_callback()


def bookings_update_capacity_display(info_box_html, date_filter):
  # Update the entire HTML info box based on selected date"""
  selected_date = date_filter.value

  if selected_date == "All Dates":
    info_box_html.value = """
    <div style="
      background-color: #2E7D32;
      padding: 20px;
      border-radius: 8px;
      width: 750px;
      margin: 0 auto;
    ">
    <div style="
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    ">
      <span style="font-weight: bold; font-size: 16px; color: white;">
        📋 In-Store Session Bookings
      </span>
      </div>
      <div style="color: white; line-height: 1.8;">
      <div style="font-weight: bold;">Select a date to view capacity</div>
      </div>
      </div>
      """
    return

  # Get capacity for the selected date
  capacity_info = bookings_get_capacity_for_date(selected_date)

  # Date Formatting
  date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
  day_name = date_obj.strftime("%A")
  formatted_date = date_obj.strftime("%B %d, %Y")

  today = datetime.now().date()
  is_today = date_obj.date() == today
  today_badge = " TODAY" if is_today else ""

  # Calculate capacity info
  afternoon_booked = capacity_info["14:00-18:00 (2pm-6pm)"]
  afternoon_remaining = 50 - afternoon_booked
  evening_booked = capacity_info["18:00-22:00 (6pm-10pm)"]
  evening_remaining = 50 - evening_booked

  # Update the entire HTML box with capacity information
  info_box_html.value = f"""
  <div style="
    background-color: #2E7D32;
    padding: 20px;
    border-radius: 8px;
    width: 750px;
    margin: 0 auto;
  ">
  <div style="
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  ">
    <span style="font-weight: bold; font-size: 16px; color: white;">
    📋 In-Store Session Bookings
    </span>
    </div>
    <div style="color: white; line-height: 1.8;">
      <div style="font-weight: bold; margin-bottom: 10px;">📅 {day_name}, {formatted_date}{today_badge}</div>
      <div>2pm-6pm: {afternoon_booked}/50 booked ({afternoon_remaining} remaining)</div>
      <div>6pm-10pm: {evening_booked}/50 booked ({evening_remaining} remaining)</div>
    </div>
    </div>
    """


def bookings_filter_by_date(change, date_filter, booking_cards_container, info_box_html, all_bookings, return_to_callback):
  # Update capacity display in the header
  bookings_update_capacity_display(info_box_html, date_filter)

  # Filter bookings based on selected date
  selected_date = date_filter.value

  if selected_date == "All Dates":
    filtered_bookings = all_bookings
  else:
    filtered_bookings = [b for b in all_bookings if b["BookingDate"] == selected_date]

  # Rebuild the booking cards with filtered data
  if not filtered_bookings:
    no_bookings = widgets.Label(
      value=f"No bookings for {selected_date}" if selected_date != "All Dates" else "No active bookings",
      layout=widgets.Layout(margin='50px 0')
    )
    no_bookings_centered = widgets.HBox(
      [no_bookings],
      layout=widgets.Layout(justify_content='center')
    )
    booking_cards_container.children = [no_bookings_centered]
    return

  booking_cards = []
  for row in filtered_bookings:
    cancel_btn = widgets.Button(
      description="Cancel",
      button_style='danger',
      layout=widgets.Layout(
        width='100px',
        height='30px',
        margin='5px 0 0 0'
      )
    )

    cancel_btn.on_click(lambda btn, uid=row["UserId"], bdate=row["BookingDate"], btime=row["Time"]: bookings_cancel_booking(btn, uid, bdate, btime, return_to_callback))

    session_title = widgets.Label(value="📅 In-Store Session", layout=widgets.Layout(font_weight='bold'))
    user_id_label = widgets.Label(value=f"User: {row['UserId']}")
    date_label = widgets.Label(value=f"Date: {row['BookingDate']}")
    time_label = widgets.Label(value=f"Time: {row['Time']}")
    guests_label = widgets.Label(value=f"Guests: {row['NoGuests']}")

    button_container = widgets.HBox(
      [cancel_btn],
      layout=widgets.Layout(justify_content='center')
    )

    booking_card = widgets.VBox([
      session_title,
      user_id_label,
      date_label,
      time_label,
      guests_label,
      button_container
    ], layout=widgets.Layout(
      border='2px solid gray',
      padding='10px',
      margin='8px',
      width='380px'
    ))

    booking_cards.append(booking_card)

  # Grid layout for booking cards (2 columns max)
  bookings_grid = widgets.GridBox(
    booking_cards,
    layout=widgets.Layout(
      grid_template_columns="repeat(2, 400px)",
      justify_content='center',
      grid_gap='10px',
      margin='20px 0'
    )
  )

  booking_cards_container.children = [bookings_grid]


def create_bookings_view(book_callback, return_to_callback):
  # Remove expired bookings first
  bookings_remove_expired()

  # Build the bookings tab view
  book_button = widgets.Button(
    description="📅 Book New Session",
    button_style='success',
    layout=widgets.Layout(width='180px', height='35px')
  )

  book_button.on_click(lambda x: book_callback())

  # Load and sort bookings chronologically
  all_bookings = []
  if os.path.exists("Bookings.txt") and os.path.getsize("Bookings.txt") > 0:
    with open("Bookings.txt", 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
        all_bookings.append(row)

    # Sort by date, then by time
    all_bookings.sort(key=lambda x: (x["BookingDate"], x["Time"]))

  # Create date filter dropdown - OUTSIDE the info box
  unique_dates = sorted(list(set([b["BookingDate"] for b in all_bookings]))) if all_bookings else []
  date_options = ["All Dates"] + unique_dates

  date_filter = widgets.Dropdown(
    options=date_options,
    value="All Dates",
    description="Filter by Date:",
    style={'description_width': '95px'},
    layout=widgets.Layout(width='320px', margin='0 0 10px 0')
  )

  date_filter_container = widgets.HBox(
    [date_filter],
    layout=widgets.Layout(justify_content='center', margin='20px 0 10px 0')
  )

  # Single HTML info box with dark green background
  info_box_html = widgets.HTML(
    value="""
    <div style="
      background-color: #2E7D32;
      padding: 20px;
      border-radius: 8px;
      width: 750px;
      margin: 0 auto;
    ">
      <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
      ">
        <span style="font-weight: bold; font-size: 16px; color: white;">
          📋 In-Store Session Bookings
        </span>
      </div>
      <div style="color: white; line-height: 1.8;">
        <div style="font-weight: bold;">Select a date to view capacity</div>
      </div>
    </div>
    """,
    layout=widgets.Layout(width='100%', margin='0 0 20px 0')
  )

  # Button positioned below the header
  button_container = widgets.HBox(
    [book_button],
    layout=widgets.Layout(justify_content='center', margin='20px 0')
  )

  # Container for booking cards (will be updated by filter)
  booking_cards_container = widgets.VBox()

  # Initial display (all bookings)
  bookings_filter_by_date(None, date_filter, booking_cards_container, info_box_html, all_bookings, return_to_callback)

  # Connect filter dropdown to update function
  date_filter.observe(
    lambda change: bookings_filter_by_date(change, date_filter, booking_cards_container, info_box_html, all_bookings, return_to_callback),
    names='value'
  )

  return widgets.VBox([
    date_filter_container,
    info_box_html,
    button_container,
    booking_cards_container
  ], layout=widgets.Layout(padding="20px", align_items='center'))
