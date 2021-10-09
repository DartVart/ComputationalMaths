def update_figure_to_x_axis(figure):
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(showgrid=False, zeroline=True, zerolinecolor="gray", zerolinewidth=2, showticklabels=False)
    figure.update_layout(height=70, plot_bgcolor="white", showlegend=False, margin=dict(b=0, t=60))


def add_nodes(fig, points, func, name, color, size, hover_template="(%{x}, %{y})"):
    fig.add_scatter(
        x=points,
        y=[func(point) for point in points],
        mode="markers",
        hovertemplate=hover_template,
        name=name,
        marker=dict(color=color, size=size),
    )


def add_line(fig, points, func, name, color, inverse=False, dash=None, hover_template="(%{x}, %{y})"):
    f_points = [func(point) for point in points]
    x = points if not inverse else f_points
    y = f_points if not inverse else points
    fig.update_layout(
        yaxis_range=[max(min(y), -100), min(max(y), 100)], xaxis_range=[max(min(x), -100), min(max(x), 100)]
    )
    fig.add_scatter(
        x=x,
        y=y,
        hovertemplate=hover_template,
        name=name,
        line=dict(color=color, width=2, dash=dash),
    )
