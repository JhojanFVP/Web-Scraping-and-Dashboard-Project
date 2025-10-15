import sqlite3

def get_top_batting_averages():
    # Query and display top 10 highest batting averages.
    conn = sqlite3.connect("baseball.db")
    cursor = conn.cursor()
    
    query = """
    SELECT Name, Team, Batting_Average, Year
    FROM batting_avg
    ORDER BY Batting_Average DESC
    LIMIT 10
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\nTop 10 Highest Batting Averages:")
    print(f"{"Player":<20}{"Team":<15}{"Average":<10}{"Year":<5}")
    for row in results:
        print(f"{row[0]:<20}{row[1]:<15}{row[2]:<10}{row[3]:<5}")
    
    conn.close()


def get_top_home_runs():
    # Query and display top 10 career home run hitters
    conn = sqlite3.connect("baseball.db")
    cursor = conn.cursor()
    
    query = """
    SELECT Name, Career_Home_Runs
    FROM home_runs
    ORDER BY Career_Home_Runs DESC 
    LIMIT 10
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\nTop 10 Career Home Run Leaders:")
    print(f"{'Player':<25}{'Home Runs':<10}")
    for row in results:
        print(f"{row[0]:<25}{row[1]:<10}")
    
    conn.close()
    

def get_combined_stats(player_name):
    # Get combined stats for a specific player.
    conn = sqlite3.connect("baseball.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT b.Name,
                   b.Batting_Average,
                   h.Career_Home_Runs,
                   s.Career_Strikeouts
            FROM batting_avg b
            LEFT JOIN home_runs h ON b.Name = h.Name
            LEFT JOIN career_strikeouts s ON b.Name = s.Name
            WHERE b.Name = ?
            """,
            (player_name,)
        )
        row = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        row = None
    finally:
        conn.close()
    
    return row
    

def get_strikeouts_by_league(league):
    # Return career strikeouts for pitchers in a given league.
    conn = sqlite3.connect("baseball.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT Name, Career_Strikeouts FROM career_strikeouts WHERE League = ? ORDER BY Career_Strikeouts DESC",
            (league,)
            )
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        rows = []
    finally:
        conn.close()
    return rows


def main():
    while True:
        print("\nBaseball Statistics Query Menu:")
        print("1. Show top 10 highest batting averages")
        print("2. Show top 10 career home run hitters")
        print("3. Get combined stats for a player")
        print("4. Get career strikeouts by league")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == "1":
            get_top_batting_averages()
        elif choice == "2":
            get_top_home_runs()
        elif choice == "3":
            player = input("Enter player name (exact case): ")
            stats = get_combined_stats(player)
            if stats:
                name, avg, home_runs, strikeouts = stats
                print(f"\nStats for {name}:")
                print(f"- Batting Average: {avg}")
                print(f"- Career Home Runs: {home_runs}")
                print(f"- Career Strikeouts: {strikeouts}")
            else:
                print(f"No stats found for player: {player}")
        elif choice == "4":
            league = input("Enter league (AL, NL, or ML): ")
            results = get_strikeouts_by_league(league)
            if results:
                print(f"\nCareer Strikeouts in {league} League:")
                for name, strikeouts in results:
                    print(f"- {name}: {strikeouts} strikeouts")
            else:
                print(f"No strikeout data found for league: {league}")
        elif choice == "5":
            print("Exiting the program.")
            break
        
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    main()
                