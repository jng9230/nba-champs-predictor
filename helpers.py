def get_end_year(year):
    end_year = int(str(year)[-2:]) + 1
    if year == 1999:
        end_year = "00"
    elif end_year < 10:
        end_year = "0" + str(end_year)
    else:
        end_year = str(end_year)
    return end_year