# ============================================
# ANALYTICS & INVENTORY PRUNING
# ============================================

import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import clear_output, display

from helpers import load_games, get_game_rent_count_by_period, create_star_display


def analytics_create_chart(chart_type, time_period=None):

  board_games = load_games("Board_Game_Info.txt", "board")
  video_games = load_games("Video_Game_Info.txt", "video")

  if chart_type == "Rental Distribution":
    # Calculate total rentals for video games vs board games
    video_rentals = sum([get_game_rent_count_by_period(g['GameID'], time_period) for g in video_games])
    board_rentals = sum([get_game_rent_count_by_period(g['GameID'], time_period) for g in board_games])

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    sizes = [video_rentals, board_rentals]
    labels = [f'Video Games\n({video_rentals} rentals)', f'Board Games\n({board_rentals} rentals)']
    colors = ['#4CAF50', '#FF9800']
    explode = (0.05, 0.05)

    chart_title = 'Game Rental Distribution'
    if time_period == 30:
      chart_title += ' (Last 30 Days)'
    elif time_period == 180:
      chart_title += ' (Last 180 Days)'
    else:
      chart_title += ' (All Time)'

    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                       startangle=90, explode=explode, textprops={'fontsize': 12, 'weight': 'bold'})

    ax.set_title(chart_title, fontsize=16, fontweight='bold', pad=20)

    # Make percentage text larger and white
    for autotext in autotexts:
      autotext.set_color('white')
      autotext.set_fontsize(14)
      autotext.set_weight('bold')

    plt.tight_layout()
    return

  elif chart_type == "Most Rented Games":
    # Update rental counts based on time period
    for game in board_games:
      game['RentalCount'] = get_game_rent_count_by_period(game['GameID'], time_period)
    for game in video_games:
      game['RentalCount'] = get_game_rent_count_by_period(game['GameID'], time_period)

    metric_key = 'RentalCount'
    chart_title = 'Most Rented Games'
    if time_period == 30:
      chart_title += ' (Last 30 Days)'
    elif time_period == 180:
      chart_title += ' (Last 180 Days)'
    else:
      chart_title += ' (All Time)'

    xlabel = 'Number of Rentals'
    vg_color = '#4CAF50'
    bg_color = '#FF9800'
    value_format = '{:.0f}'
    x_limit = None

  else:  # Games by Star Rating
    metric_key = 'Rating'
    chart_title = 'Games by Star Rating'
    xlabel = 'Average Rating (out of 5)'
    vg_color = '#2196F3'
    bg_color = '#9C27B0'
    value_format = '{:.1f}'
    x_limit = (0, 5)

  fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
  fig.patch.set_alpha(0)
  ax1.patch.set_alpha(0)
  ax2.patch.set_alpha(0)

  fig.suptitle(chart_title, fontsize=16, fontweight='bold')

  vg_names = [g['Name'][:20] + '...' if len(g['Name']) > 20 else g['Name'] for g in video_games]
  vg_values = [g[metric_key] if g[metric_key] is not None else 0 for g in video_games]

  ax1.barh(vg_names, vg_values, color=vg_color)
  ax1.set_xlabel(xlabel, fontweight='bold')
  ax1.set_title('Video Games', fontsize=14, fontweight='bold')
  ax1.invert_yaxis()

  if x_limit:
    ax1.set_xlim(x_limit)

  # Add value labels
  for i, v in enumerate(vg_values):
    offset = 0.05 if x_limit else v * 0.02
    ax1.text(v + offset, i, value_format.format(v), va='center')

  bg_names = [g['Name'][:20] + '...' if len(g['Name']) > 20 else g['Name'] for g in board_games]
  bg_values = [g[metric_key] if g[metric_key] is not None else 0 for g in board_games]

  ax2.barh(bg_names, bg_values, color=bg_color)
  ax2.set_xlabel(xlabel, fontweight='bold')
  ax2.set_title('Board Games', fontsize=14, fontweight='bold')
  ax2.invert_yaxis()

  if x_limit:
    ax2.set_xlim(x_limit)

  # Add value labels
  for i, v in enumerate(bg_values):
    offset = 0.05 if x_limit else v * 0.02
    ax2.text(v + offset, i, value_format.format(v), va='center')

  plt.tight_layout()


def analytics_update_charts(change, chart_selector, time_period_selector, chart_output):
  selected = chart_selector.value

  # Get time period (only relevant for rental charts)
  time_period = None
  if selected == "Most Rented Games" or selected == "Rental Distribution":
    period_value = time_period_selector.value
    if period_value == "Last 30 Days":
      time_period = 30
    elif period_value == "Last 180 Days":
      time_period = 180
    # if NO SELECTION, assumes all time (hence None)

  # Clear previous output
  chart_output.clear_output(wait=True)
  with chart_output:
    # Show the chart
    analytics_create_chart(selected, time_period)
    plt.show()


