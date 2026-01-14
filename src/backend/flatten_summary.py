def flatten_summary(d, parent_key=""):
    """
    Converts nested dict from locationData into flat list of dicts with 'Metric' and 'Value'.
    Example:
    {
      'numRows': 8128,
      'mostCommonBee': {'scientificName': 'Osmia', 'count': 827}
    }
    becomes:
    [
      {'Metric': 'numRows', 'Value': 8128},
      {'Metric': 'mostCommonBee.scientificName', 'Value': 'Osmia'},
      {'Metric': 'mostCommonBee.count', 'Value': 827}
    ]
    """
    rows = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            rows.extend(flatten_summary(v, new_key))
        else:
            rows.append({"Metric": new_key, "Value": v})
    return rows