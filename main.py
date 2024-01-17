import csv
import random
from datetime import datetime, timedelta, time


def read_teams_from_csv(filename):
    teams = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            teams.append(row[0])
    return teams


def generate_dates(start_date, num_games, num_teams):
    dates = []
    date = datetime.strptime(start_date, "%m/%d/%Y")
    interval = 7  # Assuming one game per week

    # Calculate the total number of game dates needed
    total_game_dates = num_games * num_teams // 2

    for _ in range(total_game_dates):
        dates.append(date.strftime("%m/%d/%Y"))
        date += timedelta(days=interval)
    return dates


def generate_schedule(teams, dates, num_games_per_team):
    schedule = []
    team_game_counts = {team: 0 for team in teams}
    num_teams = len(teams)
    games_per_date = num_teams // 2 if num_teams % 2 == 0 else (num_teams // 2) + 1

    for date in dates:
        games_scheduled = 0
        day_teams = list(teams)  # Copy of the teams list for this date

        while day_teams and games_scheduled < games_per_date:
            random.shuffle(day_teams)
            home_team = day_teams.pop()
            away_team = day_teams.pop() if day_teams else "Bye"

            if team_game_counts[home_team] < num_games_per_team and (
                    away_team == "Bye" or team_game_counts[away_team] < num_games_per_team):
                schedule.append({'date': date, 'home_team': home_team, 'away_team': away_team})
                team_game_counts[home_team] += 1
                if away_team != "Bye":
                    team_game_counts[away_team] += 1

            games_scheduled += 1

            if away_team == "Bye":
                break  # Assign bye to the last game slot

    return schedule


def generate_game_times(schedule):
    game_start_time_strings = ['7:15pm', '8:05pm', '8:55pm']
    game_start_times = [datetime.strptime(time_str, '%I:%M%p').time() for time_str in game_start_time_strings]

    # Group games by date and separate byes
    games_by_date = {}
    byes_by_date = {}
    for game in schedule:
        date = game['date']
        if game['away_team'] == "Bye":
            if date not in byes_by_date:
                byes_by_date[date] = []
            byes_by_date[date].append(game)
        else:
            if date not in games_by_date:
                games_by_date[date] = []
            games_by_date[date].append(game)

    # Assign start times for each date and append byes at the end
    for date in games_by_date:
        times = game_start_times.copy()
        random.shuffle(times)
        for game in games_by_date[date]:
            game['game_start_time'] = times.pop(
                0) if times else time.min  # Assign time, or mark as TBD if no more times are available

        if date in byes_by_date:
            games_by_date[date].extend(byes_by_date[date])  # Add byes at the end of the day

    # Combine and flatten the schedule
    combined_schedule = [game for date in games_by_date for game in games_by_date[date]]
    return combined_schedule


def main():
    teams = read_teams_from_csv('teams.csv')  # Load teams from CSV file

    # User input for number of games and starting date
    num_games = int(input("Enter the number of games each team will play: "))
    start_date = input("Enter the start date (MM/DD/YYYY): ")

    dates = generate_dates(start_date, num_games, len(teams))
    initial_schedule = generate_schedule(teams, dates, num_games)
    final_schedule = generate_game_times(initial_schedule)

    # Sort the schedule by date and start time
    final_schedule_sorted = sorted(final_schedule,
                                   key=lambda x: (datetime.strptime(x['date'], "%m/%d/%Y"),
                                                  x.get('game_start_time', time.max)))

    print("Game Schedule:")
    last_date = ""
    for game in final_schedule_sorted:
        if game['date'] != last_date:
            if last_date:
                print("\n")
            last_date = game['date']

        game_time = game.get('game_start_time')
        game_time_str = game_time.strftime('%I:%M%p') if game_time and game_time != time.max else 'Bye'

        if game['away_team'] != "Bye":
            print(f"{game['date']} - {game['home_team']} vs {game['away_team']} - Start time: {game_time_str}")
        else:
            print(f"{game['date']} - {game['home_team']} has a bye.")


if __name__ == "__main__":
    main()
