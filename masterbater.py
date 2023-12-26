import requests
import json
import platform
import math
from datetime import datetime
from random import randint
from dotenv import load_dotenv
import os

load_dotenv()
base_url="https://api.betika.com/"

l_url="v1/login"
w_url="v1/withdraw"
balance=0
profile_id=""
token=""
print(os.path.join(base_url,l_url))
s=requests.session()
bets=[]
betslip=[]
def get_games_frome_file(filename):
   try:
      with open(filename,"r") as file:
         teams=file.readlines()
         games=[]
         for team in teams:
            try:
               home_game,away_game,pick=team.replace("\n","").split(",")
               game={"teams":{"home_game":home_game.strip(),"away_game":away_game.strip()},"pick":pick}
               if game not in games:
                  games.append(game)
            except Exception as e:
               pass
         file.close()
      return games
   except Exception as e:
      return None
def login(url,data):
    global base_url,balance,profile_id
    headers={"Content-Type":"application/json; charset=utf-8","Origin":"https://www.betika.com",
             "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",   
             }
    if os.getenv("TOKEN") is not None:
       profile_id=os.getenv("PROFILE")

       print("Logged in Profile: ",profile_id)
       return os.getenv("TOKEN")
    req=requests.post(url=url,data=json.dumps(data),headers=headers)
    try:
     info=req.json()
     if info['data']['user'] is not None:
        print("logged in Successfully")
        balance=math.floor(float(info['data']['user']['balance']))
        profile_id=info['data']['user']['id'] 
        with open(".env","w") as f2:
           f2.write(f"TOKEN={info['token']}\n")
           f2.write(f"PROFILE={profile_id}\n")
           f2.write(f"PHONE={data['mobile']}\n")
           f2.write(f"PASSWORD={data['password']}")
           f2.close()
        return info['token']
    except Exception as e:
       print(info['error']['message'])
       return False
def withdraw(url,data,token):
   try:
      headers={"Content-Type":"application/json; charset=utf-8","Origin":"https://www.betika.com",
             "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
             }
      req=requests.post(url=url,data=json.dumps(data),json=json.dumps(data),headers=headers)
      info=req.json()
      if info['success'] is not None:
         print(info['success']['message'], end="\n\n")
   except Exception as e:
      if str(e).__contains__("session"):
         print("Session Expired Login Required")
         menu()
      else:
         print("failed to withdraw "+str(e))

def input_game():
   games=[]
   try:
       number_of_games=int(input("How many games do you want to place? "))
       for number in range(number_of_games):
          print(f"Game number {number +1 }")
          home_game=input("Enter Team 1:  ")
          away_game=input("Enter Team 2 : ")
          pick =input("Your Pick Home (1) , Draw (2) Away (3): ")
          game={"teams":{"home_game":home_game.strip(),"away_game":away_game.strip()},"pick":pick}
          if game not in games:
             games.append(game)
       return games
   except Exception as e: 
      print(e)
      return None
def fetch_games():
   global betslip,total_odds

   games_to_bet=get_games_frome_file("my_games.txt")
   if games_to_bet is not None:
      LIMIT=2000
      url2=f"https://api.betika.com/v1/uo/matches?page=1&limit={LIMIT}&tab=upcoming&sub_type_id=1,186,340&sport_id=14&tag_id=&sort_id=1&period_id=9&esports=false"
      req=requests.get(url=url2)
      games=req.json()['data']
      total_odds=1
      betslip=[]
      file= open("matches.csv","w") 
      file.write("Home Team, Away Team, Home odd, Away odd, Draw,Competition Name,Category,start time ,game id,match id, parent match id\n")
      # file2=open("my_games.txt","w")
      for game in games:
        game_id=game['game_id']
        match_id=game['match_id']
        home_team=game['home_team']
        away_team=game['away_team']
        home_odd=game['home_odd']
        draw=game['neutral_odd']
        away_odd=game['away_odd']
        sport_id=game['sport_id']
        competition_name=game['competition_name']
        parent_match_id=game['parent_match_id']
        start_time=game['start_time']
        category=game['category']
        date=start_time.split(" ")[0]
        if  float(home_odd) > 2  and float(away_odd) > 2  and(float(date.split("-")[1].strip()) ==12 and float(date.split("-")[2].strip()) <=31 )  :
            # pick2 =randint(1,3)
            # print(home_odd,away_odd)
            # file2.write(f"{home_team},{away_team},{pick2}\n")
            pass
        file.write(f"{home_team},{away_team},{home_odd},{away_odd},{draw},{competition_name.replace(',','')},{category.replace(',','')},{start_time},{game_id},{match_id},{parent_match_id}\n")
        for team in games_to_bet: 
         if home_team  in team['teams'].values() and away_team in team['teams'].values():
           pick=team['pick']
           odd=1
           team1=""
           if pick =="1" :
              odd=home_odd
              team1=home_team
           elif pick =="2":
              odd=draw
              team1="draw"
           else:
              odd=away_odd
              team1=away_team
            
           bet={
            "sub_type_id": "1",
            "bet_pick": f"{team1}",
            "odd_value": f"{odd}",
            "outcome_id": f"{pick}",
            "sport_id": f"{sport_id}",
            "special_bet_value": "",
            "parent_match_id": f"{parent_match_id}",
            "bet_type": 7
               }
           betslip.append(bet)
           total_odds *=float(odd)
           break
      file.close()
      # file2.close()
      #   print(home_team,away_team,home_odd,away_odd,game_id,match_id)
     
