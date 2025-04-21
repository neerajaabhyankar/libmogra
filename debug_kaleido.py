import kaleido

import asyncio
# await kaleido.get_chrome()

import plotly.graph_objects as go
fig = go.Figure()
# fig.write_image('aaa.png')

# async with kaleido.Kaleido(n=4, timeout=90) as k:
#   await k.write_fig(fig, path="./", opts={"format":"jpg"})

asyncio.run(
  kaleido.write_fig(
    fig,
    path="./",
    n=4
  )
)
