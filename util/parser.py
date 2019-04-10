import html
import requests
import datetime
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


class CorruptDataException(Exception):
    pass


def escape_html(text):
    """
    Escape html characters and transform Umlaute to their unicode representation.
    :param text: text to encode
    """
    return text.encode("ascii", "xmlcharrefreplace").decode("utf-8")


def create_php_data(headers, user_data):
    """
    Create valid php file data from the user data list.
    :param headers: all header fields 
    :param user_data: data for each student
    """
    today = datetime.date.today()
    # This date was always part of the summer break. We just use this as a reference date to change the school year
    # You could of course make this more complex and correct by using an api for the exact date of the summer break.
    reference_date = datetime.date(day=30, month=7, year=today.year)
    if today > reference_date:
        school_year = (today.year, today.year + 1)
    else:
        school_year = (today.year-1, today.year)

    header = """<?php include 'top.php';?>

<head>
<h2 style="color:firebrick">Rubrik der L&ouml;serinnen und L&ouml;ser</h2>
<p><i>Stand: {0}</i></p> <!-- aktuelles Datum im Format %d.%m.%Y -->
<p><i>Die Klassenangaben beziehen sich auf das Schuljahr {1}/{2}.</i></p> <!-- Schuljahr im Format 2018/2019 -->
<p>
</head>

<table border="1" width="400" style="margin-left:10%;">
    <colgroup>
        <col width="70">
        <col width="45">
        <col width="30">
        <col width="35">
        <col width="35">
        <col width="35">
        <col width="45">
        <col width="45">
        <col width="35">
    </colgroup>
    """.format(today.strftime("%d.%m.%Y"), *school_year)

    # Write the Header entries to the php file.
    widths = [70, 45, 30, 35, 35, 35, 35, 45, 35, 35]
    widths += [35]*(len(headers)-len(widths))
    th_str = """        <th align="left" valign="top" width="{0}" height="25">{1}</th>\n"""

    header += "<tr>\n"
    header += "".join([escape_html(th_str.format(w, h)) for w, h in zip(widths, headers)])
    header += "    </tr>"

    body_element = """
    <tr>
        <td>{0}</td> <!-- Name -->
        <i><td align="center" valign="bottom">{1}</td></i> <!-- Klassenstufe -->
        <td>{2}</td> <!-- Ort, Schule -->
        <td align="center" valign="center">{3}</td> <!-- Punkte 1 -->
        <td align="center" valign="center">{4}</td> <!-- Punkte 2 -->
        <td align="center" valign="center">{5}</td> <!-- Punkte 3 -->
        <td align="center" valign="center">{6}</td> <!-- Punkte 4 -->
        <b><td align="center" valign="center"><b>{7}</b></td></b> <!-- Summe -->
        <td align="center" valign="center">{8}</td> <!-- Forscherpunkte -->
        <td align="center" valign="center">{9}</td> <!-- Denkerchen -->
    </tr>"""

    footer = """
</table>

</td>
</tr>

<?php include 'bottom.php';?>
"""

    # Write the user list to the php file.
    body = "".join(body_element.format(*map(escape_html, data)) for data in user_data)

    return header + body + footer


def fetch_latest_data(url):
    """
    Fetch the latest data from the monoid website.
    :return: html source code
    """
    return requests.get(url, allow_redirects=True).content


def _parse_table(table_data):
    """
    Parse the html table structure which contains all headers and students.
    :param table_data: string with html table structure
    :return list of headings, list of all user data
    """
    parsed_html = BeautifulSoup(table_data, "html5lib")
    table = parsed_html.findChild("tbody")
    # Read the table content including the heading
    content = table.findChildren("tr")
    # Create a list with all table headers
    headers = [h.text for h in content[0].findChildren("th")]
    # Create a list with a tuple for each users
    # The elements in the tuple correspond to the data entries for a user.
    # The order of the elements inside the tuple is the same as inside the headers list.
    entries = [[e.text for e in user_row.findChildren("td")] for user_row in content[1:]]
    # Sanity check: Make sure that each entry contains all necessary information.
    if not all(len(e) == len(headers) for e in entries):
        raise CorruptDataException("Some data entries missing requiered fields.")
    # Return the headers and the sorted data.
    return headers, sorted(entries, key=lambda e: e[0].lower())


def parse_website_data(data):
    """
    Parse the html table and return the headings as well as all the user data.
    :param data: html source code data
    :return list of headings, list of all user data
    """
    parsed_html = BeautifulSoup(data, "html5lib")
    table_container = parsed_html.body.find("table")
    table = table_container.findChild("table")
    return _parse_table(str(table))


def parse_php_file(path):
    """
    Parse an exported php file.
    :param path: path to exported php file.
    :return list of headings, list of all user data
    """
    php_file = open(path, "r")
    content = php_file.read()
    php_file.close()

    parsed_html = BeautifulSoup(content, "html5lib")
    table = parsed_html.body.find("table")
    return _parse_table(str(table))
