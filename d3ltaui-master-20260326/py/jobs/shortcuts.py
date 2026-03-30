def get_csv_preview(csv_path):
    from pandas import read_csv
    from logging import getLogger

    try:
        with open(csv_path, "rb") as f:
            df = read_csv(f, nrows=10)
            return { "columns": df.columns.tolist(), "data": df.values.tolist() }
    except Exception as e:
        getLogger().exception(e)
        return { "columns": [], "data": [] }


def remove_file(path):
    from os import remove
    from logging import getLogger

    try:
        remove(path)
    except FileNotFoundError:
        pass
    except Exception as e:
        getLogger().exception(e)


def sort_clusters(items):
    def sort_key(item):
        cid = item["id"]

        if cid == "all":
            return (0, "", "")
        if cid == "none":
            return (1, "", "")

        cid_str = str(cid)
        return (2, len(cid_str), cid_str.lower())

    return sorted(items, key=sort_key)
