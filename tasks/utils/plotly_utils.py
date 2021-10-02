def update_figure_to_x_axis(figure):
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(showgrid=False, zeroline=True, zerolinecolor="gray", zerolinewidth=2, showticklabels=False)
    figure.update_layout(height=70, plot_bgcolor="white", showlegend=False, margin=dict(b=0, t=60))