def analytics_ui(main_menu_callback):

  # View selection buttons
  # -----------------------

  charts_view_btn = widgets.Button(
    description="📊 Charts View",
    layout=widgets.Layout(width='50%', height='50px'),
    style={'font_weight': 'bold'}
  )

  underperformers_view_btn = widgets.Button(
    description="⚠️ Underperformers",
    layout=widgets.Layout(width='50%', height='50px'),
    style={'font_weight': 'bold'}
  )

  view_buttons = widgets.HBox(
    [charts_view_btn, underperformers_view_btn],
    layout=widgets.Layout(width='95%', margin='0 auto 20px auto')
  )

  # Charts View Components
  # ----------------------

  chart_selector = widgets.Dropdown(
    options=['Most Rented Games', 'Games by Star Rating', 'Rental Distribution'],
    description='View:',
    style={'description_width': '80px'},
    layout=widgets.Layout(width='300px')
  )

  # Time period selector for rental charts
  time_period_selector = widgets.Dropdown(
    options=['All Time', 'Last 180 Days', 'Last 30 Days'],
    value='All Time',
    description='Period:',
    style={'description_width': '80px'},
    layout=widgets.Layout(width='300px')
  )

  chart_output = widgets.Output(
    layout=widgets.Layout(
      width='100%',
      min_height='600px'
    )
  )

  selector_container = widgets.HBox(
    [chart_selector, time_period_selector],
    layout=widgets.Layout(justify_content='center', margin='20px 0',
                          grid_gap='20px')
  )

  charts_view = widgets.VBox([
    selector_container,
    chart_output
  ])

  # Underperformers View Components
  # --------------------------------

  min_rentals_slider = widgets.IntSlider(
    value=0,
    min=0,
    max=20,
    step=1,
    description='Min Rentals:',
    style={'description_width': '120px'},
    layout=widgets.Layout(width='500px')
  )

  min_rating_slider = widgets.FloatSlider(
    value=0.0,
    min=0.0,
    max=5.0,
    step=0.5,
    description='Min Rating:',
    style={'description_width': '120px'},
    layout=widgets.Layout(width='500px')
  )

  sliders_container = widgets.VBox(
    [min_rentals_slider, min_rating_slider],
    layout=widgets.Layout(
      align_items='center',
      margin='20px 0'
    )
  )

  underperformers_output = widgets.Output(
    layout=widgets.Layout(
      width='100%',
      min_height='600px',
      max_height='600px',
      overflow_y='auto'
    )
  )

  underperformers_view = widgets.VBox([
    sliders_container,
    underperformers_output
  ])

  # Content area
  # ------------

  content_area = widgets.VBox(
    layout=widgets.Layout(
      min_height='600px',
      border='2px solid gray',
      padding='20px'
    )
  )

  # View switching logic
  # --------------------

  current_view = [0]  # 0=charts, 1=underperformers

  def switch_and_update_time_selector(view_idx):
    analytics_switch_view(
      view_idx,
      current_view,
      charts_view_btn,
      underperformers_view_btn,
      content_area,
      charts_view,
      underperformers_view
    )
    # Show/hide time period selector based on chart type
    update_time_period_visibility()

  charts_view_btn.on_click(lambda btn: switch_and_update_time_selector(0))
  underperformers_view_btn.on_click(lambda btn: switch_and_update_time_selector(1))

  # Function to show/hide time period selector
  def update_time_period_visibility(change=None):
    if chart_selector.value == "Most Rented Games" or chart_selector.value == "Rental Distribution":
      time_period_selector.layout.visibility = 'visible'
    else:
      time_period_selector.layout.visibility = 'hidden'

  # Initial loads
  # -------------

  analytics_update_charts(None, chart_selector, time_period_selector, chart_output)
  analytics_update_underperformers(
    None,
    min_rentals_slider,
    min_rating_slider,
    underperformers_output
  )

  # Update when sliders change
  min_rentals_slider.observe(
    lambda change: analytics_update_underperformers(
      change,
      min_rentals_slider,
      min_rating_slider,
      underperformers_output
    ),
    names='value'
  )

  min_rating_slider.observe(
    lambda change: analytics_update_underperformers(
      change,
      min_rentals_slider,
      min_rating_slider,
      underperformers_output
    ),
    names='value'
  )

  # Update when dropdown changes
  chart_selector.observe(
    lambda change: [
      analytics_update_charts(change, chart_selector, time_period_selector, chart_output),
      update_time_period_visibility(change)
    ],
    names='value'
  )

  # Update when time period changes
  time_period_selector.observe(
    lambda change: analytics_update_charts(
      change,
      chart_selector,
      time_period_selector,
      chart_output
    ),
    names='value'
  )

  # Set initial visibility
  update_time_period_visibility()

  title = widgets.Label(
    value="📊 Analytics Dashboard",
    layout=widgets.Layout(margin='10px 0')
  )

  clear_output(wait=True)
  # Header
  header = widgets.HTML("<h2 style='color:#0b8517; margin:0'>PIXEL VAULT – ANALYTICS</h2>")

  main_menu_button = widgets.Button(
    description="🏠 Main Menu",
    button_style='success',
    layout=widgets.Layout(width='150px', height='40px'),
    style={'font_weight': 'bold'}
  )

  main_menu_button.on_click(lambda btn: main_menu_callback())

  header_frame = widgets.HBox(
    [header, main_menu_button],
    layout=widgets.Layout(
      width='95%',
      margin='0 auto 20px auto',
      padding='15px 20px',
      border='2px solid #0b8517',
      justify_content='space-between',
      align_items='center'
    )
  )

  # Content
  content = widgets.VBox([
    title,
    view_buttons,
    content_area
  ], layout=widgets.Layout(padding="20px", align_items='center'))

  main_container = widgets.VBox(
    [header_frame, content],
    layout=widgets.Layout(
      width='90%',
      margin='0 auto',
      padding='20px'
    )
  )

  # Set initial view
  analytics_switch_view(
    0,
    current_view,
    charts_view_btn,
    underperformers_view_btn,
    content_area,
    charts_view,
    underperformers_view
  )

  display(main_container)


