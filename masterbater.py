import requests
import json
import platform
import math
from datetime import datetime
from random import randint
import random
from dotenv import load_dotenv
import os

load_dotenv()

base_url = "https://api.betika.com/"
l_url = "v1/login"
w_url = "v1/withdraw"
balance = 0
profile_id = ""
token = ""
print(os.path.join(base_url, l_url))
s = requests.session()
bets = []
betslip = []
slip = []
total_odds = 1.0


def get_games_from_file(filename):
    try:
        with open(filename, "r") as file:
            teams = file.readlines()
            games = []
            for team in teams:
                try:
                    home_team, away_team, home_odd, away_odd, sport_id, parent_match_id, start_time = team.replace(
                        "\n", "").split(",")
                    game = (home_team, away_team, home_odd, away_odd, sport_id, parent_match_id, start_time)
                    if game not in games:
                        games.append(game)
                except Exception as e:
                    pass
            file.close()
        return games
    except Exception as e:
        return None


def login(url, data):
    global base_url, balance, profile_id
    headers = {"Content-Type": "application/json; charset=utf-8", "Origin": "https://www.betika.com",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/115.0.0.0 Safari/537.36",
               }
    if os.getenv("TOKEN") is not None:
        profile_id = os.getenv("PROFILE")
        print(os.getenv("TOKEN"))

        print("Logged in Profile: ", profile_id)
        return os.getenv("TOKEN")
    req = requests.post(url=url, data=json.dumps(data), headers=headers)
    try:
        info = req.json()
        if info['data']['user'] is not None:
            print("logged in Successfully")
            balance = math.floor(float(info['data']['user']['balance']))
            profile_id = info['data']['user']['id']
            with open(".env", "w") as f2:
                f2.write(f"TOKEN={info['token']}\n")
                f2.write(f"PROFILE={profile_id}\n")
                f2.write(f"BALANCE={balance}\n")
                f2.write(f"PHONE={data['mobile']}\n")
                f2.write(f"PASSWORD={data['password']}")
                f2.close()
            return info['token']
    except Exception as e:
        print(info['error']['message'])
        return False


def withdraw(url, data, token):
    try:
        headers = {"Content-Type": "application/json; charset=utf-8", "Origin": "https://www.betika.com",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/115.0.0.0 Safari/537.36"
                   }
        req = requests.post(url=url, data=json.dumps(data), json=json.dumps(data), headers=headers)
        info = req.json()
        if info['success'] is not None:
            print(info['success']['message'], end="\n\n")
    except Exception as e:
        if str(e).__contains__("session"):
            print("Session Expired Login Required")
            menu()
        else:
            print("failed to withdraw " + str(e))


def input_game():
    games = []
    try:
        number_of_games = int(input("How many games do you want to place? "))
        for number in range(number_of_games):
            print(f"Game number {number + 1}")
            home_game = input("Enter Team 1:  ")
            away_game = input("Enter Team 2 : ")
            pick = input("Your Pick Home (1) , Draw (2) Away (3): ")
            game = {"teams": {"home_game": home_game.strip(), "away_game": away_game.strip()}, "pick": pick}
            if game not in games:
                games.append(game)
        return games
    except Exception as e:
        print(e)
        return None


def processTeams(n_combination=None):
    global betslip, total_odds
    global total_odds
    load_betslip()
    if n_combination is None:
        betslip_length = int(input("How many team combination do you want? "))
    else:
        betslip_length = n_combination
    slip = []

    selected_teams = []
    if len(betslip) > betslip_length:
        for i in range(betslip_length):
            random_position = randint(0, len(betslip) - 1)
            slip.append(betslip[random_position])
            total_odds *= float(betslip[random_position]['odd_value'])
            selected_teams.append(teams[random_position])
        return slip, selected_teams, total_odds
    else:
        print("No Enough teams to combine")
        return [], [], 1.0


def load_betslip():
    global betslip
    global total_odds

    file = open("choices.json", "r")
    my_betslips = json.loads(file.read())

    chosen_list = []
    over_s = []
    chosen_parent_ids = []

   
    # choose over 0.5 70%

    while True:
        random_id = randint(0, len(my_betslips) - 1)
        random_slip = my_betslips[random_id]
        if random_slip[0]['parent_match_id'] not in chosen_parent_ids and len(over_s) <= int(len(my_betslips) * 0.9):
            chosen_slip = [rando for rando in random_slip if rando['bet_pick'] == 'over 0.5']
            if len(chosen_slip) > 0:
                chosen_parent_ids.append(chosen_slip[0]['parent_match_id'])
                over_s.append(chosen_slip[0])
                betslip.append(chosen_slip[0])
                print("BETSLIP INSIDE OVER  ",len(betslip))
                total_odds *= float(chosen_slip[0]['odd_value'])
            else:
                over_s.append({})
        elif len(over_s) >= int(len(my_betslips) * 0.9):
            break

    for slip in my_betslips:
        if slip[0]['parent_match_id'] not in chosen_parent_ids and len(slip) > 0:
            remaining_options = [rando for rando in slip if rando['bet_pick'] != 'over 0.5']
            random_index = randint(0, len(remaining_options) - 1)
            chosen_parent_ids.append(remaining_options[random_index]['parent_match_id'])
            betslip.append(remaining_options[random_index])
            total_odds *= float(remaining_options[random_index]['odd_value'])
        elif len(chosen_list) == len(my_betslips):
            break

    file=open("betslip.json","w")
    file.write(json.dumps(betslip))
    file.close()
