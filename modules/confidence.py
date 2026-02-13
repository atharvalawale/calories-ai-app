def compute_confidence(detected_foods):
    if not detected_foods:
        return 0

    total = 0.0
    count = 0

    for item in detected_foods:
        conf = item.get("confidence")

        # skip invalid values
        if conf is None:
            continue

        try:
            conf = float(conf)
        except:
            continue

        total += conf
        count += 1

    if count == 0:
        return 0

    avg = total / count

    # clamp between 0–100
    if avg < 0:
        avg = 0
    if avg > 100:
        avg = 100

    return round(avg, 2)
