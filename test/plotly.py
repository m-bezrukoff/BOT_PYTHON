from simulator_v2.playground_plotly import do_plot_online

pair = 'BTC_ETH'
charts = load_charts_from_file(pair=pair)
print(type(charts))

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
charts = charts[:2000]
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

fr = -2000
to = -1000
limit = 210000
dimension = 14


arr = render_indicators(charts, fr, to)
points_in = find_enter_points(arr)
points_out = find_exit_points(arr)
# points = render_test_data(dimension, arr)
# points = []
profit_calculator(points_in, points_out, charts, fr, to)
do_plot_online(points_in, points_out, arr)