def fetch_games(s_time=0):
    global betslip
    global total_odds
    betslip=[]
    total_odds= 1.0
    LIMIT = 200
    end_H = input("Enter End Range kick off hour:  ")


    url2 = f"https://api.betika.com/v1/uo/matches?page=1&limit={LIMIT}&tab=&sub_type_id=1,186,340&" \
           f"sport_id=14&tag_id=&sort_id=1&period_id=-1&esports=false"
    req = requests.get(url=url2)
    games = req.json()['data']
    my_betslips = []
    file2 = open("choices.json", "w")
  
    for game in games:

        game_id = game['game_id']
        match_id = game['match_id']
        home_team = game['home_team']
        away_team = game['away_team']
        home_odd = game['home_odd']
        draw = game['neutral_odd']
        away_odd = game['away_odd']
        sport_id = game['sport_id']
        competition_name = game['competition_name']
        parent_match_id = game['parent_match_id']
        start_time = game['start_time']
        category = game['category']
        date = start_time.split(" ")[0]
        time = start_time.split(" ")[1]
        hour = time.split(":")[0]
        odds = game['odds']
 
        if ((float(home_odd) < 1.89 and float(home_odd) > 1.2 and float(away_odd) > 3.0) or (
                float(away_odd) < 1.95 and float(away_odd) > 1.2 and float(home_odd) > 3.0)) and (
                float(date.split("-")[2].strip()) <= float(datetime.now().date().day)) and (
                float(hour) <= float(end_H) and float(hour) >= s_time):
            
            print(f"++++++++++++++++{home_team} VS {away_team}=================")
           
            head_odd=random.uniform(1.3,1.7)
            print(head_odd,"HEAD HONME" ,min(home_odd,away_odd))
            if abs(float(home_odd) - float(away_odd)) > 4.0 and min(float(home_odd),float(away_odd) < head_odd):
         
                pick_odd = home_odd if home_odd < away_odd else away_odd
                bet = {
                    "sub_type_id": odds[0]['sub_type_id'],
                    "bet_pick": home_team if home_odd < away_odd else away_team,
                    "odd_value": pick_odd,
                    "outcome_id": "1" if home_odd < away_odd else "3",
                    "sport_id": f"{sport_id}",
                    "special_bet_value": "",
                    "parent_match_id": f"{parent_match_id}",
                    "bet_type": "7"
                }
                betslip.append(bet)
                total_odds *= float(pick_odd)
            else:
                add_both_teams_to_score= True if abs(float(home_odd)-float(away_odd)) <= 3.5  else False
                more_odds = get_more_odds(parent_match_id)
                slips = process_odds(more_odds, sport_id, parent_match_id,add_both_teams=add_both_teams_to_score)

                if len(slips) > 0:
                    my_betslips.append(slips)

            print("Date:", float(date.split("-")[2].strip()))
    if len(my_betslips) > 1:
        print(f"{len(my_betslips)} betslips Loaded to a file {file2.name}")
    file2.write(json.dumps(my_betslips))

   
