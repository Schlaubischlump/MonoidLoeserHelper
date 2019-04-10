from .parser import create_php_data


def str_to_points(point_str):
    """
    Convert a string of point to the corresponding integer.
    All unknown characters, including "-" lead to a value of 0.
    :param point_str: integer points as string
    """
    try:
        return float(point_str)
    except:
        try:
            return float(point_str.replace(",", "."))
        except:
            pass
    return 0


def points_to_str(points):
    """
    Convert points to a readable string.
    :param points: number of points
    """
    if points == 0:
        return "-"
    else:
        if points.is_integer():
            return str(int(points))
        return str(points).replace(".", ",")


def export_data_to_file(path, headers, data):
    """
    Create a new php file with all the data at the given path.
    :param path: path to php file.
    """
    php_data = create_php_data(headers, data)
    with open(path, "w+") as f:
        f.write(php_data)
