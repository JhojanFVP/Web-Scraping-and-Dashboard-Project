from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd


driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))


def scrape_batting_average(driver):
    driver.get("https://www.baseball-almanac.com/recbooks/rb_bavg1.shtml")
    tr_header = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/table/tbody/tr[10]")
    rows = tr_header.find_elements(By.XPATH, ".//following-sibling::tr")
    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) == 6:
            league = cells[1].text.strip()
            name = cells[2].text.strip()
            team = cells[3].text.strip()
            avg = cells[4].text.strip()
            year = cells[5].text.strip()
        elif len(cells) == 5:
            league = cells[0].text.strip()
            name = cells[1].text.strip()
            team = cells[2].text.strip()
            avg = cells[3].text.strip()
            year = cells[4].text.strip()
        else:
            continue
        data.append({
            "League": league,
            "Name": name,
            "Team": team,
            "Batting Average": avg,
            "Year": year
        })
    
    df = pd.DataFrame(data)
    result_df = df.drop_duplicates(subset=["Name","Batting Average"])
    result_df = result_df.iloc[0:23].reset_index(drop=True)
    return result_df


def career_home_run(driver):
    driver.get("https://www.baseball-almanac.com/recbooks/rb_hr1.shtml")
    tr_header = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/table/tbody/tr[2]")
    rows = tr_header.find_elements(By.XPATH, ".//following-sibling::tr")
    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) == 6:
            name_cell = cells[2]
            name_a = name_cell.find_elements(By.TAG_NAME, "a")
            if name_a:
                name = name_a[0].text.strip()
            else:
                name = name_cell.text.strip()
            home_run_hit_cell = cells[5]
            home_run_hit_a = home_run_hit_cell.find_elements(By.TAG_NAME, "a")
            if home_run_hit_a:
                home_run_hit = home_run_hit_a[0].text.strip()
            else:
                home_run_hit = home_run_hit_cell.text.strip()
        elif len(cells) == 5:
            name_cell = cells[1]
            name_a = name_cell.find_elements(By.TAG_NAME, "a")
            if name_a:
                name = name_a[0].text.strip()
            else:
                name = name_cell.text.strip()
            home_run_hit_cell = cells[4]
            home_run_hit_a = home_run_hit_cell.find_elements(By.TAG_NAME, "a")
            if home_run_hit_a:
                home_run_hit = home_run_hit_a[0].text.strip()
            else:
                home_run_hit = home_run_hit_cell.text.strip()
        elif len(cells) == 4:
            name_cell = cells[0]
            name_a = name_cell.find_elements(By.TAG_NAME, "a")
            if name_a:
                name = name_a[0].text.strip()
            else:
                name = name_cell.text.strip()
            home_run_hit_cell = cells[3]
            home_run_hit_a = home_run_hit_cell.find_elements(By.TAG_NAME, "a")
            if home_run_hit_a:
                home_run_hit = home_run_hit_a[0].text.strip()
            else:
                home_run_hit = home_run_hit_cell.text.strip()
        else:
            continue
        data.append({
            "Name": name,
            "Career Home Runs": home_run_hit
        })
    
    df = pd.DataFrame(data)
    df = df[~df['Name'].isin(["AL", "NL", "LG", "ML"])]
    result_df = df.drop_duplicates(subset=["Name"])
    result_df = result_df.iloc[:-5].reset_index(drop=True)
    return result_df


def career_strikeout_for_pitchers(driver):
    driver.get("https://www.baseball-almanac.com/recbooks/rb_strik.shtml")
    tr_header = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/table/tbody/tr[2]")
    rows = tr_header.find_elements(By.XPATH, ".//following-sibling::tr")
    data = []
    for row in rows:
        if "banner" in row.get_attribute("class"):
            break
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) == 6:
            league = cells[1].text.strip()
            name_cell = cells[2]
            name_a = name_cell.find_elements(By.TAG_NAME, "a")
            if name_a:
                name = name_a[0].text.strip()
            else:
                name = name_cell.text.strip()
            strikeout_cell = cells[5].text.strip()
        elif len(cells) == 5:
            league = cells[0].text.strip()
            name_cell = cells[1]
            name_a = name_cell.find_elements(By.TAG_NAME, "a")
            if name_a:
                name = name_a[0].text.strip()
            else:
                name = name_cell.text.strip()
            strikeout_cell = cells[4].text.strip()
        else:
            continue
        data.append({
            "League": league,
            "Name": name,
            "Career Strikeouts": strikeout_cell
        })
    
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["League", "Name"])
    result_df = df.iloc[0:8].reset_index(drop=True)
    return result_df
    

try:
    # Batting Average Records
    batting_df = scrape_batting_average(driver)
    # print(batting_df)
    batting_df['Batting Average'] = batting_df['Batting Average'].astype(float)
    batting_df['Year'] = pd.to_numeric(batting_df['Year'], errors='coerce')
    batting_df.to_csv("batting_avg.csv")
    print("Data saved to batting_avg.csv")
    
    # Career Home Runs Records
    home_run_df = career_home_run(driver)
    # print(home_run_df)
    home_run_df['Career Home Runs'] = home_run_df['Career Home Runs'].astype(int)
    home_run_df.to_csv("home_runs.csv")
    print("Data saved to career_home_runs.csv")
    
    # Career Strikeout Records for Pitchers
    strikeout_df = career_strikeout_for_pitchers(driver)
    # print(strikeout_df)
    strikeout_df['Career Strikeouts'] = pd.to_numeric(strikeout_df['Career Strikeouts'].str.replace(",", ""), errors='coerce')
    strikeout_df.to_csv("career_strikeouts.csv")
    print("Data saved to career_strikeouts.csv")
    
except Exception as e:
    print(f"An error occurred: {type(e).__name__} {e}")
finally:
    driver.quit()