def process_odds(oddList, sport_id, parent_match_id,add_both_teams=False):
    slips = []
    for data in oddList:
        if data['name'] == "1X2" or data['name'] == "TOTAL" or data['name'] == "DOUBLE CHANCE" or str(data['name']).__contains__("BOTH TEAMS TO SCORE (GG/NG)"):
        
            if data['name'] == "TOTAL":
                odds = data['odds']
                for odd in odds:
                    if odd['odd_key'] == "over 0.5" or odd['odd_key'] == "over 1.5":
                        bet = {
                            "sub_type_id": data['sub_type_id'],
                            "bet_pick": odd['odd_key'],
                            "odd_value": odd['odd_value'],
                            "outcome_id": odd['outcome_id'],
                            "sport_id": f"{sport_id}",
                            "special_bet_value": f"total={odd['odd_key'].split()[1]}",
                            "parent_match_id": f"{parent_match_id}",
                            "bet_type": 7
                        }
                        slips.append(bet)
            elif data['name'] == "DOUBLE CHANCE":
                odds = data['odds']
                home_draw = odds[0]['odd_value']
                away_draw = odds[1]['odd_value']
                home_away= odds[2]['odd_value']
                for odd in odds:
                    if odd['display'] == "1/X" and float(home_draw) < (float(away_draw) + 0.05):
                        bet = {
                            "sub_type_id": data['sub_type_id'],
                            "bet_pick": odd['odd_key'],
                            "odd_value": odd['odd_value'],
                            "outcome_id": odd['outcome_id'],
                            "sport_id": f"{sport_id}",
                            "special_bet_value": "",
                            "parent_match_id": f"{parent_match_id}",
                            "bet_type": 7
                        }
                        slips.append(bet)
                    elif odd['display'] == "X/2" and float(home_draw) > (float(away_draw) + 0.02):
                        bet = {
                            "sub_type_id": data['sub_type_id'],
                            "bet_pick": odd['odd_key'],
                            "odd_value": odd['odd_value'],
                            "outcome_id": odd['outcome_id'],
                            "sport_id": f"{sport_id}",
                            "special_bet_value": odd['special_bet_value'],
                            "parent_match_id": f"{parent_match_id}",
                            "bet_type": 7
                        }
                        slips.append(bet)
            elif add_both_teams and str(data['name']).__contains__("BOTH TEAMS TO SCORE"):
                odds = data['odds']
                yes_odd = [odd['odd_value'] for odd in odds if odd['odd_key']=="yes"][0]
                no_odd = [odd['odd_value'] for odd in odds if odd['odd_key']=="no"][0]

                for odd in odds:
                  if float(yes_odd)  < (float(no_odd) - 0.2):
                        bet = {
                              "sub_type_id": data['sub_type_id'],
                              "bet_pick": odd['odd_key'],
                              "odd_value": odd['odd_value'],
                              "outcome_id":  odd['outcome_id'] ,
                              "sport_id": f"{sport_id}",
                              "special_bet_value": odd['special_bet_value'],
                              "parent_match_id": f"{parent_match_id}",
                              "bet_type": 7
                           }
                        slips.append(bet)
                        break
                  elif float(no_odd) < 2.0:
                        bet = {
                              "sub_type_id": data['sub_type_id'],
                              "bet_pick": odd['odd_key'],
                              "odd_value": odd['odd_value'],
                              "outcome_id":  odd['outcome_id'] ,
                              "sport_id": f"{sport_id}",
                              "special_bet_value": odd['special_bet_value'],
                              "parent_match_id": f"{parent_match_id}",
                              "bet_type": 7
                           }
                        slips.append(bet)
                        break
                     
        if len(slips) == 5:
            break
    return slips

def get_more_odds(parent_match_id):
    try:
        url = f"https://api.betika.com/v1/uo/match?parent_match_id={parent_match_id}"
        req = requests.get(url)
        data = req.json()['data']

        return data

    except Exception as e:
        pass


def place_bet(url, betslip, stake, token, total_odds=1):
    global profile_id
    try:
      if len(betslip) > 0:
         headers = {"Content-Type": "application/json; charset=utf-8", "Origin": "https://www.betika.com",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/115.0.0.0 Safari/537.36"
                     }
         progress=True
         print("SLIP UNTRIMMED SIZE",len(betslip) , " ODD VALUE  ",total_odds)
         if len(betslip)  > 40:
              betslip = random.sample(betslip, 30)
              total_odd_values = sum(float(bet['odd_value']) for bet in betslip)
              total_odds=total_odd_values

              print("SLIP TRIMMED SIZE",len(betslip) , "TRIMMED ODD VALUE  ",total_odds)
              ask=input("Do you want to conitue ?? (yes/no)")
              if ask.lower().strip()== "no":
                  progress=False
         payload2 = {
               "profile_id": f"{profile_id}",
               "stake": f"{stake}",
               "total_odd": f"{total_odds}",
               "src": "MOBILE_WEB",
               "betslip": betslip,
               "token": f"{token}",
               "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/115.0.0.0 Safari/537.36"
         }
         if progress:
            req = requests.post(url=url, json=payload2, headers=headers)
            info = req.json()
            print(info)
            if info['success'] is not None:
                  print("Betslip Placed Successfully")
            return
         print("Bet cancelled")
    except Exception as e:
        print(e)
