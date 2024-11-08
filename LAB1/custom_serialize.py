def custom_serialize(data):
    if isinstance(data, dict):
        items = []
        for key, value in data.items():
            key_type = get_type_string(key)
            value_serialized = custom_serialize(value)
            items.append(f"D:k:{key_type}({key}):v:{value_serialized}")
        return "{" + "; ".join(items) + "}"

    elif isinstance(data, list):
        items = [custom_serialize(item) for item in data]
        return f"L:[{'; '.join(items)}]"

    elif isinstance(data, str):
        return f"str({data})"

    elif isinstance(data, int):
        return f"int({data})"

    elif isinstance(data, float):
        return f"float({data})"

    elif data is None:
        return "null"

    else:
        raise TypeError(f"Unsupported data type: {type(data)}")


def custom_deserialize(serialized_data):
    serialized_data = serialized_data.strip()
    if serialized_data.startswith("L:["):
        items_str = serialized_data[3:-1]  # Remove L:[ and ]
        items = split_serialized_items(items_str)
        return [custom_deserialize(item) for item in items]

    elif serialized_data.startswith("{") and serialized_data.endswith("}"):
        items_str = serialized_data[1:-1]  # Remove { and }
        items = split_serialized_items(items_str)
        deserialized_dict = {}
        for item in items:
            if item.startswith("D:k:"):
                key, value = item.split(":v:", 1)
                key_type, key_value = extract_type_value(key[4:])  # Remove D:k:
                deserialized_dict[key_value] = custom_deserialize(value)
        return deserialized_dict

    else:
        return extract_type_value(serialized_data)[1]


def split_serialized_items(data_str):
    items = []
    bracket_count = 0
    current_item = []
    for char in data_str:
        if char == "[" or char == "{":
            bracket_count += 1
        elif char == "]" or char == "}":
            bracket_count -= 1
        if char == ";" and bracket_count == 0:
            items.append(''.join(current_item).strip())
            current_item = []
        else:
            current_item.append(char)
    if current_item:
        items.append(''.join(current_item).strip())
    return items


def get_type_string(value):
    if isinstance(value, str):
        return "str"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, dict):
        return "dict"
    elif isinstance(value, list):
        return "list"
    elif value is None:
        return "null"
    else:
        raise TypeError(f"Unsupported data type: {type(value)}")


def extract_type_value(data_str):
    if "(" not in data_str or not data_str.endswith(")"):
        raise ValueError(f"Incorrect format for type extraction: {data_str}")

    type_name, value_str = data_str.split("(", 1)
    value = value_str.rstrip(")")
    if type_name == "str":
        return str, value
    elif type_name == "int":
        return int, int(value)
    elif type_name == "float":
        return float, float(value)
    elif type_name == "null":
        return type(None), None
    else:
        raise TypeError(f"Unsupported type in deserialization: {type_name}")


data = [{"key1": {'cheie': 'valoare'}}, {"key2": 2}]
serialized = custom_serialize(data)
print("Serialized:", serialized)

deserialized = custom_deserialize(serialized)
print("Deserialized:", deserialized)
