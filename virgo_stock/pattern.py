
    
def find_pattern(df, pattern_func):
    points = []
    for i in range(len(df)):
        if pattern_func(df, i):
            points.append(i)
    return points


def drop_more_than_five_percent(df, i):
    if i + 1 >= len(df):
        return False
    prev = df.iloc[i + 1]['close']
    low = df.iloc[i]['low']
    if (prev - low) / prev > 0.05:
        return True
    return False
