import pandas as pd


def style_pandas_html_table(
    data_frame: pd.DataFrame, table_heading: str
) -> str:
    """
    Write pandas data frame to html and add a CSS file.

    Arguments:
    ---------
    data_frame: Pandas data frame.

    table_heading: Add a table heading.
    """

    pd.set_option("colheader_justify", "center")

    html_string = """
    <html>
      <head>
      </head>
      <link rel="stylesheet" type="text/css" href="/static/pandas_table_style.css"/>
      <body>
        <h1>{table_heading}</h1>
        {data_frame}
      </body>
    </html>.
    """

    html = html_string.format(
        table_heading=table_heading,
        data_frame=data_frame.to_html(
            # escape = False -> to 'render' links properly
            classes="mystyle",
            index=False,
            escape=False,
        ),
    )

    return html
