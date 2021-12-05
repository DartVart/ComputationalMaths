def update_figure_to_x_axis(figure):
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(showgrid=False, zeroline=True, zerolinecolor="gray", zerolinewidth=2, showticklabels=False)
    figure.update_layout(height=70, plot_bgcolor="white", showlegend=False, margin=dict(b=0, t=60))


def add_nodes(fig, points, func, name, color, size, hover_template="(%{x}, %{y})", row=None, col=None, showlegend=True):
    fig.add_scatter(
        x=points,
        y=[func(point) for point in points],
        mode="markers",
        hovertemplate=hover_template,
        name=name,
        marker=dict(color=color, size=size),
        row=row,
        col=col,
        showlegend=showlegend
    )


def add_line(
    fig, points, func, name, color, inverse=False, dash=None, hover_template="(%{x}, %{y})", row=None, col=None
):
    f_points = [func(point) for point in points]
    x = points if not inverse else f_points
    y = f_points if not inverse else points
    fig.update_xaxes(range=[max(min(x), -1000), min(max(x), 1000)], row=row, col=col)
    fig.update_yaxes(range=[max(min(y), -1000), min(max(y), 1000)], row=row, col=col)
    fig.add_scatter(
        x=x, y=y, hovertemplate=hover_template, name=name, line=dict(color=color, width=2, dash=dash), row=row, col=col
    )
