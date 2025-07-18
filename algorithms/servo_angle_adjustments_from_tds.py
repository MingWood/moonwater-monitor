def proportial_only_servo_angle_from_tds(tds_values, flow_buffer, target, current_angle, deadband=2):
    '''Use a basic algo to move servo proportionally off of error'''
    gain = .8
    max_angle = 270
    tds_value = min(tds_values) # ignores momentary TDS spikes
    flow_rate_max = max(flow_buffer)
    print('getting min tds value from buffer: {}'.format(tds_values))
    error = target - tds_value
    overshot = tds_value > target
    
    if abs(error) <= deadband:
        print('target tds {}, current tds {}, current angle maintained at {}, error in band of {}'.format(
            target, tds_value, current_angle, deadband))
        return current_angle

    if flow_rate_max == 0:
        print('target tds {}, current tds {}, current angle maintained at {}, flow rate is stationary'.format(
            target, tds_value, current_angle))
        return current_angle

    angle_change_needed_raw = gain * (abs(error) - deadband)
    angle_change_needed = angle_change_needed_raw * -1 if overshot else angle_change_needed_raw
    new_angle = max(0, current_angle + angle_change_needed)
    new_angle_up_to_limit = min(new_angle, max_angle)
    print('target tds {}, current tds {}, angle change proposed {}, new angle {}'.format(
        target, tds_value, angle_change_needed, new_angle_up_to_limit))
    return new_angle_up_to_limit