def place_bet(url,betslip,stake,token,total_odds=1):
   global profile_id
   if len(betslip) > 0:
      headers={"Content-Type":"application/json; charset=utf-8","Origin":"https://www.betika.com",
             "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
             }
      payload2={
    "profile_id": f"{profile_id}",
    "stake": f"{stake}",
    "total_odd": f"{total_odds}",
    "src": "MOBILE_WEB",
     "betslip": betslip,
    "token": f"{token}",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "app_version": "6.0.0",
    "affiliate": None,
    "promo_id": None,
    "fbpid": False,
    "is_freebet": False
}
      print(payload2)
      req=requests.post(url,json=json.dumps(payload2), data=json.dumps(payload2),headers=headers)
      response=req.json()
   
      if req.status_code == 200:
         if response['message'] is not None:
           print(response['message'])
      else:
         print(response)
def bet_history(data):
   url_bet_history="https://api.betika.com/v1/uo/bethistory"
   bet_history_payload={
      "page": "1",
      "limit": "1000",
      "period": "YEAR",
      "product": "NORMAL",
      "profile_id": f"{data['profile']}",
      "token": f"{data['token']}"
   }
   req=requests.post(url_bet_history,json=json.dumps(bet_history_payload), data=json.dumps(bet_history_payload))
   bets=req.json()['bets']
   file=open("history.csv","w")
   file.write("Bet id, date,total odds,message,Amount,Possible win,Bet type,Status\n")
   for n, bet in enumerate(bets):
      bet_id=bet['bet_id']
      date_created=bet['created']
      total_odds=bet['total_odd']
      bet_message=bet['bet_message']
      bet_amount=bet['bet_amount']
      possible_win=bet['possible_win']
      bet_type=bet['bet_type']
      category=bet['category']
      taxable_amount=bet['taxable_amount']
      tax_amount=bet['tax_amount']
      bet_status_text=bet['betStatus']['text']
      file.write(f"{bet_id}, {date_created},{total_odds},{bet_message},{taxable_amount},{possible_win},{bet_type},{bet_status_text}")
      if n < len(bets)-1:
         file.write("\n")
   file.close()
   print(f"Bet History retrived {os.path.join(os.getcwd(),file.name)}")

def menu():
   load_dotenv()
   global token,balance,betslip,profile_id
   profile_id=os.getenv("PROFILE")
   token=os.getenv("TOKEN")
   print("\n1.Login\n2.Bet\n3.Withdraw \n4.Bet history")
   option=input("Your choice: ")
   if option=="1":
      with open(".env","w") as f:
         f.close()
      number=input("Phone Number: ")
      password=input("Password: ")
      token=login(os.path.join(base_url,l_url),data={"mobile":f"{number}","password":f"{password}","remember":True,"src":"MOBILE_WEB"})
   
   elif option =="2":
      fetch_games()
      profile_id=os.getenv("PROFILE")
      token=os.getenv("TOKEN")
      if token is not None:
         print(len(betslip))
         betslip=[bet for n,bet in enumerate(betslip) if n %2 ==0 ]
         print(len(betslip))
         stake=input("Enter bet amount: ")
         url3="https://api.betika.com/v2/bet"
         
         place_bet(url3,betslip,stake,token,total_odds)
        
      else:
         print("Session Expired login required")
        
   elif option =="3":
      try:
         amount=input("Enter Amount: ")
         amount=float(amount)
         data={"amount":str(balance),"app_name":"MOBILE_WEB","token":token}
         if balance > 50 :
            withdraw(os.path.join(base_url,w_url),data)
           
         else:
            print(f"{balance} is less than 50 minimum withdrawal limit")
      except Exception as e:
         print("Invalid amount")
         
   elif option =="4":
      data={"profile":profile_id,"token":token}
      bet_history(data)
   else:
      print("invalid option\nSelect again")
   menu()
if __name__ =="__main__":
      menu()
    
        