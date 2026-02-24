import svg

canvas = svg.SVG(
    width=60,
    height=60,
    elements=[
        svg.Circle(
            cx=30,
            cy=30,
            r=20,
            stroke='red',
            fill='white',
            stroke_width=5,
        ),
    ],
)
print(canvas)