def analytics_switch_view(
  view_index,
  current_view,
  charts_view_btn,
  underperformers_view_btn,
  content_area,
  charts_view,
  underperformers_view
):
  current_view[0] = view_index

  if view_index == 0:
    charts_view_btn.button_style = 'success'
    underperformers_view_btn.button_style = ''
    content_area.children = [charts_view]
  else:
    charts_view_btn.button_style = ''
    underperformers_view_btn.button_style = 'success'
    content_area.children = [underperformers_view]


def analytics_update_underperformers(
  change,
  min_rentals_slider,
  min_rating_slider,
  underperformers_output
):
  min_rentals = min_rentals_slider.value
  min_rating = min_rating_slider.value

  board_games = load_games("Board_Game_Info.txt", "board")
  video_games = load_games("Video_Game_Info.txt", "video")
  all_games = board_games + video_games

  underperforming = []

  for game in all_games:
    rental_count = game['RentalCount'] if game['RentalCount'] is not None else 0
    rating = game['Rating'] if game['Rating'] is not None else 0

    if rental_count < min_rentals or rating < min_rating:
      underperforming.append({
        'name': game['Name'],
        'type': game['Type'],
        'rentals': rental_count,
        'rating': rating
      })

  underperformers_output.clear_output(wait=True)
  with underperformers_output:
    if not underperforming:
      display(widgets.HTML(
        "<div style='text-align: center; margin: 50px; color: green; font-size: 18px;'>"
        "✔ All games meet the performance criteria!"
        "</div>"
      ))
    else:
      display(widgets.HTML(
        "<div style='text-align: center; margin: 20px 0; color: #FF5722; font-size: 16px; font-weight: bold;'>"
        f"{len(underperforming)} game(s) are underperforming and may need to be removed"
        "</div>"
      ))

      game_cards = []
      for game in underperforming:
        game_type_emoji = "🎮" if game['type'] == 'video' else "🎲"
        stars = create_star_display(game['rating'], "string") if game['rating'] > 0 else "No ratings"

        game_card = widgets.HTML(
          f"<div style='border: 1px solid #000; padding: 15px; margin: 10px; "
          f"background-color: #ffffff; color: #000000; border-radius: 5px;'>"
          f"<strong>{game_type_emoji} {game['name']}</strong><br>"
          f"Rentals: {game['rentals']} (Min: {min_rentals})<br>"
          f"Rating: {stars} ({game['rating']:.1f}/5.0, Min: {min_rating:.1f})"
          f"</div>"
        )
        game_cards.append(game_card)

      # Display games side by side in a grid
      games_grid = widgets.GridBox(
        game_cards,
        layout=widgets.Layout(
          grid_template_columns="repeat(2, 1fr)",
          grid_gap='10px',
          width='100%'
        )
      )
      display(games_grid)