def fetch_betDetails(data):
    try:
      my_bet_url="https://api.betika.com/v1/mybet"
      payload={
         "page": "1",
         "limit": "20",
         "profile_id": data['profile_id'],
         "short_bet_id": data['short_bet_id'],
         "token": data['token'],
         "category": "normal_bet"
      }

      response=requests.post(my_bet_url,json=payload,headers={"Content-type":"application/json; charset=utf-8"})

      
      data1= response.json()
      bet_list=data1['data']
      meta=data1['meta']
      final_slip={
          "meta":meta,
          "data":[]
      }
      for betslip in bet_list:
          new_slip=  {
          "odd_value":betslip['odd_value'],
          "home_team":betslip['home_team'],
          "away_team":betslip['away_team'],
          "bet_pick":betslip['bet_pick'],
          "winning_outcome":betslip['winning_outcome'],
          "final_score":betslip['ft_score'],
          "event_status":betslip['event_status'],
          "bet_status":betslip['bet_status'],
          "home_corners":betslip['home_corners'],
          "away_corners":betslip['away_corners'],
          "away_yellow_card" : betslip['away_yellow_card'],
          "home_yellow_card":betslip['home_yellow_card'],
          "home_red_card":betslip['home_red_card'],
          "away_red_card":betslip['away_red_card']
          }
          final_slip['data'].append(new_slip)
         
      file =open(f"{data['short_bet_id']}.json","w")
      file.write(json.dumps(final_slip))
      file.close()
    except Exception as e:
        print(e)
def menu():
    global balance, token, profile_id
    is_logged = False
    mobile = os.getenv("PHONE")
    password = os.getenv("PASSWORD")
    token = os.getenv("TOKEN")
    profile_id = os.getenv("PROFILE")
  
    if token is not None and profile_id is not None:
        is_logged = True
    if not is_logged:
        mobile = input("Enter mobile number: ")
        password = input("Enter password: ")
        data = {"mobile": mobile, "password": password}
        token = login(os.path.join(base_url, l_url), data)
        load_dotenv()
    if is_logged or token is not False:
        while True:
            print("\n1. Withdraw\n2. Check Balance\n3. Place Bet\n4. View Betslip\n5. Fetch Games\n6. Bet History\n7.Logout")
            choice = input("Enter choice: ")
            if choice == "1":
                amount = input("Enter amount to withdraw: ")
                mobile = input("Enter mobile number: ")
                data = {"mobile": mobile, "amount": amount}
                withdraw(os.path.join(base_url, w_url), data, token)
            elif choice == "2":
                print("Your balance is: ", os.getenv("BALANCE"))
            elif choice == "3":
                stake = input("Enter stake: ")
               #  slip, selected_teams, odds = processTeams()
                place_bet(url=os.path.join(base_url, "v2/bet"), betslip=betslip, stake=stake, token=token,
                          total_odds=total_odds)
            elif choice == "4":
                print("Betslip: ", betslip)

            elif choice == "5":
                start_time=float(input("Enter start Range kick off hour: "))
                fetch_games(start_time)
                print(total_odds)
                load_betslip()


                print(f"Total odds  ",total_odds, "  BETSLIP SIZE  ", len(betslip))
                
                print(total_odds)
            elif choice == "6":
               data={"profile_id":profile_id,"token":token}
               bet_history(data)

            elif choice == "7":
                file=open(".env","w")
                file.write("")
                file.close()
                print("Logged out ")
                load_dotenv()
                menu()
            else:
                print("Invalid choice!")
    else:
        print("Login Failed!")


def bet_history(data):
    
    url_bet_history = "https://api.betika.com/v1/uo/bethistory"
    bet_history_payload = {
        "page": "1",
        "limit": "1000",
        "period": "YEAR",
        "product": "NORMAL",
        "profile_id": data['profile_id'],
        "token": data['token']
    }

    try:
        response = requests.post(url_bet_history, json=bet_history_payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        bets = response.json().get('bets', [])

        with open("history.csv", "w") as file:
            file.write("Bet id, date,total odds,message,Amount,Possible win,Bet type,Status\n")
            for n, bet in enumerate(bets):
                bet_id = bet['bet_id']
                short_bet_id=bet['short_bet_id']
                date_created = bet['created']
                total_odds = bet['total_odd']
                bet_message = bet['bet_message']
                bet_amount = bet['bet_amount']
                possible_win = bet['possible_win']
                bet_type = bet['bet_type']
                category = bet['category']
                taxable_amount = bet['taxable_amount']
                tax_amount = bet['tax_amount']
                bet_status_text = bet['betStatus']['text']
                if bet_status_text =="Open":
                    data={
                        "token":data['token'],
                        "profile_id":data['profile_id'],
                        "short_bet_id":short_bet_id
                    }
                    fetch_betDetails(data)
                file.write(f"{bet_id},{date_created},{total_odds},{bet_message},{taxable_amount},{possible_win},{bet_type},{bet_status_text}\n")

        print(f"Bet History retrieved at: {os.path.join(os.getcwd(), 'history.csv')}")
    except requests.RequestException as e:
        print(f"Error fetching bet history: {e}")
    except KeyError as e:
        print(f"Error parsing bet data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    menu()
    
