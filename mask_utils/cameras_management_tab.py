
def create_default_region(w_in, h_in, extra_pixels_in):
    result = [0 + extra_pixels_in, 0 + extra_pixels_in, w_in - extra_pixels_in, 0 + extra_pixels_in,
              w_in - extra_pixels_in,
              h_in - extra_pixels_in, 0 + extra_pixels_in, h_in - extra_pixels_in]
    return result


def create_default_counting_line(w_in, h_in, extra_pixels_in):
    counting_line = [0 + extra_pixels_in, int(h_in / 2), w_in - extra_pixels_in, int(h_in / 2)]
    direction_point = [int(w_in / 2), int(h_in / 2) + 50]
    result = [
        {
            "id": "Counting-1",
            "points": counting_line,
            "direction_point": direction_point
        }
    ]
    return result
