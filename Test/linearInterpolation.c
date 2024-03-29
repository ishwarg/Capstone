int map_range(float value, float old_min, float old_max, float new_min, float new_max) {
    // Scale the value from the old range to a value in the range [0, 1]
    float normalized_value = (value - old_min) / (old_max - old_min);
    // Map this normalized value to the new range
    int new_value = new_min + normalized_value * (new_max - new_min);
    return new_value;
}

int mapped_value = map_range(value_to_map, old_min, old_max, new_min, new_max);


