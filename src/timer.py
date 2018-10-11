import re


minutes_total = 0

while True:
    inp = input("Skriv inn tid på formen tt[:.,]mm  ")
    if not inp:
        break

    in_parts = re.split("[:.,]", inp)
    hours = int(in_parts[0])
    minutes = int(in_parts[1]) if len(in_parts) > 1 else 0

    minutes_total += hours * 60 + minutes


print("\nTotalt: {}:{:02}".format(minutes_total // 60, minutes_total % 60))
