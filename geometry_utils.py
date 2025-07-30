import numpy as np


# Compute the random walk per time-step:
def get_intersect(seg1_start, seg1_end, seg2_start, seg2_end):
    if abs(seg1_end[0] - seg1_start[0]) < 1e-9 and abs(seg2_start[0] - seg2_end[0]) < 1e-9:
        return None
    elif abs(seg1_end[0] - seg1_start[0]) < 1e-9:
        m2 = (seg2_end[1] - seg2_start[1]) / (seg2_end[0] - seg2_start[0])
        b2 = seg2_start[1] - m2 * seg2_start[0]
        point = [seg1_end[0], m2 * seg1_end[0] + b2]
    elif abs(seg2_start[0] - seg2_end[0]) < 1e-9:
        m1 = (seg1_end[1] - seg1_start[1]) / (seg1_end[0] - seg1_start[0])
        b1 = seg1_end[1] - m1 * seg1_end[0]
        point = [seg2_start[0], m1 * seg2_start[0] + b1]
    else:
        m2 = (seg2_end[1] - seg2_start[1]) / (seg2_end[0] - seg2_start[0])
        b2 = seg2_start[1] - m2 * seg2_start[0]
        m1 = (seg1_end[1] - seg1_start[1]) / (seg1_end[0] - seg1_start[0])
        b1 = seg1_end[1] - m1 * seg1_end[0]
        if abs(m1 - m2) < 1e-9:
            return None
        else:
            point_x = (b2 - b1) / (m1 - m2)
            point_y = m1 * point_x + b1
            point = [point_x, point_y]


    if (
            min(seg1_start[0], seg1_end[0]) - 1e-9 <= point[0] <= max(seg1_start[0], seg1_end[0]) + 1e-9
            and min(seg1_start[1], seg1_end[1]) - 1e-9 <= point[1] <= max(seg1_start[1], seg1_end[1]) + 1e-9
            and min(seg2_start[0], seg2_end[0]) - 1e-9 <= point[0] <= max(seg2_start[0], seg2_end[0]) + 1e-9
            and min(seg2_start[1], seg2_end[1]) - 1e-9 <= point[1] <= max(seg2_start[1], seg2_end[1]) + 1e-9
    ):
        return point
    else:
        return []
    

def make_vector_from_tet(alpha: float) -> np.ndarray :
    """
    Makes a unit 2D vector from a given angle alpha (in Radians).
    """
    return np.array(
                    [np.cos(alpha), 
                     np.sin(alpha)]
                    )


def rotate_2d_vector(alpha: float,
                        d: np.ndarray) -> np.ndarray :
    """
    Rotates a 2d vector CCW with angle alpha (in Radians).
    """
    if len(d) != 2:
        msg = "Not a 2D vector."
        raise ValueError(msg)
    
    return np.array(
                    [d[0]*np.cos(alpha) - d[1]*np.sin(alpha), 
                        d[0]*np.sin(alpha) + d[1]*np.cos(alpha)]
                    )